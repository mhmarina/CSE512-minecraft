import time
import threading
import statistics
import uuid
from datetime import datetime
from tabulate import tabulate
from psycopg2 import connect, OperationalError, DatabaseError
from psycopg2.extras import execute_values
from dotenv import load_dotenv
from urllib.parse import urlparse, urlunparse

load_dotenv()

CRDB_CONN = "postgresql://vhonnavalli:WKk5bNvt_pvEMLEpTyZ7cQ@dd-minecraft-9734.jxf.gcp-us-west2.cockroachlabs.cloud:26257/minecraft?sslmode=require"
TEST_DB_NAME = "minecraft_test"
# number of sample rows to use in benchmarks
INSERT_BATCH = 200
CONCURRENT_WRITERS = 8
CONCURRENT_WRITES_PER_THREAD = 200

# ============================
# Utilities: connection helpers
# ============================
def _replace_db_in_conn(conn_str: str, db_name: str):
    parsed = urlparse(conn_str)
    path = f"/{db_name}"
    rebuilt = urlunparse((parsed.scheme, parsed.netloc, path, parsed.params, parsed.query, parsed.fragment))
    return rebuilt

def conn(db_name=None):
    cs = CRDB_CONN if not db_name else _replace_db_in_conn(CRDB_CONN, db_name)
    # retry loop on transient connection errors
    for _ in range(10):
        try:
            c = connect(cs)
            c.autocommit = False
            return c
        except OperationalError as e:
            print("Connection failed, retrying in 2s:", e)
            time.sleep(2)
    raise SystemExit("Unable to connect to CockroachDB after retries.")

# ============================
# Setup & teardown (test DB)
# ============================
def create_test_db():
    print(f"[SETUP] Creating test DB: {TEST_DB_NAME}")
    c = conn()
    cur = c.cursor()
    try:
        cur.execute(f"CREATE DATABASE IF NOT EXISTS {TEST_DB_NAME};")
        c.commit()
        print("[SETUP] Test DB created.")
    finally:
        cur.close()
        c.close()

def drop_test_db():
    print(f"[CLEANUP] Dropping test DB: {TEST_DB_NAME}")
    c = conn()
    cur = c.cursor()
    try:
        cur.execute(f"DROP DATABASE IF EXISTS {TEST_DB_NAME} CASCADE;")
        c.commit()
        print("[CLEANUP] Test DB dropped.")
    finally:
        cur.close()
        c.close()

def create_schema():
    print("[SETUP] Creating schema in test DB.")
    c = conn(TEST_DB_NAME)
    cur = c.cursor()
    try:
        cur.execute("""
CREATE TABLE IF NOT EXISTS servers (
    ip STRING PRIMARY KEY
);
CREATE TABLE IF NOT EXISTS server_data (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    ip STRING NOT NULL,
    ts TIMESTAMP NOT NULL,
    online BOOL NOT NULL,
    latency FLOAT8,
    curr_players INT,
    max_players INT
);
""")
        c.commit()
        print("[SETUP] Schema created.")
    finally:
        cur.close()
        c.close()

# ============================
# Metrics storage
# ============================
metrics = {
    "insert_latencies": [],
    "read_latencies": [],
    "insert_success": 0,
    "insert_fail": 0,
    "concurrent_insert_success": 0,
    "concurrent_insert_fail": 0,
    "transaction_restarts": 0,
    "recovery_times": [],
    "repeatable_read_pass": 0,
    "repeatable_read_fail": 0
}

# ============================
# Test 1: Insert latency benchmark
# ============================
def insert_latency_test(batch_size=INSERT_BATCH):
    print(f"[TEST] Insert latency (batch_size={batch_size})")
    c = conn(TEST_DB_NAME)
    cur = c.cursor()
    # sample rows
    rows = [("lat-"+str(uuid.uuid4()), datetime.utcnow(), True, float(i % 100), i % 10, 100) for i in range(batch_size)]
    sql = "INSERT INTO server_data (ip, ts, online, latency, curr_players, max_players) VALUES %s;"
    start = time.time()
    try:
        execute_values(cur, sql, rows)
        c.commit()
        dur = time.time() - start
        metrics["insert_latencies"].append(dur)
        metrics["insert_success"] += len(rows)
        print(f"[TEST] Inserted {len(rows)} rows in {dur:.3f}s -> {len(rows)/dur:.1f} rows/s")
    except Exception as e:
        c.rollback()
        metrics["insert_fail"] += len(rows)
        print("[ERROR] Insert failed:", e)
    finally:
        cur.close()
        c.close()

