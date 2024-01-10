import json
from urllib.parse import parse_qs, urlencode
from seleniumwire.utils import decode


def extract_graphql_objects_from_requests(driver):
    for request in driver.requests:
        if "graphql" not in request.url:
            continue

        body = decode(request.response.body, request.response.headers.get(
            "Content-Encoding", "identity")).decode()

        if "GroupsCometFeedRegularStories_paginationGroup" not in body:
            continue

        return request, [json.loads(line) for line in body.split("\n")]


def update_fetch_post_body(body, new_cursor):
    body = parse_qs(body)
    body = {k: v[0] for k, v in body.items()}

    old_variables = body["variables"]

    new_variables = json.loads(old_variables)
    new_variables["cursor"] = new_cursor

    body["variables"] = json.dumps(new_variables)

    return urlencode(body)


def process_extracted_graphql_objects(request, objects, last_cursor):
    for obj in objects:
        if not obj.get("label") or "page_info" not in obj["label"]:
            continue

        if last_cursor:
            body = update_fetch_post_body(request.body.decode(), last_cursor)
        else:
            body = request.body.decode()

        return body


def fetch_posts(driver, body, template, group_id):
    request = template.replace(
        '"body": ""',
        f'"body": "{body}"').replace(
            '"referrer": ""',
            f'"referrer": "https://www.facebook.com/groups/{group_id}"')

    response = driver.execute_script(request)

    objects = [json.loads(line) for line in response.split("\n")]

    nodes = []

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

        nodes.append(node)

    return nodes, new_cursor


def update_main_fetch_comment_body(body, feedback_id):
    body = parse_qs(body)
    body = {k: v[0] for k, v in body.items()}

    old_variables = """{"commentsIntentToken":"CHRONOLOGICAL_UNFILTERED_INTENT_V1","feedLocation":"DEDICATED_COMMENTING_SURFACE","feedbackSource":110,"focusCommentID":null,"scale":1,"useDefaultActor":false,"id":"ZmVlZGJhY2s6NzQ1MDIyNzkzMTY5NDkzNg=="}"""
    new_variables = json.loads(old_variables)
    new_variables["id"] = feedback_id

    body["variables"] = json.dumps(new_variables)
    body["fb_api_req_friendly_name"] = "CommentListComponentsRootQuery"
    body["doc_id"] = 24442488642063884
    del body["__req"]

    return urlencode(body)


def update_secondary_fetch_comment_body(body, feedback_id, new_cursor):
    body = parse_qs(body)
    body = {k: v[0] for k, v in body.items()}

    old_variables = """{"commentsAfterCount":-1,"commentsAfterCursor":"AQHRcUzPl7NxbfxJnMXQs4HcVjZkY91QnGfoybTKnDJyRRUYPsnxT8dm0Nyl1ssFkSduhcTBAog-821FbUumrdZiqg","commentsBeforeCount":null,"commentsBeforeCursor":null,"commentsIntentToken":"CHRONOLOGICAL_UNFILTERED_INTENT_V1","feedLocation":"GROUP_PERMALINK","focusCommentID":null,"scale":1,"useDefaultActor":false,"id":"ZmVlZGJhY2s6MjM5MDM2NzQ1MTE2MDEwNg=="}"""
    new_variables = json.loads(old_variables)
    new_variables["id"] = feedback_id
    new_variables["commentsAfterCursor"] = new_cursor

    body["variables"] = json.dumps(new_variables)
    body["fb_api_req_friendly_name"] = "CommentsListComponentsPaginationQuery"
    body["doc_id"] = 7114405888582562
    del body["__req"]

    return urlencode(body)


def fetch_comments(driver, body, template, feedback_id, group_id):
    _body = update_main_fetch_comment_body(
        body, feedback_id)

    request = template.replace(
        '"body": ""',
        f'"body": "{_body}"'
    ).replace(
        '"referrer": ""',
        f'"referrer": "https://www.facebook.com/groups/{group_id}"'
    ).replace(
        '"x-fb-friendly-name": ""',
        '"x-fb-friendly-name": "CommentListComponentsRootQuery"'
    )

    response = driver.execute_script(request)

    data = [json.loads(line)for line in response.split("\n")][0]

    data = data["data"]["node"]["comment_rendering_instance_for_feed_location"]["comments"]

    comments = [edge["node"]["body"] for edge in data["edges"]]

    comments = [item.get("text")
                for item in comments if item is not None]

    while data["page_info"].get("has_next_page"):
        _body = update_secondary_fetch_comment_body(
            body, data["page_info"]["end_cursor"], feedback_id)

        request = template.replace(
            '"body": ""',
            f'"body": "{_body}"'
        ).replace(
            '"referrer": ""',
            f'"referrer": "https://www.facebook.com/groups/{group_id}"'
        ).replace(
            '"x-fb-friendly-name": ""',
            '"x-fb-friendly-name": "CommentsListComponentsPaginationQuery"'
        )

        response = driver.execute_script(request)

        data = [json.loads(line)for line in response.split("\n")][0]

        if not data["data"].get("node"):
            break

        data = data["data"]["node"]["comment_rendering_instance_for_feed_location"]["comments"]

        comments.extend([edge["node"]["body"].get("text")
                        for edge in data["edges"] if edge["node"]["body"] is not None])

    return comments
