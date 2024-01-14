import json
import traceback
from kbhit import should_keep_working
from facebook_scraper import FacebookScraper

def main():
    no_terminal_exceptions = True
    while should_keep_working() and no_terminal_exceptions:
        scraper = FacebookScraper()
        try:
            scraper.run()
        except Exception:
            traceback.print_exc()
        except:
            no_terminal_exceptions = False
        finally:
            scraper.cleanup()


if __name__ == "__main__":
    main()
