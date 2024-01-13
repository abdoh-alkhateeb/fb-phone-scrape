import json
import traceback
from seleniumwire import webdriver
from facebook_scraper import FacebookScraper


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


def main():
    keep_working = True
    while keep_working:
        scraper = FacebookScraper(options, config)

        try:
            scraper.run()
        except KeyboardInterrupt:
            keep_working = False
        except Exception:
            traceback.print_exc()
        finally:
            scraper.cleanup()


if __name__ == "__main__":
    main()
