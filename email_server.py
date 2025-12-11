#!/usr/bin/env python3

import asyncio
import os
import base64
from mcp.server.models import InitializationOptions
import mcp.types as types
from mcp.server import NotificationOptions, Server
import mcp.server.stdio
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import email
from email.header import decode_header
from email_reply_parser import EmailReplyParser
import anthropic
from gmail_auth import get_gmail_service


async def send_email(to: str, subject: str, body: str):
    """Send an email using Gmail API"""
    service = get_gmail_service()

    # Get the authenticated user's email
    profile = service.users().getProfile(userId='me').execute()
    email_user = profile['emailAddress']

    # Create message
    msg = MIMEMultipart()
    msg['From'] = email_user
    msg['To'] = to
    msg['Subject'] = subject
    msg.attach(MIMEText(body, 'plain'))

    # Encode the message
    raw_message = base64.urlsafe_b64encode(msg.as_bytes()).decode('utf-8')

    # Send via Gmail API
    message = service.users().messages().send(
        userId='me',
        body={'raw': raw_message}
    ).execute()

    return message['id']


def decode_mime_words(s):
    """Decode MIME encoded-word strings"""
    if s is None:
        return ""
    decoded_fragments = decode_header(s)
    return ''.join(
        str(fragment, encoding or 'utf-8') if isinstance(fragment, bytes) else str(fragment)
        for fragment, encoding in decoded_fragments
    )


async def get_unread_emails(max_emails: int = 10):
    """Fetch unread emails from Gmail via Gmail API"""
    service = get_gmail_service()

    # Search for unread messages in INBOX
    results = service.users().messages().list(
        userId='me',
        q='is:unread in:inbox',
        maxResults=max_emails
    ).execute()

    messages = results.get('messages', [])

    if not messages:
        return []

    emails = []
    for msg_info in messages:
        # Get full message details
        msg = service.users().messages().get(
            userId='me',
            id=msg_info['id'],
            format='full'
        ).execute()

        # Extract headers
        headers = {h['name']: h['value'] for h in msg['payload']['headers']}
        from_addr = headers.get('From', '')
        subject = headers.get('Subject', '')
        date = headers.get('Date', '')
        message_id = headers.get('Message-ID', '')

        # Extract email body
        body = ""
        if 'parts' in msg['payload']:
            # Multipart message
            for part in msg['payload']['parts']:
                if part['mimeType'] == 'text/plain':
                    if 'data' in part['body']:
                        body = base64.urlsafe_b64decode(
                            part['body']['data']
                        ).decode('utf-8')
                        break
        else:
            # Simple message
            if 'data' in msg['payload']['body']:
                body = base64.urlsafe_b64decode(
                    msg['payload']['body']['data']
                ).decode('utf-8')

        # Parse reply using email_reply_parser
        parsed_body = EmailReplyParser.parse_reply(body)

        emails.append({
            'id': msg_info['id'],
            'message_id': message_id,
            'from': from_addr,
            'subject': subject,
            'date': date,
            'body': parsed_body,
            'full_body': body
        })

    return emails


async def generate_draft_reply(email_content: dict, tone: str = "professional", additional_context: str = ""):
    """Generate an AI-powered draft reply using Claude"""
    client = anthropic.Anthropic()

    # Construct the prompt
    prompt = f"""You are helping draft a reply to an email. Generate a {tone} response.

Original Email:
From: {email_content['from']}
Subject: {email_content['subject']}
Date: {email_content['date']}

Body:
{email_content['body']}

{f"Additional Context: {additional_context}" if additional_context else ""}

Please generate a clear, concise, and {tone} reply to this email. Only provide the email body text, without any subject line or greetings like "Dear [Name]" unless specifically needed for the context."""

    message = client.messages.create(
        model="claude-haiku-4-5-20251001",
        max_tokens=1024,
        messages=[
            {"role": "user", "content": prompt}
        ]
    )

    return message.content[0].text


async def save_draft_to_gmail(to: str, subject: str, body: str, in_reply_to: str = None):
    """Save a draft email to Gmail using Gmail API"""
    service = get_gmail_service()

    # Get the authenticated user's email
    profile = service.users().getProfile(userId='me').execute()
    email_user = profile['emailAddress']

    # Create the email message
    msg = MIMEMultipart()
    msg['From'] = email_user
    msg['To'] = to
    msg['Subject'] = subject
    if in_reply_to:
        msg['In-Reply-To'] = in_reply_to
        msg['References'] = in_reply_to
    msg.attach(MIMEText(body, 'plain'))

    # Encode the message
    raw_message = base64.urlsafe_b64encode(msg.as_bytes()).decode('utf-8')

    # Create draft via Gmail API
    draft = service.users().drafts().create(
        userId='me',
        body={
            'message': {
                'raw': raw_message
            }
        }
    ).execute()

    return draft['id']


