import os
import json
from time import sleep
from urllib.parse import parse_qs, urlencode
from seleniumwire import webdriver
from seleniumwire.utils import decode
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
import traceback

with open("config.json", "r") as f:
    config = json.load(f)


options = webdriver.ChromeOptions()
options.add_argument("--incognito")
options.add_argument("--headless")
options.add_argument("--remote-debugging-port=9222")
options.add_argument("--disable-extensions")
options.add_argument("--disable-plugins-discovery")
options.binary_location = config["CHROME_BINARY"]


def init_driver(driver):
    driver.get("https://www.facebook.com")

    wait = WebDriverWait(driver, 30)

    email = wait.until(EC.visibility_of_element_located((By.NAME, "email")))
    email.send_keys(config["FB_EMAIL"])

    password = wait.until(EC.visibility_of_element_located((By.NAME, "pass")))
    password.send_keys(config["FB_PASSWORD"])
    password.send_keys(Keys.RETURN)

    sleep(5)

    driver.get(f"https://www.facebook.com/{config['FB_GROUP_ID']}")

    sleep(5)

    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")

    sleep(5)


def update_body(body, new_cursor):
    body = parse_qs(body)
    body = {k: v[0] for k, v in body.items()}

    old_variables = body["variables"]

    new_variables = json.loads(old_variables)
    new_variables["cursor"] = new_cursor

    body["variables"] = json.dumps(new_variables)

    return urlencode(body)


def fetch_ids(driver, fetch_template, last_cursor, dump_file):
    count = 0

    for request in driver.requests:
        if "graphql" not in request.url:
            continue

        body = decode(request.response.body, request.response.headers.get(
            "Content-Encoding", "identity")).decode()

        if "GroupsCometFeedRegularStories_paginationGroup" not in body:
            continue

        objects = [json.loads(line) for line in body.split("\n")]

        break

    try:
        for obj in objects:
            if not obj.get("label") or "page_info" not in obj["label"]:
                continue

            if last_cursor:
                body = update_body(request.body.decode(), last_cursor)
            else:
                body = request.body.decode()

            break
    except UnboundLocalError:
        print("Not properly initialized. Exiting...")
        return last_cursor

    try:
        while True:
            fetch_request = fetch_template.replace(
                '"body": ""', f'"body": "{body}"')

            fetch_response = driver.execute_script(fetch_request)

            objects = [json.loads(line)
                       for line in fetch_response.split("\n")]

            for obj in objects:
                if obj.keys() == {"data", "extensions"}:
                    post_id = obj["data"]["node"]["group_feed"]["edges"][0]["node"]["post_id"]
                elif obj.keys() == {"label", "path", "data", "extensions"}:
                    if "page_info" in obj["label"]:
                        new_cursor = obj["data"]["page_info"]["end_cursor"]
                        body = update_body(body, new_cursor)
                        continue
                    try:
                        post_id = obj["data"]["node"]["post_id"]
                    except KeyError:
                        continue
                else:
                    continue

                dump_file.write(post_id + "\n")
                count += 1

                os.system("cls") if os.name == "nt" else os.system("clear")
                print(f"Fetched IDs count (current session): {count}")

            sleep(5)
    except KeyboardInterrupt:
        print("Exiting...")
    except json.JSONDecodeError:
        print("Response empty. Exiting...")

    try:
        return new_cursor
    except NameError:
        return last_cursor


def main():
    try:
        driver = webdriver.Chrome(options=options)
        init_driver(driver)

        with open("fetch_template.js", "r") as fetch_template_file:
            fetch_template = fetch_template_file.read()

        try:
            with open("last_cursor.txt", "r") as last_cursor_file:
                last_cursor = last_cursor_file.read()
        except FileNotFoundError:
            last_cursor = ""

        with open("dump.txt", "a") as dump_file:
            last_cursor = fetch_ids(
                driver, fetch_template, last_cursor, dump_file)

        with open("last_cursor.txt", "w") as last_cursor_file:
            last_cursor_file.write(last_cursor)
    except KeyboardInterrupt:
        print("Exiting...")
    except Exception as e:
        print(f"Error occurred: {str(e)}")
        traceback.print_exc()
    finally:
        try:
            driver.quit()
        except NameError:
            pass


if __name__ == "__main__":
    main()
