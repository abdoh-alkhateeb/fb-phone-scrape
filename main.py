import os
import json
import traceback
from time import sleep
from urllib.parse import parse_qs, urlencode
from seleniumwire import webdriver
from seleniumwire.utils import decode
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait


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


def update_fetch_post_body(body, new_cursor):
    body = parse_qs(body)
    body = {k: v[0] for k, v in body.items()}

    old_variables = body["variables"]

    new_variables = json.loads(old_variables)
    new_variables["cursor"] = new_cursor

    body["variables"] = json.dumps(new_variables)

    return urlencode(body)


def update_fetch_comment_body(body, story_id, feedback_id):
    body = parse_qs(body)
    body = {k: v[0] for k, v in body.items()}

    old_variables = """{"UFI2CommentsProvider_commentsKey":"CometFocusedStoryView","feedbackID":"ZmVlZGJhY2s6MzU1MjM2NjEzNTAyNTU4MA==","feedbackSource":110,"feedLocation":"DEDICATED_COMMENTING_SURFACE","scale":1,"storyID":"UzpfSTYxNTUyNzM2MDY2MzgwOlZLOjM1NTIzNjYxMzUwMjU1ODA=","__relay_internal__pv__CometUFIIsRTAEnabledrelayprovider":false,"__relay_internal__pv__CometUFIReactionsEnableShortNamerelayprovider":false}"""
    new_variables = json.loads(old_variables)
    new_variables["storyID"] = story_id
    new_variables["feedbackID"] = feedback_id

    body["variables"] = json.dumps(new_variables)
    body["fb_api_req_friendly_name"] = "CometFocusedStoryViewUFIQuery"

    return urlencode(body)


def fetch_ids(driver, fetch_post_template, fetch_comment_template, last_cursor, dump_directory):
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
                body = update_fetch_post_body(
                    request.body.decode(), last_cursor)
            else:
                body = request.body.decode()

            break
    except UnboundLocalError:
        print("Not properly initialized. Exiting...")
        return last_cursor

    try:
        while True:
            fetch_post_request = fetch_post_template.replace(
                '"body": ""',
                f'"body": "{body}"').replace(
                    '"referrer": ""',
                    '"referrer": "https://www.facebook.com/groups/' + config['FB_GROUP_ID'] + '"')

            fetch_post_response = driver.execute_script(fetch_post_request)

            objects = [json.loads(line)
                       for line in fetch_post_response.split("\n")]

            for obj in objects:
                if obj.keys() == {"data", "extensions"}:
                    node = obj["data"]["node"]["group_feed"]["edges"][0]["node"]
                elif obj.keys() == {"label", "path", "data", "extensions"}:
                    if "page_info" in obj["label"]:
                        new_cursor = obj["data"]["page_info"]["end_cursor"]
                        body = update_fetch_post_body(body, new_cursor)
                        continue
                    try:
                        node = obj["data"]["node"]
                    except KeyError:
                        continue
                else:
                    continue

                dump_file_name = os.path.join(dump_directory, node["post_id"])
                with open(f"{dump_file_name}.json", "w", encoding="utf-8") as dump_file:
                    id = node["post_id"]
                    story = node["comet_sections"]["content"]["story"]
                    try:
                        text = story["message"]["text"]
                    except TypeError:
                        text = ""

                    story_id = story["id"]
                    feedback_id = story["feedback"]["id"]

                    _body = update_fetch_comment_body(
                        body, story_id, feedback_id)

                    print(_body)

                    fetch_comment_request = fetch_comment_template.replace(
                        '"body": ""',
                        f'"body": "{_body}"').replace(
                            '"referrer": ""',
                            '"referrer": "https://www.facebook.com/groups/' + config['FB_GROUP_ID'] + '"')

                    result = driver.execute_script(fetch_comment_request)

                    # print(type(result))
                    # print(result)

                    comments = []
                    json.dump({"id": id, "text": text, "comments": comments},
                              dump_file, ensure_ascii=False)

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

        last_cursor = fetch_ids(driver, fetch_post_template,
                                fetch_comment_template, last_cursor, dump_directory)

        with open("last_cursor.txt", "w") as last_cursor_file:
            last_cursor_file.write(last_cursor)
    except KeyboardInterrupt:
        print("Exiting...")
    except Exception as e:
        print(f"Error occurred:\n{traceback.format_exc()}")
    finally:
        try:
            driver.quit()
        except NameError:
            pass


if __name__ == "__main__":
    main()
