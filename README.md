# Email MCP Server

An MCP (Model Context Protocol) server that provides email management capabilities for Gmail, including fetching unread emails, generating AI-powered draft replies using Claude, and saving drafts.

## Features

- **Fetch Unread Emails**: Retrieve unread emails from your Gmail inbox via Gmail API
- **Generate AI Draft Replies**: Use Claude AI to generate contextual email replies with customizable tone
- **Save Drafts**: Save draft emails directly to Gmail
- **Send Emails**: Send emails via Gmail API
- **OAuth 2.0 Authentication**: Secure authentication using Google OAuth (no app passwords needed!)

## Prerequisites

- Python 3.8+
- Gmail account
- Google Cloud Project with Gmail API enabled
- OAuth 2.0 credentials from Google Cloud Console
- Anthropic API key (for AI-powered draft replies)
- Claude Desktop (for MCP integration)

## Setup

### 1. Configure Gmail API and OAuth 2.0

#### Create Google Cloud Project

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select an existing one
3. Enable the Gmail API:
   - Navigate to **APIs & Services > Library**
   - Search for "Gmail API"
   - Click **Enable**

#### Configure OAuth Consent Screen

1. Go to **APIs & Services > OAuth consent screen**
2. Choose **External** user type (or **Internal** if using Google Workspace)
3. Fill in the required fields:
   - App name: "Email MCP Server" (or your preferred name)
   - User support email: Your email address
   - Developer contact: Your email address
4. Click **Save and Continue**

#### Add OAuth Scopes

1. On the Scopes page, click **Add or Remove Scopes**
2. Add these scopes:
   - `https://www.googleapis.com/auth/gmail.readonly` - Read emails
   - `https://www.googleapis.com/auth/gmail.compose` - Create drafts
   - `https://www.googleapis.com/auth/gmail.modify` - Modify emails
   - `https://www.googleapis.com/auth/gmail.send` - Send emails
3. Click **Update** and **Save and Continue**

#### Add Test Users

1. On the Test users page, click **+ ADD USERS**
2. Add your Gmail address
3. Click **Save**

#### Create OAuth Credentials

1. Go to **APIs & Services > Credentials**
2. Click **Create Credentials > OAuth client ID**
3. Choose **Desktop app** as the application type
4. Enter a name (e.g., "Email MCP Client")
5. Click **Create**
6. Download the credentials JSON file
7. Save it as `credentials.json` in the project directory

### 2. Install Dependencies

