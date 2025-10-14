# query_mcsrvstat.py
import asyncio
import aiohttp
import json
import time
from aiohttp import ClientTimeout
from pathlib import Path

API = "https://api.mcsrvstat.us/2/{}"  # append ip or ip:port
INPUT = "minecraft_ips.json"
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
            except Exception as e:
                await asyncio.sleep(2 ** attempt)
        return {"_ip": ip, "error": "max_retries", "_queried_at": int(time.time())}

async def main():
    js = json.load(open(INPUT))
    ips = js.get("ips", [])
    sem = asyncio.Semaphore(SEM_LIMIT)
    conn = aiohttp.TCPConnector(limit=SEM_LIMIT)
    async with aiohttp.ClientSession(connector=conn, headers={"User-Agent": "MyBot/1.0 (+your-email)"}) as session:
        tasks = [fetch_one(session, sem, ip) for ip in ips]
        results = []
        for coro in asyncio.as_completed(tasks):
            res = await coro
            results.append(res)
            # stream to disk incrementally to avoid losing everything on crash:
            with open(OUTDIR / f"{res['_ip'].replace(':','_')}.json", "w") as f:
                json.dump(res, f)
    # Optionally write an index file
    with open(OUTDIR / f"index_{int(time.time())}.json", "w") as f:
        json.dump({"count": len(results), "generated_at": int(time.time())}, f)
    print("Done. Fetched:", len(results))

if __name__ == "__main__":
    asyncio.run(main())
