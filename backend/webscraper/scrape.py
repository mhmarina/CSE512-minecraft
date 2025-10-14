#!/usr/bin/env python3
# scrape_minecraft_server_list.py

from playwright.sync_api import sync_playwright
import json
import time

URL = "https://minecraft-server-list.com/"
OUTFILE = "minecraft_serverlist_ips.json"

def scrape_all_ips():
    ips = set()
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page(user_agent="Mozilla/5.0 (compatible; MinecraftScraper/1.0)")
        page.goto(URL, timeout=60000)
        time.sleep(2)

        page_no = 1
        while True:
            print(f"Scraping page {page_no}...")

            # Each IP is in a green box inside the "IP Address" column
            ip_elements = page.locator("input.copylinkinput")
            count = ip_elements.count()
            if count == 0:
                print(f"No IPs found on page {page_no} stopping.")
                break

            for i in range(count):
                ip = ip_elements.nth(i).input_value()
                if ip:
                    ips.add(ip)

            # Try to click the "Next" button if available
            next_button = page.get_by_role("link", name=">").first
            if next_button.count() == 0 or not next_button.is_enabled():
                print("No more pages, done.")
                break

            next_button.first.click()
            page.wait_for_timeout(2000)
            page_no += 1

        browser.close()

    return sorted(ips)

def main():
    start = time.time()
    ips = scrape_all_ips()
    data = {"timestamp": int(time.time()), "count": len(ips), "ips": ips}
    with open(OUTFILE, "w") as f:
        json.dump(data, f, indent=2)
    print(f"Scraped {len(ips)} IPs in {time.time()-start:.1f}s → saved to {OUTFILE}")

if __name__ == "__main__":
    main()
