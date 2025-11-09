"""
archive_scraper_uc_full.py
Stealth Product Hunt Launch Archive scraper using undetected-chromedriver + Selenium.
Extracts product details (name, URL, description, tags, votes) and saves to CSV.

Requirements:
- pip install undetected-chromedriver selenium pandas
- Optional: set USER_DATA_DIR to reuse a Chrome profile (recommended)
"""

import os
import time
import traceback
import pandas as pd
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, StaleElementReferenceException
from selenium.webdriver.common.action_chains import ActionChains

# === CONFIG ===
START_URL = "https://www.producthunt.com/"
USER_DATA_DIR = r"D:/Work/chrome_profile"   # optional persistent profile
WAIT_LONG = 30
WAIT_VERY_LONG = 60
SCROLL_PAUSE = 3  # seconds to wait after scroll

# Output CSV filename
OUTPUT_CSV = "output1.csv"

def build_driver():
    options = uc.ChromeOptions()
    if USER_DATA_DIR:
        os.makedirs(USER_DATA_DIR, exist_ok=True)
        options.add_argument(f"--user-data-dir={USER_DATA_DIR}")
    options.add_argument("--start-maximized")
    options.add_argument("--disable-blink-features=AutomationControlled")
    driver = uc.Chrome(options=options)
    return driver

def wait_for_element_clickable(driver, locator, timeout=WAIT_LONG):
    wait = WebDriverWait(driver, timeout)
    return wait.until(EC.element_to_be_clickable(locator))

def wait_for_elements_present(driver, locator, timeout=WAIT_LONG):
    wait = WebDriverWait(driver, timeout)
    return wait.until(EC.presence_of_all_elements_located(locator))

def scroll_to_load_all(driver, pause_time=SCROLL_PAUSE, max_empty_scrolls=3):
    empty_scrolls = 0
    last_count = 0

    while True:
        product_cards = driver.find_elements(By.CSS_SELECTOR, "section[data-test^='post-item-']")
        current_count = len(product_cards)

        if current_count == last_count:
            empty_scrolls += 1
        else:
            empty_scrolls = 0
            last_count = current_count

        if empty_scrolls >= max_empty_scrolls:
            break

        if product_cards:
            last_card = product_cards[-1]
            ActionChains(driver).move_to_element(last_card).perform()

        time.sleep(pause_time)

def main():
    driver = None
    all_products = []

    try:
        driver = build_driver()
        print("Driver launched. Opening Product Hunt...")
        driver.get(START_URL)
        time.sleep(2)

        try:
            launches = wait_for_element_clickable(
                driver, (By.XPATH, "//a[contains(normalize-space(.),'Launches')]"), timeout=WAIT_VERY_LONG
            )
            print("Found 'Launches' link — clicking it now.")
            launches.click()
        except TimeoutException:
            raise RuntimeError("Could not find 'Launches' link — possibly blocked by verification.")
        time.sleep(2)

        try:
            archive_elem = wait_for_element_clickable(
                driver,
                (By.XPATH, "//a[contains(translate(., 'ABCDEFGHIJKLMNOPQRSTUVWXYZ','abcdefghijklmnopqrstuvwxyz'), 'archive') and (contains(., 'Launch') or contains(., 'launch'))]"),
                timeout=10
            )
            print("Found 'Launch Archive' — clicking.")
            archive_elem.click()
            time.sleep(3)
        except TimeoutException:
            print("No explicit 'Launch Archive' link found — using current page.")

        all_url = driver.find_element(By.XPATH, "//a[contains(@href, '/all')]").get_attribute("href")
        driver.get(all_url)
        print(f"Navigated directly to ALL tab URL: {all_url}")
        time.sleep(3)

        print("Scrolling to load all products...")
        scroll_to_load_all(driver)
        print("✅ 'All' tab fully loaded with new product cards.")

        product_cards = wait_for_elements_present(
            driver, (By.CSS_SELECTOR, "section[data-test^='post-item-']"), timeout=WAIT_VERY_LONG
        )
        print(f"Found {len(product_cards)} product cards (including promoted).")

        for card in product_cards:
            try:
                try:
                    card.find_element(By.CSS_SELECTOR, "button[data-test='vote-button']")
                except:
                    continue

                name_elem = card.find_element(By.CSS_SELECTOR, "div[data-test^='post-name-'] a")
                product_name = name_elem.text.strip()
                product_url = name_elem.get_attribute("href")

                try:
                    description = card.find_element(By.CSS_SELECTOR, "div.text-16.font-normal").text.strip()
                except:
                    description = ""

                try:
                    tags = [t.text.strip() for t in card.find_elements(By.CSS_SELECTOR, "div[data-sentry-component='TagList'] a")]
                except:
                    tags = []

                try:
                    votes = card.find_element(By.CSS_SELECTOR, "button[data-test='vote-button'] p").text.strip()
                except:
                    votes = "0"

                all_products.append({
                    "Title": product_name,
                    "URL": product_url,
                    "Description": description,
                    "Tags": ", ".join(tags),
                    "Votes": votes
                })

                print(f"{len(all_products)}. {product_name} | Votes: {votes} | Tags: {tags}")

            except StaleElementReferenceException:
                continue
            except Exception as e:
                print("Error extracting card:", e)

        df = pd.DataFrame(all_products)
        df.to_csv(OUTPUT_CSV, index=False)
        print(f"\nScraping complete. Saved {len(all_products)} products to '{OUTPUT_CSV}'.")

    except Exception as exc:
        print("ERROR:", exc)
        traceback.print_exc()

    finally:
        if driver:
            # driver.quit()  # Uncomment to auto-close browser
            print("Driver still running (close manually).")

if __name__ == "__main__":
    main()