```bash
cd email-mcp-server
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 3. Authenticate with Gmail

Run the authentication script to complete the OAuth flow:

```bash
source venv/bin/activate
python gmail_auth.py
```

This will:
1. Open your browser for Google sign-in
2. Ask you to authorize the app
3. Save a `token.json` file with your credentials

**Note:** You may see a warning "Google hasn't verified this app" - this is normal for apps in testing mode. Click **"Advanced"** and **"Go to email-mcp-server (unsafe)"** to proceed.

The `token.json` file contains your refresh token and will be used automatically by the MCP server. You won't need to re-authenticate unless you revoke access or delete this file.

### 4. Get Anthropic API Key

1. Sign up at [https://console.anthropic.com](https://console.anthropic.com)
2. Create an API key from the dashboard
3. Keep this key secure - you'll add it to the Claude Desktop config

### 5. Configure Claude Desktop

Add to your Claude Desktop configuration file at `~/.config/Claude/claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "email": {
      "command": "/path/to/your/email-mcp-server/venv/bin/python",
      "args": ["/path/to/your/email-mcp-server/email_server.py"],
      "env": {
        "ANTHROPIC_API_KEY": "your-anthropic-api-key"
      }
    }
  }
}
```

**Example (replace paths with your actual paths):**
```json
{
  "mcpServers": {
    "email": {
      "command": "/home/username/mcp/email-mcp-server/venv/bin/python",
      "args": ["/home/username/mcp/email-mcp-server/email_server.py"],
      "env": {
        "ANTHROPIC_API_KEY": "sk-ant-api03-..."
      }
    }
  }
}
```

**Important Notes:**
- Make sure both `credentials.json` and `token.json` are in the project directory
- These files are already in `.gitignore` - never commit them to version control
- After updating the config, restart Claude Desktop for changes to take effect

## Available Tools

### 1. get_unread_emails

Fetch unread emails from Gmail inbox.

**Parameters:**
- `max_emails` (optional): Maximum number of emails to fetch (default: 10)

**Example:**
```json
{
  "max_emails": 5
}
```

### 2. generate_draft_reply

Generate an AI-powered draft reply using Claude.

**Parameters:**
- `email_from`: The sender's email address
- `email_subject`: The subject of the email
- `email_body`: The body of the email
- `email_date`: The date of the email
- `tone` (optional): Tone of the reply (e.g., "professional", "casual", "friendly")
- `additional_context` (optional): Additional context for the AI to consider

**Example:**
```json
{
  "email_from": "sender@example.com",
  "email_subject": "Project Update",
  "email_body": "How is the project coming along?",
  "email_date": "Mon, 13 Nov 2024 10:30:00",
  "tone": "professional",
  "additional_context": "The project is on track and will be completed by Friday"
}
```

### 3. save_draft

Save a draft email to Gmail.

**Parameters:**
- `to`: Recipient email address
- `subject`: Email subject
- `body`: Email body content
- `in_reply_to` (optional): Message ID of the email being replied to

**Example:**
```json
{
  "to": "recipient@example.com",
  "subject": "Re: Project Update",
  "body": "The project is progressing well...",
  "in_reply_to": "<message-id@example.com>"
}
```

### 4. send_email

Send an email immediately.

**Parameters:**
- `to`: Recipient email address
- `subject`: Email subject
- `body`: Email body content

**Example:**
```json
{
  "to": "recipient@example.com",
  "subject": "Hello",
  "body": "This is a test email."
}
```

## Demo: Working with Claude Desktop

Once configured, you can interact with your emails through Claude Desktop using natural language.

### Example Prompts

**1. Check unread emails:**
```
"Show me my unread emails"
"What are my latest 5 unread emails?"
"Check my inbox for unread messages"
```

**2. Generate draft replies:**
```
"Generate a professional reply to the first email"
"Draft a friendly response to the email from [sender]"
"Create a casual reply to the project update email with a professional tone"
```

**3. Save drafts:**
```
"Save that reply as a draft in Gmail"
"Create a draft reply to [sender] about [topic]"
```

**4. Complete workflow:**
```
"Check my unread emails, then draft a professional reply to the most recent one and save it as a draft"
```

### Workflow Example

1. **Fetch unread emails:**
   - Claude calls `get_unread_emails` tool
   - Returns sender, subject, body, date, and message ID for each email

2. **Generate a draft reply:**
   - Claude calls `generate_draft_reply` with email details and desired tone
   - AI generates contextual response using Claude Haiku

3. **Save the draft to Gmail:**
   - Claude calls `save_draft` with recipient, subject, body, and threading info
   - Draft appears in your Gmail Drafts folder, properly threaded

### Screenshots

To demonstrate the MCP server in action, consider adding screenshots showing:
- Claude Desktop fetching unread emails
- AI-generated draft replies
- Confirmation of drafts saved to Gmail
- The complete workflow from reading to replying

*(You can add screenshots to a `screenshots/` folder and reference them here)*

## Security Notes

- Never commit `credentials.json` or `token.json` to version control (they're in `.gitignore`)
- OAuth tokens are stored securely in `token.json` with file permissions
- The refresh token allows automatic re-authentication without user interaction
- Revoke access anytime from your [Google Account](https://myaccount.google.com/permissions)
- Consider using environment-specific credentials for production deployments

## Troubleshooting

### OAuth Authentication Issues

**"Access blocked: email-mcp-server has not completed the Google verification process"**
- Make sure you've added yourself as a test user in the OAuth consent screen
- Go to **APIs & Services > OAuth consent screen > Test users** and add your email

**"Google hasn't verified this app" warning**
- This is normal for apps in testing mode
- Click **"Advanced"** → **"Go to email-mcp-server (unsafe)"** to proceed
- For personal use only, this is perfectly safe

**Token refresh fails**
- Delete `token.json` and run `python gmail_auth.py` again to re-authenticate
- Check that your Google Cloud project is still active
- Verify the Gmail API is still enabled

### Permission Errors

**"Insufficient Permission" or "Request had insufficient authentication scopes"**
- Delete `token.json`
- Re-run `python gmail_auth.py` to get a new token with correct scopes
- Verify all required scopes are added to your OAuth consent screen

### Revoke and Reset

To revoke access and start fresh:

```bash
python gmail_auth.py revoke
```

Then re-authenticate:

```bash
python gmail_auth.py
```

## Development

To run the server in development mode:

```bash
cd email
source venv/bin/activate
python email_server.py
```

## License

MIT License
