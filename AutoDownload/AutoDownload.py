from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import time
from selenium.webdriver.chrome.options import Options

fileName = "D:\BDDTIPE\DownloadClassical.txt"
links = []
with open(fileName, 'r') as file:
    # Read each line in the file
    for line in file:
        # Print each line
        links.append(line.strip())

service = Service(executable_path="chromedriver.exe")
dlpath = r'D:\BDDTIPE\Classical'

chrome_options = Options()
chrome_options.add_experimental_option('prefs', {
    'download.default_directory': dlpath,
    'download.enable_downloads': True,
    'download.prompt_for_download': False,
    'download.directory_upgrade': True,
    'safebrowsing.enabled': True,
    'se:downloadsEnabled': True
})
driver = webdriver.Chrome(service=service, options=chrome_options, )


def accept_cookies():
    try:
        cookies = driver.find_element(By.XPATH, '//*[@id="CybotCookiebotDialogBodyLevelButtonLevelOptinAllowAll"]')
        cookies.click()
    except:
        print("No cookies button found / Problem with the cookies")


def log_in():
    try:
        login = driver.find_element(By.XPATH, '//*[@id="navigation"]/div/nav/div[3]/ul/li[1]/a')
        login.click()
        time.sleep(0.1)
        email = driver.find_element(By.XPATH, '//*[@id="email"]')
        email.click()
        email.clear()
        email.send_keys("EMAIL")
        password = driver.find_element(By.XPATH, '//*[@id="password"]')
        password.clear()
        password.send_keys("PASSWORD")
        password.send_keys(Keys.ENTER)

    except:
        print("No login button found / Problem with the login")


driver.get(
    "https://freemusicarchive.org/search?adv=1&search-genre=Rock&duration_from=0&duration_to=4&music-filter-CC-attribution-only=1&music-filter-CC-attribution-sharealike=1&music-filter-CC-attribution-noncommercial=1&music-filter-CC-attribution-noncommercial-sharealike=1&music-filter-remix-allowed=1")
# driver.get("https://freemusicarchive.org/music/charts/this-month")
time.sleep(0.3)
accept_cookies()
time.sleep(0.3)
log_in()
time.sleep(0.5)
driver.capabilities.setdefault("se:downloadsEnabled", True)
for link in links:
    driver.execute_script("window.open('" + link + "');")
    time.sleep(1)
time.sleep(20)
driver.quit()