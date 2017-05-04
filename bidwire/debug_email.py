import sendgrid
from sendgrid.helpers.mail import *
from yattag import Doc

import bid
import document
import bidwire_settings
import db


class DebugEmail:
    def __init__(self, sg_client=None, db_session=None):
        """
        Arguments:
        sg_client (optional) -- SendgridAPIClient object to use for email
          sending; if not provided, one will be constructed using default settings
        session (optional) -- Database session to use for database operations;
          if not provided, a default one will be constructed
        """
        if not sg_client:
            self.sg_client = sendgrid.SendGridAPIClient(
                apikey=bidwire_settings.SENDGRID_API_KEY)
        else:
            self.sg_client = sg_client

        if db_session:
            self.db_session = db_session
        else:
            self.db_session = db.Session()

    def send(self, records_dict, recipients_notified, elapsed_secs):
        """Composes and sends the debug email.

        Arguments:
        records_dict -- {site: records} dictionary with new records we just sent
            notifications about
        recipients_notified -- list of strings with emails that received the
            notifications
        elapsed_secs -- integer number of seconds that elapsed between the
            beginning and the end of the entire Bidwire run
        """
        subject = "Bidwire status"
        content = Content(
            "text/html",
            self._make_content(records_dict,
                               recipients_notified,
                               elapsed_secs)
        )
        from_email = Email(bidwire_settings.ADMIN_EMAIL)
        to_email = Email(bidwire_settings.DEBUG_EMAIL)
        mail = Mail(from_email, subject, to_email, content)
        response = self.sg_client.client.mail.send.post(
            request_body=mail.get())

    def _make_content(self, records_dict, recipients_notified, elapsed_secs):
        doc, tag, text = Doc().tagtext()
        with tag('p'):
            text("New records found:")
            with tag('ul'):
                for site, records in records_dict.items():
                    with tag('li'):
                        text("{}: {} new records".format(site.value, len(records)))
        with tag('p'):
            obfuscated_emails = [self._obfuscate_email(
                e) for e in recipients_notified]
            text("For sites with new records, notifications were sent to {}".format(
                ", ".join(obfuscated_emails)))

        with tag('p'):
            text("Total time elapsed: {}m {}sec".format(int(elapsed_secs / 60),
                                                        elapsed_secs % 60))

        with tag('p'):
            text("Current database contents:")
            with tag('ul'):
                record_count = bid.get_bid_count_per_site(self.db_session)
                record_count.update(
                    document.get_doc_count_per_site(self.db_session))
                for site, count in record_count.items():
                    with tag('li'):
                        text("{}: {} total records".format(site.value, count))

        return doc.getvalue()

    def _obfuscate_email(self, email):
        parts = email.split("@")
        return "{}***@{}".format(parts[0][0], parts[1])
