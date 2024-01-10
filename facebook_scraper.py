import os
import json
from time import sleep
from urllib.parse import parse_qs, urlencode
from seleniumwire import webdriver
from seleniumwire.utils import decode
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait


class FacebookScraper:
    def __init__(self, options, config):
        self.driver = webdriver.Chrome(options=options)

        self.email = config["FB_EMAIL"]
        self.password = config["FB_PASSWORD"]
        self.group_id = config["FB_GROUP_ID"]
        self.dump_directory = config["DUMP_DIRECTORY"]

        self.cursor = None
        self.fetch_template = None

        self.request = None
        self.body = None

        print("Initializing...", end=" ")

        self.load_cursor()
        self.load_fetch_template()
        self.setup_dump_directory()

        print("done!")

        print("Preparing group...", end=" ")

        self.login()
        self.prepare_group()

        print("done!")

    def load_cursor(self):
        try:
            with open("cursor.txt", "r", encoding="ascii") as f:
                self.cursor = f.read()
        except FileNotFoundError:
            pass

    def load_fetch_template(self):
        with open("fetch_template.js", "r", encoding="utf-8") as f:
            self.fetch_template = f.read()

    def setup_dump_directory(self):
        os.makedirs(self.dump_directory, exist_ok=True)

    def login(self):
        self.driver.get("https://www.facebook.com")

        wait = WebDriverWait(self.driver, 30)

        email = wait.until(EC.visibility_of_element_located((By.NAME, "email")))
        email.send_keys(self.email)

        password = wait.until(EC.visibility_of_element_located((By.NAME, "pass")))
        password.send_keys(self.password)
        password.send_keys(Keys.RETURN)

    def prepare_group(self):
        sleep(5)
        self.driver.get(f"https://www.facebook.com/groups/{self.group_id}?sorting_setting=CHRONOLOGICAL")
        sleep(5)
        self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        sleep(5)

    def run(self):
        self.extract_initial_graphql_request()
        self.prepare_initial_fetch_request_body()

        dump_file = open("dump.txt", "a", encoding="ascii")
        try:
            count = 0
            while True:
                nodes = self.fetch_posts()
                for node in nodes:
                    self.scrape_node(node)
                    dump_file.write(node["post_id"] + "\n")
                    count += 1

                os.system("cls") if os.name == "nt" else os.system("clear")
                print(f"Scraped posts count (current session only): {count}")

                sleep(5)
        except KeyboardInterrupt:
            print("Exiting...")
        except json.JSONDecodeError:
            print("Response empty or unsupported. Exiting...")
        finally:
            dump_file.close()

    def extract_initial_graphql_request(self):
        for request in self.driver.requests:
            if "graphql" not in request.url:
                continue

            body = decode(request.response.body, request.response.headers.get("Content-Encoding", "identity")).decode()

            if "GroupsCometFeedRegularStories_paginationGroup" not in body:
                continue

            self.request = request
            break

    def prepare_initial_fetch_request_body(self):
        if self.cursor:
            self.body = FacebookScraper.generate_fetch_posts_body(self.request.body.decode(), self.cursor)
        else:
            self.body = self.request.body.decode()

    def fetch_posts(self):
        request = self.fetch_template.replace(
            '"body": ""',
            f'"body": "{self.body}"'
        ).replace(
            '"referrer": ""',
            f'"referrer": "https://www.facebook.com/groups/{self.group_id}"'
        ).replace(
            '"x-fb-friendly-name": ""',
            '"x-fb-friendly-name": "GroupsCometFeedRegularStoriesPaginationQuery"'
        )

        response = self.driver.execute_script(request)

        objects = [json.loads(line) for line in response.split("\n")]

        nodes = []

        for obj in objects:
            if obj.keys() == {"data", "extensions"}:
                node = obj["data"]["node"]["group_feed"]["edges"][0]["node"]
            elif obj.keys() == {"label", "path", "data", "extensions"}:
                if "page_info" in obj["label"]:
                    self.cursor = obj["data"]["page_info"]["end_cursor"]
                    self.body = FacebookScraper.generate_fetch_posts_body(self.body, self.cursor)
                    continue
                try:
                    node = obj["data"]["node"]
                except KeyError:
                    continue
            else:
                continue

            nodes.append(node)

        return nodes

    @staticmethod
    def generate_fetch_posts_body(body, cursor):
        body = parse_qs(body)
        body = {k: v[0] for k, v in body.items()}

        old_variables = body["variables"]

        new_variables = json.loads(old_variables)
        new_variables["cursor"] = cursor

        body["variables"] = json.dumps(new_variables)

        return urlencode(body)

    def scrape_node(self, node):
        dump_file_name = os.path.join(self.dump_directory, node["post_id"])
        with open(f"{dump_file_name}.json", "w", encoding="utf-8") as dump_file:
            id = node["post_id"]

            story = node["comet_sections"]["content"]["story"]

            try:
                text = story["message"]["text"]
            except TypeError:
                text = ""

            try:
                comments = self.fetch_comments(story["feedback"]["id"])
            except KeyError:
                comments = []

            json.dump({"id": id, "text": text, "comments": comments},
                      dump_file, indent=4, ensure_ascii=False)

    def fetch_comments(self, feedback_id):
        body = FacebookScraper.generate_fetch_comments_body(self.body, feedback_id)

        request = self.fetch_template.replace(
            '"body": ""',
            f'"body": "{body}"'
        ).replace(
            '"referrer": ""',
            f'"referrer": "https://www.facebook.com/groups/{self.group_id}"'
        ).replace(
            '"x-fb-friendly-name": ""',
            '"x-fb-friendly-name": "CommentListComponentsRootQuery"'
        )

        response = self.driver.execute_script(request)

        data = [json.loads(line)for line in response.split("\n")][0]
        data = data["data"]["node"]["comment_rendering_instance_for_feed_location"]["comments"]

        comments = [edge["node"]["body"].get("text")
                    for edge in data["edges"] if edge["node"]["body"] is not None]

        while data["page_info"].get("has_next_page"):
            body = FacebookScraper.generate_fetch_comments_body(self.body, feedback_id, data["page_info"]["end_cursor"])

            request = self.fetch_template.replace(
                '"body": ""',
                f'"body": "{body}"'
            ).replace(
                '"referrer": ""',
                f'"referrer": "https://www.facebook.com/groups/{self.group_id}"'
            ).replace(
                '"x-fb-friendly-name": ""',
                '"x-fb-friendly-name": "CommentsListComponentsPaginationQuery"'
            )

            response = self.driver.execute_script(request)

            data = [json.loads(line)for line in response.split("\n")][0]
            data = data["data"]["node"]["comment_rendering_instance_for_feed_location"]["comments"]

            comments.extend([edge["node"]["body"].get("text")
                            for edge in data["edges"] if edge["node"]["body"] is not None])

        return comments

    @staticmethod
    def generate_fetch_comments_body(body, feedback_id, cursor=None, is_primary=True):
        body = parse_qs(body)
        body = {k: v[0] for k, v in body.items()}

        if is_primary:
            old_variables = """{"commentsIntentToken":"CHRONOLOGICAL_UNFILTERED_INTENT_V1","feedLocation":"DEDICATED_COMMENTING_SURFACE","feedbackSource":110,"focusCommentID":null,"scale":1,"useDefaultActor":false,"id":"ZmVlZGJhY2s6NzQ1MDIyNzkzMTY5NDkzNg=="}"""
        else:
            old_variables = """{"commentsAfterCount":-1,"commentsAfterCursor":"AQHRcUzPl7NxbfxJnMXQs4HcVjZkY91QnGfoybTKnDJyRRUYPsnxT8dm0Nyl1ssFkSduhcTBAog-821FbUumrdZiqg","commentsBeforeCount":null,"commentsBeforeCursor":null,"commentsIntentToken":"CHRONOLOGICAL_UNFILTERED_INTENT_V1","feedLocation":"GROUP_PERMALINK","focusCommentID":null,"scale":1,"useDefaultActor":false,"id":"ZmVlZGJhY2s6MjM5MDM2NzQ1MTE2MDEwNg=="}"""

        new_variables = json.loads(old_variables)
        new_variables["id"] = feedback_id

        if not is_primary:
            new_variables["commentsAfterCursor"] = cursor

        body["variables"] = json.dumps(new_variables)

        if is_primary:
            body["fb_api_req_friendly_name"] = "CommentListComponentsRootQuery"
            body["doc_id"] = 24442488642063884
        else:
            body["fb_api_req_friendly_name"] = "CommentsListComponentsPaginationQuery"
            body["doc_id"] = 7114405888582562

        del body["__req"]

        return urlencode(body)

    def __del__(self):
        print("Saving cursor...", end=" ")

        with open("cursor.txt", "w") as f:
            f.write(self.cursor)

        print("done!")

        print("Shutting down driver...", end=" ")

        self.driver.quit()

        print("done!")
