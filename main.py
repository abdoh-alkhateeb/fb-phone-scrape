import json
from time import sleep
from seleniumwire import webdriver
from seleniumwire.utils import decode
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait


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

    wait = WebDriverWait(driver, 30)

    email = wait.until(EC.visibility_of_element_located((By.NAME, "email")))
    email.send_keys(config["FB_EMAIL"])

    password = wait.until(EC.visibility_of_element_located((By.NAME, "pass")))
    password.send_keys(config["FB_PASSWORD"])
    password.send_keys(Keys.RETURN)

    sleep(5)

    driver.get(f"http://www.facebook.com/groups/{config['FB_GROUP_ID']}")

    sleep(5)

    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")

    sleep(5)

    for request in driver.requests:
        if "graphql" in request.url:
            body = str(decode(request.response.body, request.response.headers.get(
                'Content-Encoding', 'identity'))).strip("b'")

            if "GroupsCometFeedRegularStories_paginationGroup" in body:
                print(json.loads(body))

                with open("dump.txt", "w") as f:
                    f.write(body)

    driver.close()


if __name__ == "__main__":
    main()