# ============================
# Test 2: Read latency benchmark
# ============================
def read_latency_test(limit=1000):
    print(f"[TEST] Read latency (limit={limit})")
    c = conn(TEST_DB_NAME)
    cur = c.cursor()
    start = time.time()
    try:
        cur.execute("SELECT id, ip, ts FROM server_data ORDER BY ts DESC LIMIT %s;", (limit,))
        rows = cur.fetchall()
        dur = time.time() - start
        metrics["read_latencies"].append(dur)
        print(f"[TEST] Read {len(rows)} rows in {dur:.3f}s")
    except Exception as e:
        print("[ERROR] Read failed:", e)
    finally:
        cur.close()
        c.close()

# ============================
# Test 4: Concurrency consistency (many writers)
# ============================
def writer_worker(thread_id, writes_per_thread):
    local_conn = None
    try:
        local_conn = conn(TEST_DB_NAME)
        cur = local_conn.cursor()
        for i in range(writes_per_thread):
            try:
                cur.execute("INSERT INTO server_data (ip, ts, online, latency) VALUES (%s, now(), TRUE, %s);",
                            (f"concurrent-{thread_id}", float(i % 100)))
                # commit each insert to simulate many small transactions
                local_conn.commit()
                metrics["concurrent_insert_success"] += 1
            except DatabaseError as e:
                local_conn.rollback()
                metrics["concurrent_insert_fail"] += 1
        cur.close()
    except Exception as e:
        print(f"[ERROR] Writer {thread_id} setup failed:", e)
    finally:
        if local_conn:
            local_conn.close()

def concurrency_consistency_test(num_threads=CONCURRENT_WRITERS, writes_per_thread=CONCURRENT_WRITES_PER_THREAD):
    print(f"[TEST] Concurrency consistency: {num_threads} threads x {writes_per_thread} writes")
    threads = []
    for t in range(num_threads):
        thr = threading.Thread(target=writer_worker, args=(t, writes_per_thread))
        thr.start()
        threads.append(thr)
    for thr in threads:
        thr.join()
    print("[TEST] concurrency finished. successes:", metrics["concurrent_insert_success"], "fails:", metrics["concurrent_insert_fail"])

# ============================
# Test 5: Fault tolerance simulation (client disconnects & retries)
# ============================
def fault_tolerance_simulation(simulated_fail_after=0.5, writes=100):
    """
    here we are trying to simulate intermittent client-side failure:
      - Start a connection, write some rows
      - After simulated_fail_after seconds, forcibly close the connection to emulate a client-side network failure
      - Measure how many writes were acknowledged vs failed, and measure recovery time (time until a successful write after reconnect)
    """
    print("[TEST] Fault tolerance simulation (client disconnects)")
    # Start a connection, do some initial writes
    c = conn(TEST_DB_NAME)
    cur = c.cursor()
    ack = 0
    fail = 0

    # background function to close socket (simulate crash) after delay
    def kill_conn_after_delay(connection, delay):
        time.sleep(delay)
        try:
            # best-effort: close the connection from client side
            connection.cancel()  # attempt to cancel current queries
        except Exception:
            pass
        try:
            connection.close()
            print("[SIM] Simulated client connection close.")
        except Exception:
            pass

    killer = threading.Thread(target=kill_conn_after_delay, args=(c, simulated_fail_after))
    killer.start()

    start_time = time.time()
    for i in range(writes):
        try:
            # if connection closed, will raise; catch and attempt reconnect
            cur.execute("INSERT INTO server_data (ip, ts, online, latency) VALUES (%s, now(), TRUE, %s);",
                        (f"fault-{i}", float(i % 50)))
            c.commit()
            ack += 1
        except Exception as e:
            fail += 1
            # attempt immediate reconnect and retry one time
            try:
                if c:
                    try:
                        c.close()
                    except:
                        pass
                c = conn(TEST_DB_NAME)
                cur = c.cursor()
                cur.execute("INSERT INTO server_data (ip, ts, online, latency) VALUES (%s, now(), TRUE, %s);",
                            (f"fault-retry-{i}", float(i % 50)))
                c.commit()
                ack += 1
                # record a restart
                metrics["transaction_restarts"] += 1
            except Exception as e2:
                fail += 1
        # small sleep to spread writes
        time.sleep(0.01)

    end_time = time.time()
    killer.join()
    # measure recovery time: try to write until success, measure elapsed
    rec_start = time.time()
    recovered = False
    rec_attempts = 0
    while time.time() - rec_start < 60:
        try:
            c2 = conn(TEST_DB_NAME)
            cur2 = c2.cursor()
            cur2.execute("INSERT INTO server_data (ip, ts, online, latency) VALUES (%s, now(), TRUE, 1);", ("recovery-probe",))
            c2.commit()
            rec_elapsed = time.time() - rec_start
            metrics["recovery_times"].append(rec_elapsed)
            recovered = True
            cur2.close(); c2.close()
            break
        except Exception:
            rec_attempts += 1
            time.sleep(1)
    if not recovered:
        metrics["recovery_times"].append(None)
        print("[SIM] Recovery probe FAILED to reconnect within 60s")
    else:
        print(f"[SIM] Recovered in {rec_elapsed:.3f}s after simulated client failure (attempts: {rec_attempts})")

    # close main connection if open
    try:
        cur.close()
    except:
        pass
    try:
        c.close()
    except:
        pass

    metrics["insert_success"] += ack
    metrics["insert_fail"] += fail
    print(f"[SIM] Acknowledged writes: {ack}, failed writes: {fail}")

