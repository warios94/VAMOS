import time
from datetime import datetime, timedelta
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import os
import random

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Firefox/121.0",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 17_2_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.2 Mobile/15E148 Safari/604.1"
]

def _scrape_url(driver, url):
    matches = []
    driver.get(url)
    wait = WebDriverWait(driver, 20)
    try:
        accept_button = wait.until(EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'I Accept')]")))
        accept_button.click()
        time.sleep(random.uniform(1, 2))
    except:
        pass
    
    match_table = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "table.result")))
    rows = match_table.find_elements(By.TAG_NAME, "tr")
    current_tournament = ""
    for i in range(len(rows)):
        row = rows[i]
        cls = row.get_attribute("class")
        if "head flags" in cls:
            try:
                current_tournament = row.find_element(By.CSS_SELECTOR, "td.t-name").text
            except:
                current_tournament = "Unknown Tournament"
            continue
        if "bott" in cls:
            try:
                player_elements = row.find_elements(By.CSS_SELECTOR, "td.t-name a")
                odds_elements = row.find_elements(By.CSS_SELECTOR, "td.course, td.coursew")
                if len(player_elements) >= 2:
                    p1_name = player_elements[0].text
                    o1 = float(odds_elements[0].text) if odds_elements and odds_elements[0].text else 1.0
                    o2 = float(odds_elements[1].text) if odds_elements and len(odds_elements) > 1 and odds_elements[1].text else 1.0
                    if i + 1 < len(rows):
                        next_row = rows[i+1]
                        player2_element = next_row.find_element(By.CSS_SELECTOR, "td.t-name a")
                        p2_name = player2_element.text
                        matches.append({"p1": p1_name, "p2": p2_name, "o1": o1, "o2": o2, "tournament": current_tournament})
            except:
                continue
    return matches

def scrape_matches(target_date, match_type='atp-single'):
    """
    V75 (Driver Version Lock): Forza la versione 144 di chromedriver.
    """
    url = f"https://www.tennisexplorer.com/next/?type={match_type}&year={target_date.year}&month={target_date.month:02d}&day={target_date.day:02d}"
    print(f"🌐 Scraping TennisExplorer con profilo V75 (Driver Lock): {url}")
    
    options = uc.ChromeOptions()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument(f"user-agent={random.choice(USER_AGENTS)}")
    
    # --- V75: Forza la versione del driver ---
    driver = uc.Chrome(version_main=144, options=options)
    
    try:
        time.sleep(random.uniform(3, 7))
        return _scrape_url(driver, url)
    except Exception as e:
        print(f"❌ Errore scraping V75: {e}")
        return []
    finally:
        driver.quit()

if __name__ == '__main__':
    print("--- Testing Scraper V75 ---")
    target_date = datetime(2026, 1, 30)
    upcoming_matches = scrape_matches(target_date)
    if not upcoming_matches:
        print("⚠️ Nessun match ATP trovato. Tento con WTA...")
        upcoming_matches = scrape_matches(target_date, match_type='wta-single')

    if upcoming_matches:
        print(f"✅ Found {len(upcoming_matches)} matches:")
        for i, match in enumerate(upcoming_matches[:10]):
            print(f"  {i+1}. [{match['tournament']}] {match['p1']} ({match['o1']}) vs {match['p2']} ({match['o2']})")
    else:
        print("Nessun match trovato.")
