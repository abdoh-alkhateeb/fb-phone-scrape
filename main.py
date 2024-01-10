import json
from seleniumwire import webdriver

from facebook_scraper import FacebookScraper


with open("config.json", "r", encoding="ascii") as f:
    config = json.load(f)


options = webdriver.ChromeOptions()
options.add_argument("--incognito")
options.add_argument("--headless")
options.add_argument("--remote-debugging-port=9222")
options.add_argument("--disable-extensions")
options.add_argument("--disable-plugins-discovery")
options.binary_location = config["CHROME_BINARY"]


def main():
    scraper = FacebookScraper(options, config)
    scraper.run()


if __name__ == "__main__":
    main()
