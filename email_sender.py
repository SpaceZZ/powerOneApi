"""
Classes and functions for rendering, formatting and sending the daily PV report via email.
"""
import logging
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from datetime import datetime

logger = logging.getLogger(__name__)


class EmailSender:
    """
    Sends an HTML email report via Gmail SMTP.
    Initialised with the sender credentials and a comma-separated list of recipients.
    """

    def __init__(self, email, password, recipients):
        self.email_user = email
        self.password = password
        self.recipients = recipients.split(",")

    def send(self, data):
        """
        Builds and sends the HTML email.
        :param data: HTML string to embed as the email body
        """
        email_text = self.render_body(data)

        try:
            server = smtplib.SMTP_SSL("smtp.gmail.com", 465)
            server.ehlo()
            server.login(self.email_user, self.password)
            server.sendmail(
                from_addr=self.email_user,
                to_addrs=self.recipients,
                msg=email_text.as_string(),
            )
            server.close()
            logger.info("Email sent successfully to %s", self.recipients)

        except Exception:
            logger.exception("Failed to send email")

    def render_body(self, data):
        """
        Wraps the HTML body in a MIME email message.
        :param data: HTML string
        :return: MIMEMultipart message object
        """
        msg = MIMEMultipart()
        msg["From"] = self.email_user
        msg["To"] = ", ".join(self.recipients)
        msg["Subject"] = "Kapalkowo - produkcja z paneli PV | {}".format(
            datetime.date(datetime.now())
        )
        msg.attach(MIMEText(data, "html"))

        return msg
