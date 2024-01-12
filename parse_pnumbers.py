import os
import re
import json


def has_8_or_more_digits(input_string):
    return sum(char.isdigit() for char in input_string) >= 8


def find_brk_digit_position(input_string):
    digit_count = 0
    limit = 11
    for i, char in enumerate(input_string):
        if char.isdigit():
            digit_count += 1
            if digit_count == 1 and (char == "7" or char == "9"):
                limit = 8

        if digit_count == limit:
            return True, i

    return False, i


def remove_non_digits(input_string):
    return re.sub(r"\D", "", input_string)


def parse(input_string):
    matches = re.findall(r"[^a-zA-Z]{8,}", input_string)
    matches = [match for match in matches if has_8_or_more_digits(match)]

    broken_matches = []
    for match in matches:
        has_brk_digits, i = find_brk_digit_position(match)
        if has_brk_digits:
            broken_matches.append(match[:i + 1])
            broken_matches.append(match[i + 1:])
        else:
            broken_matches.append(match)

    matches = [remove_non_digits(match) for match in broken_matches if has_8_or_more_digits(match)]

    results = []
    for match in matches:
        if match.startswith(("3", "7", "9")):
            result = "+356" + (match[3:] if match.startswith("356") else match[:8])
            results.append(result)

    return results


def parse_post(post):
    results = []

    if post["text"]:
        results.extend(parse(post["text"]))

    for comment in post["comments"]:
        if comment[0]:
            results.extend(parse(comment[0]))

        for reply in comment[1]:
            if reply[0]:
                results.extend(parse(reply[0]))

            for subreply in reply[1]:
                if subreply:
                    results.extend(parse(subreply))

    return results


def read_files_in_directory(directory_path):
    file_names = [file_name for file_name in os.listdir(directory_path)]
    files = [json.load(open(os.path.join(directory_path, file_name), "r", encoding="utf-8")) for file_name in file_names]
    return files


def main():
    with open("config.json", "r", encoding="ascii") as f:
        DUMP_DIRECTORY = json.load(f)["DUMP_DIRECTORY"]

    posts = read_files_in_directory(DUMP_DIRECTORY)

    results = []
    for post in posts:
        results.extend(parse_post(post))

    for result in results:
        print(result)


if __name__ == "__main__":
    main()
