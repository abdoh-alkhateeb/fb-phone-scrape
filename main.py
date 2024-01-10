import os
import json
import traceback
from time import sleep
from seleniumwire import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from utils import (extract_graphql_objects_from_requests,
                   process_extracted_graphql_objects,
                   update_fetch_post_body,
                   fetch_posts, fetch_comments)


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

    driver.get(
        f"https://www.facebook.com/groups/{config['FB_GROUP_ID']}?sorting_setting=CHRONOLOGICAL")

    sleep(5)

    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")

    sleep(5)


def fetch_data(driver, fetch_post_template, fetch_comment_template, last_cursor, dump_directory):
    count = 0

    request, objects = extract_graphql_objects_from_requests(driver)

    try:
        body = process_extracted_graphql_objects(request, objects, last_cursor)
    except UnboundLocalError:
        print("Not properly initialized. Exiting...")
        return last_cursor

    try:
        while True:
            nodes, new_cursor = fetch_posts(
                driver, body, fetch_post_template, config["FB_GROUP_ID"])

            for node in nodes:
                dump_file_name = os.path.join(dump_directory, node["post_id"])
                with open(f"{dump_file_name}.json", "w", encoding="utf-8") as dump_file:
                    id = node["post_id"]
                    story = node["comet_sections"]["content"]["story"]
                    try:
                        text = story["message"]["text"]
                    except TypeError:
                        text = ""

                    feedback_id = story["feedback"]["id"]

                    comments = fetch_comments(
                        driver, body, fetch_comment_template, feedback_id, config["FB_GROUP_ID"])

                    json.dump({"id": id, "text": text, "comments": comments},
                              dump_file, indent=4, ensure_ascii=False)

                count += 1

                os.system("cls") if os.name == "nt" else os.system("clear")
                print(f"Fetched IDs count (current session): {count}")

            body = update_fetch_post_body(request.body.decode(), new_cursor)

            sleep(5)
    except KeyboardInterrupt:
        print("Exiting...")
    except json.JSONDecodeError:
        print("Response empty or unsupported. Exiting...")

    try:
        return new_cursor
    except NameError:
        return last_cursor


def main():
    try:
        dump_directory = "scrape_out"

        driver = webdriver.Chrome(options=options)
        init_driver(driver)

        with open("fetch_post.js", "r") as fetch_template_file:
            fetch_post_template = fetch_template_file.read()

        with open("fetch_comment.js", "r") as fetch_template_file:
            fetch_comment_template = fetch_template_file.read()

        try:
            with open("last_cursor.txt", "r") as last_cursor_file:
                last_cursor = last_cursor_file.read()
        except FileNotFoundError:
            last_cursor = ""

        os.makedirs(dump_directory, exist_ok=True)

        last_cursor = fetch_data(
            driver, fetch_post_template, fetch_comment_template, last_cursor, dump_directory)

        with open("last_cursor.txt", "w") as last_cursor_file:
            last_cursor_file.write(last_cursor)
    except KeyboardInterrupt:
        print("Exiting...")
    except:
        print(f"Error occurred:\n{traceback.format_exc()}")
    finally:
        try:
            driver.quit()
        except NameError:
            pass


if __name__ == "__main__":
    main()
