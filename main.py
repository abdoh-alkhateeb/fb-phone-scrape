import json
import traceback
import signal
import shr
from facebook_scraper import FacebookScraper


def sigint_handler(sig, frame):
    print('Handled CTRL+C')
    shr.keep_working = False

def main():
    signal.signal(signal.SIGINT, sigint_handler)
    
    while shr.keep_working:
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
