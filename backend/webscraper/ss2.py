import asyncio
import json
from mcstatus import BedrockServer, JavaServer

INPUT = "minecraft_servers.json"

async def query_ips(ip, s, p, results, sem):
    async with sem:
        try:
            status = await (await JavaServer.async_lookup(ip)).async_status()
            res = {
                "ip": ip,
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
                "online": False
            }
            results.append(res)  
            p[0] += 1  

        except:
            # try bedrock
            try:
                status = await (await BedrockServer.async_lookup(ip)).async_status()
                res = {
                    "ip": ip,
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
                    "online": False
                }
                results.append(res)  
                p[0] += 1  
            
            # any other errors are a lost cause...
            except:
                # TODO: remove these IPs
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
    sem = asyncio.Semaphore(50) 
    await asyncio.wait({asyncio.create_task(query_ips(ip, skipped, proc, results, sem)) for ip in ips})
    print(f"processed: {proc[0]}, skipped: {skipped[0]}")

    # results is a list of json objects/ dict
    # run and pipe output to out.txt:
    # python3 ss2.py > out.txt
    # we can do insertions HERE:
    for result in results:
        print(json.dumps(result, indent=4))
        print("")

if __name__ == "__main__":
    asyncio.run(main())
