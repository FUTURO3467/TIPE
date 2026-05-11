from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import time
from selenium.webdriver.chrome.options import Options

fichier_liens = r"D:\BDDTIPE\DownloadJazz.txt"
liens = []
with open(fichier_liens, 'r') as fichier:
    # Read each line in the file
    for ligne in fichier:
        # Print each line
        liens.append(ligne.strip())

service = Service(executable_path="chromedriver.exe")
chemin_telechargement = r'D:\BDDTIPE\Jazz'

chrome_options = Options()
chrome_options.add_experimental_option('prefs', {
    'download.default_directory': chemin_telechargement,
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
        email.send_keys("joublotleopold@gmail.com")
        password = driver.find_element(By.XPATH, '//*[@id="password"]')
        password.clear()
        password.send_keys("password")
        password.send_keys(Keys.ENTER)

    except:
        print("No login button found / Problem with the login")


driver.get("https://freemusicarchive.org/music/charts/this-month")
time.sleep(0.3)
accept_cookies()
time.sleep(0.3)
log_in()
time.sleep(0.5)
driver.capabilities.setdefault("se:downloadsEnabled", True)
for link in liens:
    driver.execute_script("window.open('" + link + "');")
    time.sleep(1)
time.sleep(20)
driver.quit()
