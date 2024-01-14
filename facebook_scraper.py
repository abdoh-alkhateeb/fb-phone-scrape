import os
import json
import pickle
from time import sleep
from urllib.parse import parse_qs, urlencode
from seleniumwire import webdriver
from seleniumwire.utils import decode
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common import exceptions
from kbhit import should_keep_working

class FacebookScraper:
    def __init__(self):
        with open("config.json", "r", encoding="ascii") as f:
            config = json.load(f)

        options = webdriver.ChromeOptions()
        options.add_argument("--incognito")
        options.add_argument("--headless")
        options.add_argument("--no-sandbox")
        options.add_argument("--remote-debugging-port=9222")
        options.add_argument("--disable-extensions")
        options.add_argument("--disable-plugins-discovery")
        options.binary_location = config["CHROME_BINARY"]

        self.dump_file = open("dump.txt", "a", encoding="ascii")
        self.driver = webdriver.Chrome(options=options)

        self.email = config["FB_EMAIL"]
        self.password = config["FB_PASSWORD"]
        self.group_id = config["FB_GROUP_ID"]
        self.dump_directory = config["DUMP_DIRECTORY"]

        self.cursor = ""
        self.fetch_template = None

        self.request = None
        self.body = None

        self.has_posts = True

        print("Initializing...")

        self.load_cursor()
        self.load_fetch_template()
        self.setup_dump_directory()


        print("Preparing group...")

        self.login()
        self.prepare_group()

        print("Done!")

    def load_cookies(self):
        try:
            with open("cookies.pkl", "rb") as f:
                cookies = pickle.load(f)
                for cookie in cookies:
                    self.driver.add_cookie(cookie)
                print("Cookies loaded...")
        except FileNotFoundError:
            pass

    def load_cursor(self):
        try:
            with open("cursor.txt", "r", encoding="ascii") as f:
                self.cursor = f.read()
                print("Cursor loaded...")
        except FileNotFoundError:
            pass

    def load_fetch_template(self):
        with open("fetch_template.js", "r", encoding="utf-8") as f:
            self.fetch_template = f.read()

    def setup_dump_directory(self):
        os.makedirs(self.dump_directory, exist_ok=True)

    def login(self):
        self.driver.get("https://www.facebook.com/robots.txt")
        self.load_cookies()

        self.driver.get("https://www.facebook.com")

        wait = WebDriverWait(self.driver, 30)

        try:
            xpath = "/html/body/div[3]/div[2]/div/div/div/div/div[4]/button[2]"
            allow_cookies = wait.until(EC.visibility_of_element_located((By.XPATH, xpath)))
            allow_cookies.click()
        except exceptions.WebDriverException:
            pass

        try:
            # Already logged in
            wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, "svg[aria-label='Your profile']")))
            print("Already logged in...")
            return
        except exceptions.WebDriverException:
            pass

        email = wait.until(EC.visibility_of_element_located((By.NAME, "email")))
        email.send_keys(self.email)

        password = wait.until(EC.visibility_of_element_located((By.NAME, "pass")))
        password.send_keys(self.password)
        
        button = wait.until(EC.visibility_of_element_located((By.XPATH, "//button[@data-testid='royal_login_button']")))
        button.click()
        
        wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, "svg[aria-label='Your profile']")))
        print("Login successful...")

    def prepare_group(self):
        sleep(5)

        self.driver.get(f"https://www.facebook.com/groups/{self.group_id}")

        sleep(5)

        wait = WebDriverWait(self.driver, 30)

        selector = ".xzt5al7 > div:nth-child(1) > h2:nth-child(1) > span:nth-child(1) > span:nth-child(1)"
        anchor = wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, selector)))
        anchor.click()

        selector = "div.x1i10hfl:nth-child(3) > div:nth-child(1) > div:nth-child(1) > div:nth-child(1) > span:nth-child(1)"
        anchor = wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, selector)))
        anchor.click()

        sleep(5)

    def run(self):
        initial_response = self.extract_initial_graphql_request()
        initial_nodes = self.prepare_initial_fetch_request_body(initial_response)

        try:
            count = 0

            for node in initial_nodes:
                self.scrape_post_node(node)
                self.dump_file.write(node["post_id"] + "\n")
                count += 1

            os.system("cls") if os.name == "nt" else os.system("clear")
            print(f"Scraped posts count (current session only): {count}")

            sleep(5)

            while self.has_posts and should_keep_working():
                post_nodes = self.fetch_posts()
                for node in post_nodes:
                    self.scrape_post_node(node)
                    self.dump_file.write(node["post_id"] + "\n")
                    last_post_id = node["post_id"]
                    count += 1

                os.system("cls") if os.name == "nt" else os.system("clear")
                print(f"Scraped posts count (current session only): {count} https://www.facebook.com/groups/{self.group_id}/posts/{last_post_id}")

                sleep(4)
        except json.JSONDecodeError:
            print("Response empty or unsupported. Exiting...")

    def extract_initial_graphql_request(self):
        for request in self.driver.requests:
            if "graphql" not in request.url:
                continue

            body = decode(request.response.body, request.response.headers.get("Content-Encoding", "identity")).decode()

            if "GroupsCometFeedRegularStories_paginationGroup" not in body:
                continue

            if '{"data":{"group":{"if_viewer_can_see_expanded_color":' not in body:
                continue

            self.request = request
            return body

    def prepare_initial_fetch_request_body(self, initial_response):
        if self.cursor:
            self.body = FacebookScraper.generate_fetch_posts_body(self.request.body.decode(), self.cursor, self.group_id)
            return []
        else:
            response = initial_response

            objects = [json.loads(line) for line in response.split("\n")]

            nodes = []

            for obj in objects:
                if obj.keys() == {"data", "extensions"}:
                    continue
                elif obj.keys() == {"label", "path", "data", "extensions"}:
                    if "page_info" in obj["label"]:
                        self.cursor = obj["data"]["page_info"]["end_cursor"]
                        self.has_posts = obj["data"]["page_info"]["has_next_page"]
                        self.body = FacebookScraper.generate_fetch_posts_body(self.request.body.decode(), self.cursor, self.group_id)
                        continue
                    try:
                        node = obj["data"]["node"]
                    except KeyError:
                        continue
                else:
                    continue

                nodes.append(node)

            return nodes

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
                    self.has_posts = obj["data"]["page_info"]["has_next_page"]
                    self.body = FacebookScraper.generate_fetch_posts_body(self.body, self.cursor, self.group_id)
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
    def generate_fetch_posts_body(body, cursor, group_id):
        body = parse_qs(body)
        body = {k: v[0] for k, v in body.items()}

        old_variables = """{"UFI2CommentsProvider_commentsKey":"CometGroupDiscussionRootSuccessQuery","count":3,"cursor":"","displayCommentsContextEnableComment":null,"displayCommentsContextIsAdPreview":null,"displayCommentsContextIsAggregatedShare":null,"displayCommentsContextIsStorySet":null,"displayCommentsFeedbackContext":null,"feedLocation":"GROUP","feedType":"DISCUSSION","feedbackSource":0,"focusCommentID":null,"privacySelectorRenderLocation":"COMET_STREAM","renderLocation":"group","scale":1,"sortingSetting":"CHRONOLOGICAL","stream_initial_count":1,"useDefaultActor":false,"id":"","__relay_internal__pv__IsWorkUserrelayprovider":false,"__relay_internal__pv__IsMergQAPollsrelayprovider":false,"__relay_internal__pv__CometUFIReactionsEnableShortNamerelayprovider":false,"__relay_internal__pv__CometUFIIsRTAEnabledrelayprovider":false,"__relay_internal__pv__StoriesArmadilloReplyEnabledrelayprovider":false,"__relay_internal__pv__StoriesRingrelayprovider":false}"""

        new_variables = json.loads(old_variables)
        new_variables["cursor"] = cursor
        new_variables["id"] = group_id

        body["variables"] = json.dumps(new_variables)
        body["doc_id"] = 6473278959439311

        return urlencode(body)

    def scrape_post_node(self, post_node):
        dump_file_name = os.path.join(self.dump_directory, post_node["post_id"])
        with open(f"{dump_file_name}.json", "w", encoding="utf-8") as dump_file:
            _id = post_node["post_id"]

            story = post_node["comet_sections"]["content"]["story"]

            try:
                text = story["message"]["text"]
            except TypeError:
                text = ""

            try:
                comment_nodes = self.fetch_comments(story["feedback"]["id"])
                comments = [self.scrape_comment_node(node) for node in comment_nodes]
            except KeyError:
                comments = []

            json.dump({"id": _id, "text": text, "comments": comments}, dump_file, indent=4, ensure_ascii=False)

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

        nodes = [edge["node"] for edge in data["edges"]]

        while data["page_info"]["has_next_page"]:
            body = FacebookScraper.generate_fetch_comments_body(self.body, feedback_id, data["page_info"]["end_cursor"], False)

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

            nodes.extend([edge["node"] for edge in data["edges"]])

        return nodes

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

    def scrape_comment_node(self, comment_node):
        comment_text = comment_node["body"].get("text") if comment_node["body"] is not None else None

        if comment_node["feedback"]["replies_fields"]["count"] == 0:
            return [comment_text, []]

        depth1_reply_nodes = self.fetch_replies(comment_node["feedback"]["id"], comment_node["feedback"]["expansion_info"]["expansion_token"], 1)
        depth2_reply_nodes = [self.fetch_replies(node["feedback"]["id"], node["feedback"]["expansion_info"]["expansion_token"], 2)
                              if node["feedback"]["replies_fields"]["count"] != 0 else [] for node in depth1_reply_nodes]

        depth1_replies = [node["body"].get("text") if node["body"] is not None else None for node in depth1_reply_nodes]
        depth2_replies = [[node["body"].get("text") if node["body"] is not None else None for node in nodes] for nodes in depth2_reply_nodes]

        replies = []
        for i, reply in enumerate(depth1_replies):
            replies.append([reply, depth2_replies[i]])

        return [comment_text, replies]

    def fetch_replies(self, feedback_id, expansion_token, depth=1):
        body = FacebookScraper.generate_fetch_replies_body(self.body, feedback_id, expansion_token, None, depth)

        request = self.fetch_template.replace(
            '"body": ""',
            f'"body": "{body}"'
        ).replace(
            '"referrer": ""',
            f'"referrer": "https://www.facebook.com/groups/{self.group_id}"'
        ).replace(
            '"x-fb-friendly-name": ""',
            f'"x-fb-friendly-name": "Depth{depth}CommentsListPaginationQuery"'
        )

        response = self.driver.execute_script(request)

        data = [json.loads(line)for line in response.split("\n")][0]
        data = data["data"]["node"]["replies_connection"]

        nodes = [edge["node"] for edge in data["edges"]]

        while data["page_info"]["has_next_page"]:
            body = FacebookScraper.generate_fetch_replies_body(self.body, feedback_id, expansion_token, data["page_info"]["end_cursor"], depth)

            request = self.fetch_template.replace(
                '"body": ""',
                f'"body": "{body}"'
            ).replace(
                '"referrer": ""',
                f'"referrer": "https://www.facebook.com/groups/{self.group_id}"'
            ).replace(
                '"x-fb-friendly-name": ""',
                f'"x-fb-friendly-name": "Depth{depth}CommentsListPaginationQuery"'
            )

            response = self.driver.execute_script(request)

            data = [json.loads(line)for line in response.split("\n")][0]
            data = data["data"]["node"]["replies_connection"]

            nodes.extend([edge["node"] for edge in data["edges"]])

        return nodes

    @staticmethod
    def generate_fetch_replies_body(body, feedback_id, expansion_token, cursor=None, depth=1):
        body = parse_qs(body)
        body = {k: v[0] for k, v in body.items()}

        if depth == 1:
            old_variables = """{"clientKey":null,"expansionToken":"MjoxNzA0OTcyOTk4OgF1phklzHy84B3QJqTAp2FDAr15CEd527P9nTNmJt7zv-0sfRiesqbpS5qRisVjFrBJdgp8zev8fkz9tTPXrYhME6lYV9OcfcE95c5DwAYvCwws75fhYHshj_rBSlIyCgH4UI95fbSni2WduhTpPfJAWX7Cj2T6XQ-kGbiPj_lZaEVQbd2hFRuQ6zs0RapFHWXQiAhH8lZ8E93T9D-iby1PMLxJ1_XNAqcyCqMRIpyCV3XyvaHsnfPI5jhUGPRoLQXhHUUW1m_47h1fIsFfLpBczzSy0imD49va1k7ab0g_NfOsdi6nEccAg6h623KIz5f0V91ZRaPa5xnWwc1Ida5L0KSTBZNSMr1k3GgtLkMyXRql7G0cc1Uyr8MAH_lNaxXGX4vF63KCIutT9njG9S78yW5trrqCm9-jAVx59KvnvQy0O_TVuna5lQA7on4jVujhCajrm9OBJ7Np7KA6hgqT3s4lcsxxjBnfx32Ru1PTgou-PPuQe8EraUtKZjxaRh81rDCjRBzjRjRDMj4","feedLocation":"DEDICATED_COMMENTING_SURFACE","focusCommentID":null,"repliesAfterCount":null,"repliesAfterCursor":null,"repliesBeforeCount":null,"repliesBeforeCursor":null,"scale":1,"useDefaultActor":false,"id":"ZmVlZGJhY2s6MjM5MTY1MDQzNzY5ODQ3NF8yMzkxNjY4MTM3Njk2NzA0"}"""
        else:
            old_variables = """{"clientKey":null,"expansionToken":"MjoxNzA0OTczMDE0OgF1Z2aoq0KQ3_g9VYA_R7_0RuJpokaVb0xZN5cJgXQcaO7DBvQWanu3JCk198otElCIvHIoXWifnmfEMXFqnX4ubALx33HduRsr7ySYcnx3d-LWtgHYT79hIpK0yy5rO_R3p_-fluVWk9IG6MBb06Bu01Zaf_Ayn8BPBEz58MrAUwOgOpqAmht9_3BZtyAfVVnA0hBbIvTa5L5FIouH-OdYS6qL_aD4dbvI6x8yaLwTciy7sHefAu9a369hRaVFASFs1VUKt5i_-jm7ijCiiLNz_lwAJB4CJENIU10Qc39MGhzPD8H4W-1lvPwVWGD_VlQ1GzFjIkky-hKJm2PP5qYjkdInmEzrsuWd6TkpuWL3nomav-civwnCV7qN-lOqkTuaG5A6WbPXM2aMG66n6f1xlsl0g_7zzEK9P-Lu2VxsDZ3Wh8-56gic8R1V2MgdVdu5sahLDJKutt2lybQBZlrl17cUZLdqZUpio2COfQqdYKcenn4OS6fDRRPjSTtJ_Joc20XCcbHmjF97OV8","feedLocation":"DEDICATED_COMMENTING_SURFACE","scale":1,"subRepliesAfterCount":null,"subRepliesAfterCursor":null,"subRepliesBeforeCount":null,"subRepliesBeforeCursor":null,"useDefaultActor":false,"id":"ZmVlZGJhY2s6MjM5MTY1MDQzNzY5ODQ3NF8yMzkxNjc0OTcxMDI5MzU0"}"""

        new_variables = json.loads(old_variables)
        new_variables["id"] = feedback_id
        new_variables["expansionToken"] = expansion_token

        if cursor:
            if depth == 1:
                new_variables["repliesAfterCursor"] = cursor
            else:
                new_variables["subRepliesAfterCursor"] = cursor

        body["variables"] = json.dumps(new_variables)

        if depth == 1:
            body["fb_api_req_friendly_name"] = "Depth1CommentsListPaginationQuery"
            body["doc_id"] = 6465084470259958
        else:
            body["fb_api_req_friendly_name"] = "Depth2CommentsListPaginationQuery"
            body["doc_id"] = 7479782038719631

        del body["__req"]

        return urlencode(body)

    def cleanup(self):
        print("Saving cursor...", end=" ")

        with open("cursor.txt", "w", encoding="ascii") as f:
            f.write(self.cursor)

        print("done!")
        
        print("Saving cookies...", end=" ")

        with open("cookies.pkl", "wb") as f:
            pickle.dump(self.driver.get_cookies(), f)

        print("done!")

        print("Shutting down driver...", end=" ")

        self.driver.quit()

        print("done!")
        
        self.dump_file.close()
