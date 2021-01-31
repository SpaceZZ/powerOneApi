import logging
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication
from datetime import datetime
from datetime import timedelta

"""
Classes and functions for rendering, formatting and sending the recipes through the email.
"""


class EmailSender:
    """
    Class to send HTML email with the recipes.
    Class initializes with the user and password for the email account, together with the list of recipents
    """

    def __init__(self, email, password, recipients):
        self.email_user = email
        self.password = password
        self.recipients = recipients.split(",")

    def send(self, data):
        """
        Method builds and sends the email with the menu
        :return:
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
            logging.info("Email has been sent!")

        except Exception as e:
            logging.exception("There was an issue with sending an email")

    def render_body(self, data):
        """
        Method renders the HTML based body of the email
        :param data:
        :return:
        """
        body = data

        msg = MIMEMultipart()
        msg["From"] = self.email_user
        msg["To"] = ", ".join(self.recipients)
        msg["Subject"] = "Kapalkowo - produkcja z paneli PV | {}".format(
            datetime.date(datetime.now())
        )
        body = MIMEText(data, "html")
        msg.attach(body)

        return msg
