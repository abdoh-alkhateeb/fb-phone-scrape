import json
import traceback
from facebook_scraper import FacebookScraper

def main():
    keep_working = True
    while keep_working:
        scraper = FacebookScraper()

        try:
            scraper.run()
        except Exception:
            traceback.print_exc()
        except:
            keep_working = False
        finally:
            scraper.cleanup()


if __name__ == "__main__":
    main()