server = Server("email-server")


@server.list_tools()
async def handle_list_tools() -> list[types.Tool]:
    return [
        types.Tool(
            name="send_email",
            description="Send an email",
            inputSchema={
                "type": "object",
                "properties": {
                    "to": {"type": "string", "description": "Recipient email address"},
                    "subject": {"type": "string", "description": "Email subject"},
                    "body": {"type": "string", "description": "Email body content"},
                },
                "required": ["to", "subject", "body"],
            },
        ),
        types.Tool(
            name="get_unread_emails",
            description="Fetch unread emails from Gmail inbox",
            inputSchema={
                "type": "object",
                "properties": {
                    "max_emails": {
                        "type": "number",
                        "description": "Maximum number of unread emails to fetch (default: 10)",
                        "default": 10
                    },
                },
                "required": [],
            },
        ),
        types.Tool(
            name="generate_draft_reply",
            description="Generate an AI-powered draft reply to an email using Claude",
            inputSchema={
                "type": "object",
                "properties": {
                    "email_from": {"type": "string", "description": "The sender of the email to reply to (optional)"},
                    "email_subject": {"type": "string", "description": "The subject of the email to reply to (optional)"},
                    "email_body": {"type": "string", "description": "The body of the email to reply to"},
                    "email_date": {"type": "string", "description": "The date of the email to reply to (optional)"},
                    "tone": {
                        "type": "string",
                        "description": "The tone of the reply (e.g., professional, casual, friendly, default: professional)",
                    },
                    "additional_context": {
                        "type": "string",
                        "description": "Additional context or instructions for the reply (optional)",
                    },
                },
                "required": ["email_body"],
            },
        ),
        types.Tool(
            name="save_draft",
            description="Save a draft email to Gmail",
            inputSchema={
                "type": "object",
                "properties": {
                    "to": {"type": "string", "description": "Recipient email address"},
                    "subject": {"type": "string", "description": "Email subject"},
                    "body": {"type": "string", "description": "Email body content"},
                    "in_reply_to": {
                        "type": "string",
                        "description": "Message ID of the email being replied to (optional)"
                    },
                },
                "required": ["to", "subject", "body"],
            },
        ),
    ]


@server.call_tool()
async def handle_call_tool(name: str, arguments: dict) -> list[types.TextContent]:
    if name == "send_email":
        to = arguments["to"]
        subject = arguments["subject"]
        body = arguments["body"]

        await send_email(to, subject, body)
        return [types.TextContent(type="text", text=f"✓ Email sent to {to}")]

    elif name == "get_unread_emails":
        max_emails = arguments.get("max_emails", 10)
        emails = await get_unread_emails(max_emails)

        if not emails:
            return [types.TextContent(type="text", text="No unread emails found.")]

        # Format emails for display
        result = f"Found {len(emails)} unread email(s):\n\n"
        for i, email in enumerate(emails, 1):
            result += f"--- Email {i} ---\n"
            result += f"From: {email['from']}\n"
            result += f"Subject: {email['subject']}\n"
            result += f"Date: {email['date']}\n"
            result += f"Message ID: {email['message_id']}\n"
            result += f"Body:\n{email['body']}\n\n"

        return [types.TextContent(type="text", text=result)]

    elif name == "generate_draft_reply":
        email_content = {
            'from': arguments.get('email_from', 'Unknown'),
            'subject': arguments.get('email_subject', 'No subject'),
            'body': arguments['email_body'],
            'date': arguments.get('email_date', '')
        }
        tone = arguments.get('tone', 'professional')
        additional_context = arguments.get('additional_context', '')

        draft_reply = await generate_draft_reply(email_content, tone, additional_context)

        result = f"Generated Draft Reply:\n\n{draft_reply}\n\n"
        result += f"(Tone: {tone})"

        return [types.TextContent(type="text", text=result)]

    elif name == "save_draft":
        to = arguments["to"]
        subject = arguments["subject"]
        body = arguments["body"]
        in_reply_to = arguments.get("in_reply_to")

        await save_draft_to_gmail(to, subject, body, in_reply_to)
        return [types.TextContent(type="text", text=f"✓ Draft saved to Gmail for {to}")]

    raise ValueError(f"Unknown tool: {name}")


async def main():
    async with mcp.server.stdio.stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            InitializationOptions(
                server_name="email-server",
                server_version="1.0.0",
                capabilities=server.get_capabilities(
                    notification_options=NotificationOptions(),
                    experimental_capabilities={},
                ),
            ),
        )


if __name__ == "__main__":
    asyncio.run(main())