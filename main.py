import json
from time import sleep
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By


options = webdriver.ChromeOptions()
options.add_argument("--disable-extensions")
options.add_argument("--profile-directory=Default")
options.add_argument("--incognito")
options.add_argument("--disable-plugins-discovery")
options.add_argument("--start-maximized")
options.add_argument("--disable-infobars")
options.add_argument("--remote-debugging-port=9222")
options.binary_location = "/snap/bin/chromium"


with open("config.json", "r") as f:
    config = json.load(f)


def main():
    driver = webdriver.Chrome(options=options)

    driver.get("http://www.facebook.com")

    sleep(2)

    email = driver.find_element(By.ID, "email")
    email.clear()
    email.send_keys(config["FB_EMAIL"])

    password = driver.find_element(By.ID, "pass")
    password.clear()
    password.send_keys(config["FB_PASSWORD"])
    password.send_keys(Keys.RETURN)

    sleep(2)

    driver.get(f"http://www.facebook.com/groups/{config['FB_GROUP_ID']}")

    with open("script.js", "r") as f:
        driver.execute_script(f.read())

    sleep(60)

    driver.close()


if __name__ == "__main__":
    main()
