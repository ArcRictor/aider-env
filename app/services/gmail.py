from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import Flow
from googleapiclient.discovery import build
from datetime import datetime
import base64
import email

class GmailService:
    SCOPES = ['https://www.googleapis.com/auth/gmail.readonly', 'https://www.googleapis.com/auth/userinfo.email']

    def __init__(self, credentials=None):
        self.credentials = credentials
        self.service = None if credentials is None else self._build_service()

    def _build_service(self):
        return build('gmail', 'v1', credentials=self.credentials)

    @staticmethod
    def create_flow(client_id, client_secret, redirect_uri):
        if not client_id or not client_secret:
            raise ValueError("Missing Gmail OAuth credentials. Check your .env file for GMAIL_CLIENT_ID and GMAIL_CLIENT_SECRET")
        
        flow = Flow.from_client_config(
            {
                "web": {
                    "client_id": client_id,
                    "client_secret": client_secret,
                    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                    "token_uri": "https://oauth2.googleapis.com/token",
                    "redirect_uris": [redirect_uri],
                    "javascript_origins": ["http://localhost:8000"]
                }
            },
            scopes=GmailService.SCOPES,
            redirect_uri=redirect_uri
        )
        return flow

    def get_recent_emails(self, max_results=10):
        if not self.service:
            raise ValueError("Service not initialized. Credentials required.")
        
        results = self.service.users().messages().list(
            userId='me', maxResults=max_results, labelIds=['INBOX']
        ).execute()

        messages = []
        if 'messages' in results:
            for message in results['messages']:
                email_data = self.service.users().messages().get(
                    userId='me', id=message['id'], format='full'
                ).execute()
                
                headers = email_data['payload']['headers']
                subject = next(h['value'] for h in headers if h['name'].lower() == 'subject')
                sender = next(h['value'] for h in headers if h['name'].lower() == 'from')
                date = next(h['value'] for h in headers if h['name'].lower() == 'date')

                # Get email body
                if 'parts' in email_data['payload']:
                    parts = email_data['payload']['parts']
                    data = parts[0]['body'].get('data', '')
                else:
                    data = email_data['payload']['body'].get('data', '')

                body = base64.urlsafe_b64decode(data.encode('ASCII')).decode('utf-8')

                messages.append({
                    'message_id': message['id'],
                    'subject': subject,
                    'sender': sender,
                    'received_at': datetime.strptime(date, '%a, %d %b %Y %H:%M:%S %z'),
                    'content': body
                })

        return messages
