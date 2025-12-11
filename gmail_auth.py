#!/usr/bin/env python3
"""
Gmail OAuth 2.0 authentication module.
Handles the OAuth flow and token management for Gmail API access.
"""

from pathlib import Path
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

# Gmail API scopes
SCOPES = [
    'https://www.googleapis.com/auth/gmail.readonly',
    'https://www.googleapis.com/auth/gmail.compose',
    'https://www.googleapis.com/auth/gmail.modify',
    'https://www.googleapis.com/auth/gmail.send'
]

# Get the directory where this script is located
SCRIPT_DIR = Path(__file__).parent.absolute()

# File paths for credentials and tokens (use absolute paths)
CREDENTIALS_FILE = SCRIPT_DIR / 'credentials.json'
TOKEN_FILE = SCRIPT_DIR / 'token.json'


def get_gmail_service():
    """
    Authenticate and return a Gmail API service instance.

    On first run:
    - Opens browser for user authorization
    - Saves refresh token to token.json for future use

    On subsequent runs:
    - Loads existing tokens from token.json
    - Automatically refreshes access token if expired

    Returns:
        googleapiclient.discovery.Resource: Authenticated Gmail API service

    Raises:
        FileNotFoundError: If credentials.json is not found
        Exception: If authentication fails
    """
    creds = None

    # Check if we have saved tokens
    if TOKEN_FILE.exists():
        try:
            creds = Credentials.from_authorized_user_file(str(TOKEN_FILE), SCOPES)
        except Exception as e:
            print(f"Error loading saved credentials: {e}", file=__import__('sys').stderr)
            creds = None

    # If there are no (valid) credentials available, let the user log in
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            # Refresh the access token
            try:
                creds.refresh(Request())
                print("Access token refreshed successfully", file=__import__('sys').stderr)
            except Exception as e:
                print(f"Error refreshing token: {e}", file=__import__('sys').stderr)
                # If refresh fails, re-authenticate
                creds = None

        if not creds:
            # No valid credentials, need to authenticate
            if not CREDENTIALS_FILE.exists():
                raise FileNotFoundError(
                    f"\n\n❌ {CREDENTIALS_FILE} not found!\n\n"
                    "Please download your OAuth 2.0 credentials from Google Cloud Console:\n"
                    "1. Go to https://console.cloud.google.com/\n"
                    "2. Select your project\n"
                    "3. Go to 'APIs & Services' > 'Credentials'\n"
                    "4. Download the OAuth 2.0 Client ID credentials\n"
                    "5. Save as 'credentials.json' in this directory\n"
                )

            # Run the OAuth flow
            flow = InstalledAppFlow.from_client_secrets_file(
                str(CREDENTIALS_FILE), SCOPES
            )

            # This will open a browser window for authorization
            creds = flow.run_local_server(
                port=0,
                success_message='Authorization successful! You can close this window.',
                open_browser=True
            )

            print("✓ Authorization successful!", file=__import__('sys').stderr)

        # Save the credentials for the next run
        with open(TOKEN_FILE, 'w') as token:
            token.write(creds.to_json())
        print(f"✓ Credentials saved to {TOKEN_FILE}", file=__import__('sys').stderr)

    # Build and return the Gmail service
    service = build('gmail', 'v1', credentials=creds)
    return service


def revoke_credentials():
    """
    Revoke the current credentials and delete token file.
    Useful for switching accounts or troubleshooting.
    """
    if TOKEN_FILE.exists():
        try:
            creds = Credentials.from_authorized_user_file(str(TOKEN_FILE), SCOPES)
            if creds and creds.valid:
                creds.revoke(Request())
                print("✓ Credentials revoked")
        except Exception as e:
            print(f"Error revoking credentials: {e}")

        TOKEN_FILE.unlink()
        print(f"✓ {TOKEN_FILE} deleted")
    else:
        print(f"{TOKEN_FILE} not found")


if __name__ == "__main__":
    """
    Test the authentication flow.
    Run this script directly to verify OAuth setup.
    """
    import sys

    if len(sys.argv) > 1 and sys.argv[1] == 'revoke':
        revoke_credentials()
    else:
        print("Testing Gmail OAuth authentication...")
        print(f"Required scopes: {', '.join(SCOPES)}\n")

        try:
            service = get_gmail_service()

            # Test the connection by getting user profile
            profile = service.users().getProfile(userId='me').execute()
            email_address = profile.get('emailAddress')

            print(f"\n✓ Successfully authenticated!")
            print(f"✓ Connected to: {email_address}")
            print(f"✓ Total messages: {profile.get('messagesTotal', 0)}")
            print(f"✓ Total threads: {profile.get('threadsTotal', 0)}")
            print(f"\nYou can now use the Gmail API in your application.")

        except FileNotFoundError as e:
            print(str(e))
            sys.exit(1)
        except Exception as e:
            print(f"\n❌ Authentication failed: {e}")
            sys.exit(1)
