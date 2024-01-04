import json
from time import sleep
from seleniumwire import webdriver
from seleniumwire.utils import decode
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from urllib.parse import parse_qs, urlencode


with open("config.json", "r") as f:
    config = json.load(f)


options = webdriver.ChromeOptions()
options.add_argument("--disable-extensions")
options.add_argument("--profile-directory=Default")
options.add_argument("--incognito")
options.add_argument("--disable-plugins-discovery")
options.add_argument("--start-maximized")
options.add_argument("--disable-infobars")
options.add_argument("--remote-debugging-port=9222")
options.binary_location = config["CHROME_BINARY"]


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

    with open("fetch_template.js", "r") as f:
        fetch_template = f.read()

    for request in driver.requests:
        if "graphql" in request.url:
            body = decode(request.response.body, request.response.headers.get(
                "Content-Encoding", "identity")).decode()

            if "GroupsCometFeedRegularStories_paginationGroup" in body:
                objects = [json.loads(line) for line in body.split("\n")]

                for obj in objects:
                    if obj.get("label") and "page_info" in obj["label"]:
                        body = str(request.body)

                        while True:
                            fetch_request = fetch_template.replace(
                                '"body": ""', f'"body": "{body}"')

                            fetch_response = driver.execute_script(
                                fetch_request)

                            objects = [json.loads(line)
                                       for line in fetch_response.split("\n")]

                            for obj in objects:
                                if obj.get("label") and "page_info" not in obj["label"]:
                                    if obj["data"].get("node") and obj["data"]["node"].get("post_id"):
                                        print(obj["data"]["node"]["post_id"])
                                elif obj.get("label"):
                                    new_cursor = obj["data"]["page_info"]["end_cursor"]
                                    body = parse_qs(body)
                                    body = {k: v[0] for k, v in body.items()}
                                    old_variables = body["variables"]
                                    new_variables = json.loads(old_variables)
                                    new_variables["cursor"] = new_cursor
                                    body["variables"] = json.dumps(
                                        new_variables)
                                    body = urlencode(body)

                            sleep(5)

    driver.close()


if __name__ == "__main__":
    main()
