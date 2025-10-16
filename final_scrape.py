from playwright.sync_api import sync_playwright
import json
import time

def scrape_minecraft_server_list(max_pages=None, pause_for_manual_auth=True):
    """
    Scrape Minecraft server IPs from minecraft-server-list.com,
    but open a visible browser so you can manually complete auth/captcha if needed.

    Args:
        max_pages: Maximum number of pages to scrape (None for unlimited)
        pause_for_manual_auth: If True, load the first page in a visible browser and wait
                               for user to manually solve authentication/captcha before continuing.
    """
    all_ips = []
    try:
        with sync_playwright() as p:
            # Open a visible browser so the user can interact
            browser = p.chromium.launch(
                headless=False,
                slow_mo=50,  # slow down slightly for manual interaction
                args=[
                    '--disable-blink-features=AutomationControlled',
                    '--disable-dev-shm-usage',
                    '--no-sandbox'
                ]
            )

            context = browser.new_context(
                viewport={'width': 1280, 'height': 800},
                user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
            )

            page = context.new_page()

            # Keep removing webdriver property (may help with some detections)
            page.add_init_script("""
                Object.defineProperty(navigator, 'webdriver', {
                    get: () => undefined
                });
            """)

            page_num = 1
            consecutive_failures = 0

            # Load the first page and allow manual auth if requested
            url = "https://minecraft-server-list.com/"
            print(f"Opening browser and navigating to: {url}")
            response = page.goto(url, timeout=120000)
            print(f"Initial page load status: {response.status if response else 'no response object'}")
            # Give the page a moment to run any client-side checks
            page.wait_for_load_state("networkidle", timeout=60000)
            time.sleep(2)

            if pause_for_manual_auth:
                try:
                    # Bring the page to the foreground so the user can see it
                    page.bring_to_front()
                except Exception:
                    pass

                print("\n---- MANUAL STEP REQUIRED ----")
                print("The browser window has been opened for you. Please:")
                print("  1) Complete any CAPTCHA, login, or human verification in the browser window.")
                print("  2) When finished, return to this terminal and press Enter to continue scraping.")
                print("  (If you want to abort, press Ctrl+C in this terminal.)\n")
                input("Press Enter here in the terminal after you finish manual authentication...")

                # Give the page time to settle after manual actions
                page.wait_for_load_state("networkidle", timeout=60000)
                time.sleep(1)

            # Main scraping loop (starts with the page already loaded)
            while True:
                if max_pages and page_num > max_pages:
                    print(f"Reached maximum page limit ({max_pages})")
                    break

                # For page 1 we already loaded the URL; for others, construct the URL
                if page_num == 1:
                    # we already loaded it — but ensure we have the proper URL in case user navigated elsewhere
                    current_url = page.url
                    print(f"Scraping page {page_num}: {current_url}")
                else:
                    url = f"https://minecraft-server-list.com/page/{page_num}/"
                    print(f"Navigating to page {page_num}: {url}")
                    try:
                        response = page.goto(url, timeout=120000)
                        print(f"Page loaded with status: {response.status if response else 'no response object'}")
                        page.wait_for_load_state("networkidle", timeout=60000)
                        time.sleep(2)
                    except Exception as e:
                        print(f"Error loading page {page_num}: {e}")
                        consecutive_failures += 1
                        if consecutive_failures >= 3:
                            print("Too many consecutive failures, stopping.")
                            break
                        time.sleep(5)
                        continue

                # Optional debug: save a screenshot of the page if you want
                # page.screenshot(path=f"debug_page_{page_num}.png")

                # Try to find IP input elements
                ip_elements = page.query_selector_all("input.copylinkinput[name='serverip']")
                if not ip_elements:
                    # Try scrolling / waiting for lazy-loaded content
                    print("IPs not found immediately; scrolling + waiting...")
                    page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
                    time.sleep(2)
                    page.evaluate("window.scrollTo(0, 0)")
                    time.sleep(1)
                    ip_elements = page.query_selector_all("input.copylinkinput[name='serverip']")

                if not ip_elements:
                    print("Still no IPs found on this page — writing HTML for debugging and stopping.")
                    content = page.content()
                    with open("debug_page.html", "w", encoding="utf-8") as f:
                        f.write(content)
                    print("Saved page HTML to debug_page.html")
                    break

                consecutive_failures = 0  # reset on success

                # Extract IPs and avoid duplicates
                page_ips = []
                for el in ip_elements:
                    ip = el.get_attribute("value")
                    if ip and ip not in all_ips:
                        page_ips.append(ip)

                all_ips.extend(page_ips)
                print(f"Found {len(page_ips)} new IPs on page {page_num} (Total: {len(all_ips)})")

                # Pagination: try to click next or navigate by page number
                # First attempt a "next" link with common classes
                next_button = page.query_selector("a.next.page-numbers") or page.query_selector("a:has-text('>'):not(:has-text('>>'))")

                if next_button:
                    print(f"Clicking next button to go to page {page_num + 1}")
                    try:
                        next_button.click()
                        page_num += 1
                        # Wait a bit after clicking
                        page.wait_for_load_state("networkidle", timeout=60000)
                        time.sleep(3)
                    except Exception as e:
                        print(f"Error clicking next button: {e}")
                        break
                else:
                    # fallback: try constructing the next page url and navigating directly
                    next_page_num = page_num + 1
                    next_url = f"https://minecraft-server-list.com/page/{next_page_num}/"
                    print(f"No next button found; attempting to navigate to {next_url}")
                    try:
                        # Try a direct goto to the next page
                        response = page.goto(next_url, timeout=120000)
                        if response and response.status == 200:
                            page_num = next_page_num
                            page.wait_for_load_state("networkidle", timeout=60000)
                            time.sleep(2)
                        else:
                            print("Direct navigation to next page failed or returned non-200. Stopping.")
                            break
                    except Exception as e:
                        print(f"Direct navigation error: {e}")
                        break

                # Safety stop
                if page_num > 200:
                    print("Reached safety page limit (200). Stopping.")
                    break

            # Close browser after scraping
            print("Scraping finished; closing browser.")
            browser.close()

    except KeyboardInterrupt:
        print("\nAborted by user (KeyboardInterrupt). Closing browser if open.")
        try:
            browser.close()
        except Exception:
            pass

    # Save IPs to JSON with metadata
    output = {
        "total_servers": len(all_ips),
        "scraped_pages": page_num,
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
        "servers": all_ips
    }

    with open("minecraft_servers.json", "w", encoding="utf-8") as f:
        json.dump(output, f, indent=2)

    print(f"\n✓ Scraped {len(all_ips)} unique server IPs from {page_num} pages")
    print("✓ Saved to minecraft_servers.json")

    return all_ips

if __name__ == "__main__":
    # Example: open browser for manual auth and then scrape up to 10 pages
    scrape_minecraft_server_list(max_pages=None, pause_for_manual_auth=True)
