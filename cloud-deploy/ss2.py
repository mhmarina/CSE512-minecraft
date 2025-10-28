import asyncio
import json
from mcstatus import BedrockServer, JavaServer
from datetime import datetime
from insert_db import insert_data

INPUT = "minecraft_servers.json"

async def query_ips(ip, s, p, results, sem, dt):
    async with sem:
        try:
            status = await (await JavaServer.async_lookup(ip)).async_status()
            res = {
                "ip": ip,
                "timestamp": dt,
                "online": True,
                "latency": status.latency,
                "curr_players": status.players.online,
                "max_players": status.players.max,
            }
            results.append(res)
            p[0] += 1

        except TimeoutError:
            res = {
                "ip": ip,
                "timestamp": dt,
                "online": False
            }
            results.append(res)  
            p[0] += 1  

        except Exception as e:
            # TODO: remove IPs that completely fail from query list
            # or keep them idk
            # maybe we can log the errors or smt and leave it at that?
            s[0] += 1

async def main():
    try:
        with open(INPUT) as f:
            js = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError) as e:
        print(f"Error reading input file: {e}")
        return

    ips = js.get("servers") or []
    print(f"Loaded {len(ips)} servers to query.\n")
    proc = [0]
    skipped = [0]
    results = []
    dt = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    sem = asyncio.Semaphore(50) 
    await asyncio.wait({asyncio.create_task(query_ips(ip, skipped, proc, results, sem, dt)) for ip in ips})
    print(f"processed: {proc[0]}, skipped: {skipped[0]}")

    # results is a list of json objects/ dict
    # run and pipe output to out.txt:
    # python3 ss2.py > out.txt
    # Insertion to DB:
    insert_data(results)


if __name__ == "__main__":
    asyncio.run(main())
