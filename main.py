import time
import random
import string
import re
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options


# === CONFIGURATION ===
PASSWORD = "Kundan@2028"
CREDENTIALS_FILE = "cred.txt"
IG_SIGNUP_URL = "https://www.instagram.com/accounts/emailsignup/"
MAILDROP_BASE = "https://maildrop.cc/inbox/?mailbox="
TARGET_USERNAME = "shivyaansh_singh"
TARGET_PROFILE_URL = f"https://www.instagram.com/{TARGET_USERNAME}/"
TARGET_FOLLOW_USERNAME = "desidynamitexd"

# === Generate Random Mailbox
def generate_mailbox():
    name = "auto_" + ''.join(random.choices(string.ascii_lowercase + string.digits, k=8))
    return name, f"{name}@maildrop.cc"

mailbox_name, email = generate_mailbox()
username = "user_" + mailbox_name[5:]
full_name = "Maildrop User"

# === START SELENIUM
options = Options()
options.add_argument("--headless=new")
options.add_argument("--disable-gpu")
options.add_argument("--window-size=1920,1080")

driver = webdriver.Chrome(service=Service(), options=options)
wait = WebDriverWait(driver, 30)
driver.maximize_window()

try:
    # STEP 1: Signup Form
    driver.get(IG_SIGNUP_URL)
    wait.until(EC.presence_of_element_located((By.NAME, "emailOrPhone"))).send_keys(email)
    driver.find_element(By.NAME, "fullName").send_keys(full_name)
    driver.find_element(By.NAME, "username").send_keys(username)
    driver.find_element(By.NAME, "password").send_keys(PASSWORD)
    signup_btn = wait.until(EC.element_to_be_clickable((By.XPATH, "//button[contains(text(),'Sign up')]")))
    driver.execute_script("arguments[0].click();", signup_btn)

    # STEP 2: Fill Birthday
    wait.until(EC.presence_of_element_located((By.XPATH, "//select[@title='Month:']")))
    Select(driver.find_element(By.XPATH, "//select[@title='Month:']")).select_by_visible_text("May")
    Select(driver.find_element(By.XPATH, "//select[@title='Day:']")).select_by_visible_text("18")
    Select(driver.find_element(By.XPATH, "//select[@title='Year:']")).select_by_visible_text("2000")
    driver.find_element(By.XPATH, "//button[text()='Next']").click()

    # STEP 3: OTP Page
    wait.until(EC.presence_of_element_located((By.NAME, "email_confirmation_code")))
    print(f"[📨] Waiting for OTP at {email}...")

    # STEP 4: Open Maildrop
    driver.execute_script(f"window.open('{MAILDROP_BASE}{mailbox_name}', '_blank');")
    driver.switch_to.window(driver.window_handles[1])

    # STEP 5: OTP Retry Loop
    otp = None
    for attempt in range(4):  # Retry 15 times
        try:
            driver.refresh()
            time.sleep(2)
            body_text = driver.find_element(By.TAG_NAME, "body").text
            match = re.search(r"\b\d{6}\b", body_text)
            if match:
                otp = match.group(0)
                print(f"[✅] OTP Detected: {otp}")
                break
        except:
            pass
        time.sleep(2)

    if not otp:
        print("[❌] OTP not found. Exiting this run.")
        driver.quit()
        exit()

    # STEP 6: Submit OTP
    driver.switch_to.window(driver.window_handles[0])
    otp_input = wait.until(EC.presence_of_element_located((By.NAME, "email_confirmation_code")))
    otp_input.clear()
    otp_input.send_keys(otp)
    otp_input.send_keys(Keys.ENTER)
    print("[🚀] OTP Submitted. Waiting for redirect...")

    # STEP 7: Wait for Instagram homepage
    for _ in range(35):
        if "instagram.com" in driver.current_url and "accounts" not in driver.current_url:
            print("[✅] Logged in. Proceeding.")
            break
        time.sleep(1)
    else:
        print("[❌] Login stuck after OTP. Exiting.")
        driver.quit()
        exit()

    # STEP 8: Save Account
    with open(CREDENTIALS_FILE, "a") as f:
        f.write(f"{email} | {username} | {PASSWORD} | SUCCESS\n")
    print(f"[💾] Saved: {email} | {username}")

    # STEP 9: Open target profile directly
    driver.get(TARGET_PROFILE_URL)
    time.sleep(4)

    follow_button = wait.until(EC.element_to_be_clickable((By.XPATH, "//button[normalize-space()='Follow']")))
    driver.execute_script("arguments[0].click();", follow_button)
    print(f"[✅] Followed @{TARGET_USERNAME}")
    time.sleep(2)

    # STEP 10: Open followers and follow second user
    followers_link = wait.until(EC.element_to_be_clickable((By.PARTIAL_LINK_TEXT, "followers")))
    driver.execute_script("arguments[0].click();", followers_link)
    time.sleep(4)

    popup_search = wait.until(EC.presence_of_element_located((By.XPATH, "//div[@role='dialog']//input[@placeholder='Search']")))
    popup_search.send_keys(TARGET_FOLLOW_USERNAME)
    time.sleep(2)

    follow_targets = driver.find_elements(By.XPATH, "//div[@role='dialog']//button[normalize-space()='Follow']")
    for btn in follow_targets:
        try:
            driver.execute_script("arguments[0].click();", btn)
            print(f"[✅] Followed @{TARGET_FOLLOW_USERNAME}")
            break
        except:
            continue

except Exception as e:
    print(f"[❌] ERROR: {e}")
    with open(CREDENTIALS_FILE, "a") as f:
        f.write(f"{email} | {username} | {PASSWORD} | FAILED\n")

finally:
    driver.quit()
    print("✅ DONE — Jai Shree Ram 🚩")
