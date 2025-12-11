# Email MCP Server

An MCP (Model Context Protocol) server that brings email management capabilities to Claude Desktop. Fetch unread emails, generate AI-powered draft replies, and manage your Gmail inbox using natural language.

## What It Does

This server integrates Gmail with Claude Desktop, allowing you to:

- Fetch unread emails from your Gmail inbox
- Generate contextual draft replies with customizable tone using Claude AI
- Save drafts directly to Gmail with proper email threading
- Send emails via Gmail API
- Interact with your inbox using natural language in Claude Desktop

## Features

- **OAuth 2.0 Authentication**: Secure Google authentication (no app passwords needed)
- **AI-Powered Replies**: Generate smart email replies using Claude
- **Email Threading**: Maintains conversation threads when replying
- **Flexible Tone Control**: Choose professional, casual, or friendly tones for replies
- **Direct Gmail Integration**: Drafts appear in your Gmail Drafts folder

## Quick Start

### Prerequisites

- Python 3.8+
- Gmail account
- Google Cloud Project with Gmail API enabled ([Setup Guide](docs/oauth-setup.md))
- Anthropic API key ([Get one here](https://console.anthropic.com))
- Claude Desktop installed

### Installation

1. **Clone and install dependencies:**
   ```bash
   cd email-mcp-server
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

2. **Set up Google OAuth 2.0:**

   Follow the detailed [OAuth Setup Guide](docs/oauth-setup.md) to:
   - Create a Google Cloud Project
   - Enable Gmail API
   - Configure OAuth consent screen
   - Download `credentials.json`

3. **Authenticate with Gmail:**
   ```bash
   source venv/bin/activate
   python gmail_auth.py
   ```

   This opens your browser to authorize the app and saves a `token.json` file.

4. **Configure Claude Desktop:**

   Add to your Claude Desktop config file:
   - **macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`
   - **Linux**: `~/.config/Claude/claude_desktop_config.json`
   - **Windows**: `%APPDATA%\Claude\claude_desktop_config.json`

   ```json
   {
     "mcpServers": {
       "email": {
         "command": "/absolute/path/to/email-mcp-server/venv/bin/python",
         "args": ["/absolute/path/to/email-mcp-server/email_server.py"],
         "env": {
           "ANTHROPIC_API_KEY": "sk-ant-api03-..."
         }
       }
     }
   }
   ```

5. **Restart Claude Desktop**

## Usage

Once configured, interact with your emails in Claude Desktop using natural language:

- "Show me my unread emails"
- "Generate a professional reply to the first email"
- "Draft a friendly response mentioning the project is on track"
- "Save that reply as a draft in Gmail"

For more examples and workflows, see the [Usage Examples Guide](docs/usage-examples.md).

## Available Tools

The server provides four MCP tools that Claude can use:

### get_unread_emails
Fetches unread emails from Gmail. Optional parameter: `max_emails` (default: 10)

### generate_draft_reply
Generates AI-powered email replies. Parameters: `email_from`, `email_subject`, `email_body`, `email_date`, optional `tone` and `additional_context`

### save_draft
Saves draft emails to Gmail. Parameters: `to`, `subject`, `body`, optional `in_reply_to` for threading

### send_email
Sends emails immediately. Parameters: `to`, `subject`, `body`

## Documentation

- [Google OAuth 2.0 Setup Guide](docs/oauth-setup.md) - Step-by-step OAuth configuration with screenshot placeholders
- [Usage Examples](docs/usage-examples.md) - Real-world usage examples and workflows with Claude Desktop
- [Troubleshooting Guide](docs/troubleshooting.md) - Common issues and solutions

## Security

- Never commit `credentials.json` or `token.json` (already in `.gitignore`)
- OAuth tokens are stored locally in `token.json`
- Refresh tokens enable automatic re-authentication
- Revoke access anytime at [Google Account Permissions](https://myaccount.google.com/permissions)

## Development

Run the server manually for testing:

```bash
cd email-mcp-server
source venv/bin/activate
python email_server.py
```

## Troubleshooting

For common issues like OAuth errors, permission problems, or Claude Desktop integration issues, see the [Troubleshooting Guide](docs/troubleshooting.md).

Quick fixes:
- **OAuth issues**: Make sure you're added as a test user in Google Cloud Console
- **Permission errors**: Delete `token.json` and re-run `python gmail_auth.py`
- **MCP not working**: Verify paths are absolute in Claude Desktop config and restart the app

## License

MIT License
