from __future__ import print_function
import pickle
import os.path
import base64
import re
from typing import Tuple, Optional

from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

# If modifying these scopes, delete the file token.pickle.
SCOPES = ['https://www.googleapis.com/auth/gmail.readonly', 'https://www.googleapis.com/auth/gmail.modify']


class EmailVerifier:
    """Shows basic usage of the Gmail API.
    Lists the user's Gmail labels.
    """

    def __init__(self):
        creds = None
        # The file token.pickle stores the user's access and refresh tokens, and is
        # created automatically when the authorization flow completes for the first
        # time.
        if os.path.exists('../data/token.pickle'):
            with open('../data/token.pickle', 'rb') as token:
                creds = pickle.load(token)
        # If there are no (valid) credentials available, let the user log in.
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    '../data/credentials.json', SCOPES)
                creds = flow.run_local_server(port=0)
            # Save the credentials for the next run
            with open('../data/token.pickle', 'wb') as token:
                pickle.dump(creds, token)

        self.service = build('gmail', 'v1', credentials=creds)

    def getUnreadEmailLinks(self, identifier, max=10, days=1) -> Tuple[Optional[str], Optional[str]]:

        # request a list of all the messages
        result = self.service.users().messages().list(userId='me', labelIds=['UNREAD', 'INBOX', 'CATEGORY_UPDATES'],
                                                      q=f'newer_than:{days}d', maxResults=max).execute()
        messages = result.get('messages')
        # iterate through all the messages
        emailLinks = {}
        for msg in messages:
            # Get the message from its id
            txt = self.service.users().messages().get(userId='me', id=msg['id'], format="full").execute()
            # Use try-except to avoid any Errors

            try:
                # Get value of 'payload' from dictionary 'txt'
                payload = txt['payload']
                found_identifier = self.__getIdentifier(payload['headers'])

                if found_identifier == identifier:
                    # The Body of the message is in Encrypted format. So, we have to decode it.
                    # Get the data and decode it with base 64 decoder.
                    parts = payload.get('parts')[0]
                    data = parts['body']['data']
                    data = data.replace("-", "+").replace("_", "/")
                    decoded_data = base64.urlsafe_b64decode(data).decode('ascii')
                    regex = 'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+'

                    links = re.findall(regex, decoded_data)
                    keywords = ['verify', 'verification', 'accept', 'Verify']
                    for link in links:
                        if any(x in link for x in keywords):
                            return msg['id'], link
            except:
                pass
        return None, None

    def __getIdentifier(self, headers) -> Optional[str]:
        to_address = None
        for item in headers:
            if item['name'] == 'Delivered-To':
                to_address = item['value']
        identifier = re.findall('.*\+(.*)@.*', to_address)
        return identifier[0] if identifier else None

    def messagesRead(self, msgIds) -> None:
        if msgIds:
            msg_labels = {'removeLabelIds': ['UNREAD'], 'addLabelIds': [], 'ids': msgIds}
            self.service.users().messages().batchModify(userId='me', body=msg_labels).execute()

    def messageRead(self, msgId) -> None:
        msg_labels = {'removeLabelIds': ['UNREAD'], 'addLabelIds': []}
        self.service.users().messages().modify(userId='me', id=msgId, body=msg_labels).execute()

