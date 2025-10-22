from playwright.sync_api import sync_playwright
import json
import time
from pathlib import Path


def scrape_minecraft_servers_infinite(
    pause_for_manual_auth=True,
    existing_file="minecraft_servers.json"
):
    """
    Scrape Minecraft server IPs from a site using infinite scroll and 'COPY IP' buttons.
    Appends unique new IPs to an existing JSON file if present.
    """
    all_ips = set()

    # Load existing IPs from previous scrape
    existing_data = {}
    existing_ips = set()
    path = Path(existing_file)
    if path.exists():
        with open(path, "r", encoding="utf-8") as f:
            existing_data = json.load(f)
            existing_ips = set(existing_data.get("servers", []))
        print(f"Loaded {len(existing_ips)} existing IPs from {existing_file}")
        all_ips.update(existing_ips)
    else:
        print("No existing JSON file found — starting fresh.")

    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(
                headless=False,
                slow_mo=50,
                args=['--disable-blink-features=AutomationControlled']
            )
            context = browser.new_context(
                viewport={'width': 1280, 'height': 900},
                user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64)'
            )
            page = context.new_page()

            # Hide webdriver flag
            page.add_init_script("""
                Object.defineProperty(navigator, 'webdriver', {get: () => undefined});
            """)

            url = "https://findmcserver.com/servers"  # replace with your target URL
            print(f"Opening {url}")
            page.goto(url, timeout=120000)
            page.wait_for_load_state("networkidle")
            time.sleep(3)

            if pause_for_manual_auth:
                print("\n--- Manual Step ---")
                print("Solve any CAPTCHA/login if present, then press Enter here.")
                input("Press Enter when ready to start scraping...")

            last_count = len(all_ips)
            retries = 0
            prev_scroll_height = 0

            while True:
                # Scroll down to load more servers
                page.evaluate("window.scrollBy(0, document.body.scrollHeight)")
                time.sleep(3)

                # Find all COPY IP spans by ID or aria-label pattern
                buttons = page.query_selector_all("[id*='copy-button'], [aria-label*='Copy IP']")
                print(f"Detected {len(buttons)} 'COPY IP' spans")

                for idx in range(len(buttons)):
                    try:
                        # Re-locate each time to avoid stale elements
                        fresh_buttons = page.query_selector_all("[id*='copy-button'], [aria-label*='Copy IP']")
                        if idx >= len(fresh_buttons):
                            continue
                        btn = fresh_buttons[idx]

                        # Scroll it into view
                        page.evaluate("(el) => el.scrollIntoView({behavior: 'smooth', block: 'center'})", btn)
                        time.sleep(0.2)

                        # Click using JS (bypasses parent anchors)
                        page.evaluate("(el) => el.click()", btn)
                        time.sleep(0.4)

                        # Read copied IP
                        ip = page.evaluate("navigator.clipboard.readText()")
                        if ip and '.' in ip and ip not in all_ips:
                            all_ips.add(ip.strip())
                            print(f"Got IP: {ip.strip()}")

                    except Exception as e:
                        print(f"Error reading IP: {e}")
                        continue

                # Detect scroll height change (end of list)
                current_height = page.evaluate("document.body.scrollHeight")
                if current_height == prev_scroll_height:
                    retries += 1
                    if retries >= 3:
                        print("No more new content loaded. Stopping.")
                        break
                else:
                    retries = 0
                    prev_scroll_height = current_height

                if len(all_ips) == last_count:
                    retries += 1
                    if retries >= 3:
                        print("No new IPs found after several scrolls. Stopping.")
                        break
                else:
                    retries = 0
                    last_count = len(all_ips)

            print(f"\n✓ Found {len(all_ips)} total unique IPs (including existing)")
            browser.close()

    except KeyboardInterrupt:
        print("Aborted by user.")
        try:
            browser.close()
        except Exception:
            pass

    # Merge and update metadata
    merged_ips = sorted(all_ips)
    updated_data = {
        "total_servers": len(merged_ips),
        "scraped_pages": existing_data.get("scraped_pages", 0),
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
        "servers": merged_ips
    }

    # Write back to JSON
    with open(existing_file, "w", encoding="utf-8") as f:
        json.dump(updated_data, f, indent=2)

    print(f"✓ Appended new IPs and updated {existing_file}")
    return merged_ips


if __name__ == "__main__":
    scrape_minecraft_servers_infinite(pause_for_manual_auth=True)
