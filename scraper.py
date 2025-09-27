from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import json
import pandas as pd
import os
import sys

cred_file = "credenciales_temp.json"
if os.path.exists(cred_file):
    with open(cred_file, "r", encoding="utf-8") as f:
        creds = json.load(f)
    usuario = creds["usuario"]
    password = creds["password"]
    hashtag = creds.get("hashtag", "#IA")
    num_scrolls = creds.get("num_scrolls", 5)
    # Eliminar archivo temporal después de usarlo
    os.remove(cred_file)
else:

    usuario = "45_prueva"
    password = "prueba1234"
    hashtag = "#IA"
    num_scrolls = 5
num_scrolls = 5

print("🚀 Iniciando navegador en modo API...")
options = Options()
options.set_capability("goog:loggingPrefs", {"performance": "ALL"})
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")
options.add_experimental_option("excludeSwitches", ["enable-automation"])
options.add_experimental_option('useAutomationExtension', False)

driver = None
for browser in [webdriver.Chrome, webdriver.Edge]:
    try:
        driver = browser(options=options)
        break
    except:
        continue

if driver is None:
    raise RuntimeError("No se pudo iniciar Chrome ni Edge. Asegúrate de tener los drivers.")

driver.maximize_window()


def extract_tweets_from_search_timeline_json(response_body, seen_ids):
    tweets = []
    try:
        data = json.loads(response_body)
    except:
        return tweets

    def walk(obj):
        if isinstance(obj, dict):
            if "rest_id" in obj and "legacy" in obj:
                tweet_id = obj["rest_id"]
                if not tweet_id or tweet_id in seen_ids:
                    return
                seen_ids.add(tweet_id)

                legacy = obj["legacy"]

                likes = legacy.get("favorite_count", 0)
                retweets = legacy.get("retweet_count", 0)
                text = legacy.get("full_text", "").strip()

                screen_name = "unknown_user"
                try:
                    user_result = obj.get("core", {}).get("user_results", {}).get("result", {})
                    if user_result and "legacy" in user_result:
                        screen_name = user_result["legacy"].get("screen_name", "unknown_user")
                except:
                    pass

                link = f"https://twitter.com/{screen_name}/status/{tweet_id}"

                tweets.append({
                    "Texto": text,
                    "Link": link,
                    "Retweets": str(retweets),
                    "Likes": str(likes)
                })
            else:
                for value in obj.values():
                    walk(value)
        elif isinstance(obj, list):
            for item in obj:
                walk(item)

    walk(data)
    return tweets

driver.get("https://twitter.com/login")
time.sleep(3)

try:
    user_input = WebDriverWait(driver, 15).until(
        EC.presence_of_element_located((By.NAME, "text"))
    )
    user_input.send_keys(usuario)
    user_input.send_keys(Keys.RETURN)
    time.sleep(2)

    pass_input = WebDriverWait(driver, 15).until(
        EC.presence_of_element_located((By.NAME, "password"))
    )
    pass_input.send_keys(password)
    pass_input.send_keys(Keys.RETURN)
    time.sleep(6)

except Exception as e:
    print("⚠️ Error en login:", e)

try:
    search_box = WebDriverWait(driver, 15).until(
        EC.presence_of_element_located((By.XPATH, "//input[@data-testid='SearchBox_Search_Input']"))
    )
    search_box.send_keys(hashtag)
    search_box.send_keys(Keys.RETURN)
    time.sleep(5)
except:
    print("❌ Error al buscar")
    driver.quit()
    exit()

# --- LATEST ---
try:
    latest = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable(
            (By.XPATH, "//span[contains(text(), 'Latest') or contains(text(), 'Más recientes')]"))
    )
    latest.click()
    print("✅ Modo 'Más recientes' activado")
    time.sleep(3)
except:
    print("⚠️ No se encontró 'Latest'")

all_tweets = []
seen_ids = set()

driver.get_log("performance")

for i in range(num_scrolls):
    print(f"  📜 Scroll {i + 1}/{num_scrolls}")
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    time.sleep(4)

    # Capturar logs de red
    logs = driver.get_log("performance")
    for entry in logs:
        try:
            log = json.loads(entry["message"])
            if log.get("message", {}).get("method") == "Network.responseReceived":
                url = log["message"]["params"]["response"]["url"]
                if "SearchTimeline" in url:
                    request_id = log["message"]["params"]["requestId"]
                    try:
                        # 🔥 Aquí está la magia: obtenemos el JSON puro de la API
                        body = driver.execute_cdp_cmd("Network.getResponseBody", {"requestId": request_id})
                        response_text = body.get("body", "")
                        if response_text:
                            new_tweets = extract_tweets_from_search_timeline_json(response_text, seen_ids)
                            all_tweets.extend(new_tweets)
                    except:
                        continue
        except:
            continue

    print(f"     ➕ Total: {len(all_tweets)} tweets")

if all_tweets:
    df = pd.DataFrame(all_tweets, columns=["Texto", "Link", "Retweets", "Likes"])
    df.to_csv("tweets_api_puro.csv", index=False, encoding="utf-8")
    print(f"\n✅ ¡Éxito! {len(all_tweets)} tweets guardados en 'tweets_api_puro.csv'")
else:
    print("\n No se extrajeron tweets. Posibles causas:")
    print("   - Cuenta con CAPTCHA / 2FA")
    print("   - Hashtag sin resultados recientes")
    print("   - Bloqueo temporal por X")

driver.quit()