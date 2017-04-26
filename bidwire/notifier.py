import bid
from db import Session
from notifiers.cityofboston_notifier import CityOfBostonNotifier
from notifiers.commbuys_notifier import CommBuysNotifier
from notifiers.massgov_notifier import MassGovNotifier
from bidwire_settings import DEBUG_EMAIL

def send_new_bids_notifications(recipient_emails):
    """
    Sends new bids notifications for each site/notifier.

    For simplicity, we don't store the time of the last notification sent, and
    instead we rely on the fact that we notify once a day, and scrape at least
    once a day (but sometimes might scrape more than once, because we are
    testing the scrapers). So we retrieve the bids added to the database in the
    last 23 hours, which should include all new bids since the last notification
    (this is not perfect, and will miss new bids if a second scrape happened
    immediately after the previous notification went out). A more robust
    solution would involve storing a timestamp of the last check, and always
    checking against that timestamp.

    Return:
    new_bids_dict -- map from bid.site to list of new bids sent in notification
    """
    notifiers = [
        CityOfBostonNotifier(recipients=recipient_emails),
        CommBuysNotifier(recipients=recipient_emails),
        MassGovNotifier(recipients=[DEBUG_EMAIL]) # TODO: set to recipient_emails
    ]
    new_bids_dict = {}
    for notifier in notifiers:
        site = notifier.get_site()
        new_bids = bid.get_bids_from_last_n_hours(
            Session(), 23, notifier.get_site())
        if new_bids:
            notifier.send_new_bids_notification(new_bids)
        new_bids_dict[site] = new_bids
    return new_bids_dict
