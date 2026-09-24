import base64
import os
import time
import logging

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from config import Config
from google.auth.credentials import TokenState


logger = logging.getLogger(__name__)


class GmailReader:

    SCOPES = ["https://www.googleapis.com/auth/gmail.readonly"]

    def __init__(self):
        self.client_file = Config.get("GMAIL_OAUTH_CLIENT_FILE")
        self.token_file = Config.get("GMAIL_TOKEN_FILE")

    def _load_saved_credentials(self):
        if not os.path.exists(self.token_file):
            return None

        return Credentials.from_authorized_user_file(
            self.token_file,
            self.SCOPES,
        )

    def _refresh_credentials(self, credentials):
        credentials.refresh(Request())

        with open(self.token_file, "w") as token:
            token.write(credentials.to_json())

        return credentials

    def _get_credentials(self):
        credentials = self._load_saved_credentials()

        if credentials and credentials.token_state is TokenState.FRESH:
            return credentials

        if credentials and credentials.refresh_token:
            return self._refresh_credentials(credentials)

        flow = InstalledAppFlow.from_client_secrets_file(
            self.client_file,
            self.SCOPES,
        )

        credentials = flow.run_local_server(port=0)

        with open(self.token_file, "w") as token:
            token.write(credentials.to_json())

        return credentials

    def _build_service(self, credentials):
        return build(
            "gmail",
            "v1",
            credentials=credentials,
        )

    def find_messages(self, service, query):
        response = (
            service.users()
            .messages()
            .list(
                userId="me",
                q=query,
            )
            .execute()
        )

        return response.get("messages", [])

    def get_message(self, service, message_id):
        return (
            service.users()
            .messages()
            .get(
                userId="me",
                id=message_id,
            )
            .execute()
        )

    def get_header(self, message, header_name):
        for header in message["payload"]["headers"]:
            if header["name"].lower() == header_name.lower():
                return header["value"]

        return None

    def get_body(self, message):
        data = message["payload"]["body"].get("data")

        if not data:
            return ""

        return base64.urlsafe_b64decode(data).decode("utf-8")

    def wait_for_message(self, service, query, timeout=30, interval=2):
        end_time = time.time() + timeout

        while time.time() < end_time:
            messages = self.find_messages(service, query)

            if messages:
                return messages

            logger.info(
                "Message not found yet. Waiting %s seconds before polling again.",
                interval,
            )
            time.sleep(interval)

        raise TimeoutError(
            f"No Gmail message found within {timeout} seconds: {query}"
        )
