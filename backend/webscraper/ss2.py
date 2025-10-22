import asyncio
import aiohttp
import json
import time
from aiohttp import ClientTimeout
from pathlib import Path

API = "https://api.mcsrvstat.us/3/{}"  # append ip or ip:port
INPUT = "minecraft_servers.json"
OUTDIR = Path("results")
OUTDIR.mkdir(exist_ok=True)

SEM_LIMIT = 20  # tune based on API tolerance
TIMEOUT = ClientTimeout(total=25)

async def fetch_one(session, sem, ip):
    url = API.format(ip)
    async with sem:
        for attempt in range(4):
            try:
                async with session.get(url, timeout=TIMEOUT) as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        data["_queried_at"] = int(time.time())
                        data["_ip"] = ip
                        return data
                    elif resp.status in (429, 502, 503):
                        # rate limit or transient server error - backoff
                        await asyncio.sleep(2 ** attempt)
                    else:
                        # other HTTP errors - record and stop
                        return {"_ip": ip, "error_http_status": resp.status, "_queried_at": int(time.time())}
            except Exception:
                await asyncio.sleep(2 ** attempt)
        return {"_ip": ip, "error": "max_retries", "_queried_at": int(time.time())}

async def main():
    try:
        with open(INPUT) as f:
            js = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError) as e:
        print(f"Error reading input file: {e}")
        return

    ips = js.get("ips") or js.get("servers") or []
    print(f"Loaded {len(ips)} servers to query.")

    sem = asyncio.Semaphore(SEM_LIMIT)
    conn = aiohttp.TCPConnector(limit=SEM_LIMIT)

    async with aiohttp.ClientSession(
        connector=conn, headers={"User-Agent": "MyBot/1.0 (+your-email)"}
    ) as session:
        tasks = [fetch_one(session, sem, ip) for ip in ips]
        results = []
        skipped = 0

        for coro in asyncio.as_completed(tasks):
            res = await coro
            # Skip any result with error keys
            if "error" in res or "error_http_status" in res:
                skipped += 1
                continue

            results.append(res)
            # Save valid results incrementally
            with open(OUTDIR / f"{res['_ip'].replace(':','_')}.json", "w") as f:
                json.dump(res, f)

    # Write summary index file
    with open(OUTDIR / f"index_{int(time.time())}.json", "w") as f:
        json.dump({
            "count_saved": len(results),
            "count_skipped": skipped,
            "generated_at": int(time.time())
        }, f)

    print(f"Done. Saved: {len(results)}, Skipped: {skipped}")

if __name__ == "__main__":
    asyncio.run(main())
