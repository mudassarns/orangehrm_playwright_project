import smtplib
from email.message import EmailMessage
from config import Config


class GmailSender:

    def __init__(self):
        self.email_address = Config.get("GMAIL_ADDRESS")
        self.app_password = Config.get("GMAIL_APP_PASSWORD")

    def send_email(self, recipient, subject, body):
        with smtplib.SMTP("smtp.gmail.com", 587) as smtp:
            smtp.starttls()
            smtp.login(self.email_address, self.app_password)

            message = EmailMessage()
            message["From"] = self.email_address
            message["To"] = recipient
            message["Subject"] = subject
            message.set_content(body)

            smtp.send_message(message)