# ============================
# Utilities: statistics helpers
# ============================
def percentile(data_list, q):
    if not data_list:
        return None
    data = sorted(data_list)
    k = (len(data)-1) * (q/100)
    f = int(k)
    c = f + 1
    if c >= len(data):
        return data[f]
    return data[f] + (data[c] - data[f]) * (k - f)

# ============================
# Run tests & produce report
# ============================
def run_all():
    try:
        create_test_db()
        create_schema()

        # warm-up insert to ensure some data exists
        insert_latency_test(batch_size=50)
        read_latency_test(limit=200)

        # concurrency
        concurrency_consistency_test(num_threads=CONCURRENT_WRITERS, writes_per_thread=CONCURRENT_WRITES_PER_THREAD)

        # larger insert benchmark
        insert_latency_test(batch_size=INSERT_BATCH)
        read_latency_test(limit=1000)

        # fault tolerance simulation: close connection mid-run and test recovery
        fault_tolerance_simulation(simulated_fail_after=0.5, writes=200)

        # final read
        read_latency_test(limit=1000)

        # build summary
        summary_rows = []

        # insert latencies statistics
        if metrics["insert_latencies"]:
            ins = metrics["insert_latencies"]
            summary_rows.append(["Insert latency (s) mean", f"{statistics.mean(ins):.4f}"])
            summary_rows.append(["Insert latency (s) p50", f"{percentile(ins, 50):.4f}"])
            summary_rows.append(["Insert latency (s) p95", f"{percentile(ins, 95):.4f}"])
            summary_rows.append(["Insert latency (s) p99", f"{percentile(ins, 99):.4f}"])
        else:
            summary_rows.append(["Insert latency", "N/A"])

        # read latencies statistics
        if metrics["read_latencies"]:
            r = metrics["read_latencies"]
            summary_rows.append(["Read latency (s) mean", f"{statistics.mean(r):.4f}"])
            summary_rows.append(["Read latency (s) p50", f"{percentile(r, 50):.4f}"])
            summary_rows.append(["Read latency (s) p95", f"{percentile(r, 95):.4f}"])
            summary_rows.append(["Read latency (s) p99", f"{percentile(r, 99):.4f}"])
        else:
            summary_rows.append(["Read latency", "N/A"])

        # counts and restarts
        summary_rows.append(["Insert success (count)", metrics["insert_success"]])
        summary_rows.append(["Insert fail (count)", metrics["insert_fail"]])
        summary_rows.append(["Concurrent insert success", metrics["concurrent_insert_success"]])
        summary_rows.append(["Concurrent insert fail", metrics["concurrent_insert_fail"]])
        summary_rows.append(["Transaction restarts observed", metrics["transaction_restarts"]])

        # recovery times
        if metrics["recovery_times"]:
            valid = [x for x in metrics["recovery_times"] if x is not None]
            if valid:
                summary_rows.append(["Recovery time (s) mean", f"{statistics.mean(valid):.3f}"])
                summary_rows.append(["Recovery time (s) p50", f"{percentile(valid,50):.3f}"])
            else:
                summary_rows.append(["Recovery time (s) mean", "timeout or none"])
        else:
            summary_rows.append(["Recovery time (s)", "N/A"])

        print("\n==== TEST SUMMARY ====")
        print(tabulate(summary_rows, headers=["Metric", "Value"], tablefmt="github"))

    finally:
        # always clean up test db to avoid lingering resources
        try:
            drop_test_db()
        except Exception as e:
            print("Warning: failed to drop test DB:", e)

if __name__ == "__main__":
    run_all()