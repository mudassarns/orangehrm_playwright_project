import uuid

from config import Config
from email_service.gmail_reader import GmailReader
from email_service.gmail_sender import GmailSender


def test_send_and_verify_gmail_email():
    email_address = Config.get("GMAIL_ADDRESS")

    run_id = uuid.uuid4().hex
    subject = f"Playwright Gmail Verification | {run_id}"
    body = f"Email verification test body | {run_id}"

    sender = GmailSender()

    sender.send_email(
        email_address,
        subject,
        body,
    )

    reader = GmailReader()
    credentials = reader._get_credentials()
    service = reader._build_service(credentials)

    messages = reader.wait_for_message(
        service,
        f'to:{email_address} subject:"{subject}"',
    )

    assert messages

    message = reader.get_message(
        service,
        messages[0]["id"],
    )

    assert reader.get_header(message, "From") == email_address
    assert reader.get_header(message, "To") == email_address
    assert reader.get_header(message, "Subject") == subject
    assert reader.get_body(message).strip() == body
