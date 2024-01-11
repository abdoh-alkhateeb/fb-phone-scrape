import os
import json
import traceback
from seleniumwire import webdriver
from facebook_scraper import FacebookScraper


with open("config.json", "r", encoding="ascii") as f:
    config = json.load(f)


options = webdriver.FirefoxOptions()
options.add_argument("--incognito")
options.add_argument("--headless")
options.add_argument("--no-sandbox")
options.add_argument("--disable-extensions")
options.add_argument("--disable-plugins-discovery")

os.makedirs("temp", exist_ok=True)
os.environ["TMPDIR"] = os.path.join(os.getcwd(), "temp")


def main():
    scraper = FacebookScraper(options, config)

    try:
        scraper.run()
    except KeyboardInterrupt:
        pass
    except Exception:
        traceback.print_exc()
    finally:
        scraper.cleanup()


if __name__ == "__main__":
    main()
