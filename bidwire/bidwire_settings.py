import os

from bid import Bid
from document import Document
from notice import Notice
from notifiers.cityofboston_notifier import CityOfBostonNotifier, CityOfBostonNoticeNotifier
from notifiers.commbuys_notifier import CommBuysNotifier
from notifiers.massgov_notifier import MassGovNotifier
from notifiers.memphis_council_calendar_notifier import MemphisCouncilCalNotifier
from scrapers.cityofboston_scraper import CityOfBostonScraper
from scrapers.commbuys_scraper import CommBuysScraper
from scrapers.massgov_eopss_scraper import MassGovEOPSSScraper
from scrapers.memphis_council_calendar_scraper import MemphisCouncilCalScraper


POSTGRES_ENDPOINT = os.environ.get('POSTGRES_ENDPOINT', 'localhost')
SENDGRID_API_KEY = os.environ.get('SENDGRID_API_KEY')
DEBUG_EMAIL = os.environ.get('DEBUG_EMAIL', 'bidwire-logs@googlegroups.com')
ADMIN_EMAIL = "bidwire-admin@googlegroups.com"


def get_recipients_list(env_var_name, default_recipients='bidwire-logs@googlegroups.com'):
    """Extracts and parses a list of email address from the given env variable.

    Arguments:
    env_var_name -- string with the name of the environment variable to use to
        load recipient list; env variable should contain comma-separated list of
        email addresses
    default_recipients (optional) -- the comma-separated list of emails to use if
        no env variable can be found
    """
    recipients_str = os.environ.get(env_var_name, default_recipients)
    # Split into array of strings and strip whitespace.
    return [r.strip() for r in recipients_str.split(',')]

# List of e-mail recipients. Array of e-mail addresses.
EMAIL_RECIPIENTS = get_recipients_list('EMAIL_RECIPIENTS')

# List of e-mail recipients for MEMPHIS_COUNCIL_CALENDAR
MEMPHIS_COUNCIL_CALENDAR_RECIPIENTS = get_recipients_list('MEMPHIS_COUNCIL_CAL_RECIPIENTS')

# A dictionary representing which scrapers, notifiers and recipients to
# use for each site
SITE_CONFIG = {
    Bid.Site.COMMBUYS: {
        'scraper': CommBuysScraper(),
        'notifier': CommBuysNotifier(),
        'recipients': EMAIL_RECIPIENTS
    },
    Bid.Site.CITYOFBOSTON: {
        'scraper': CityOfBostonScraper(),
        'notifier': CityOfBostonNotifier(),
        'recipients': EMAIL_RECIPIENTS
    },
    Notice.Site.BOSTON: {
        'scraper': CityOfBostonScraper(),
        'notifier': CityOfBostonNoticeNotifier(),
        'recipients': EMAIL_RECIPIENTS
    },
    Document.Site.MASSGOV_EOPSS: {
        'scraper': MassGovEOPSSScraper(),
        'notifier': MassGovNotifier(),
        'recipients': EMAIL_RECIPIENTS
    },
    Document.Site.MEMPHIS_COUNCIL_CALENDAR: {
        'scraper': MemphisCouncilCalScraper(),
        'notifier': MemphisCouncilCalNotifier(),
        'recipients': MEMPHIS_COUNCIL_CALENDAR_RECIPIENTS
    }
}
