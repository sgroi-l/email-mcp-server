# Troubleshooting Guide

This guide covers common issues and solutions when setting up and using the Email MCP Server.

## OAuth Authentication Issues

### "Access blocked: email-mcp-server has not completed the Google verification process"

**Cause:** You haven't added yourself as a test user in the OAuth consent screen.

**Solution:**
1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Navigate to **APIs & Services > OAuth consent screen**
3. Click on **Test users** section
4. Click **+ ADD USERS**
5. Add your Gmail address
6. Click **Save**
7. Try authenticating again with `python gmail_auth.py`

### "Google hasn't verified this app" warning

**Cause:** This is normal for OAuth apps in testing mode.

**Solution:**
- This is perfectly safe for personal use
- Click **"Advanced"** at the bottom of the warning
- Click **"Go to email-mcp-server (unsafe)"** to proceed
- This allows your app to access your Gmail account

**Note:** If you want to publish this app for others to use, you would need to complete Google's verification process, but this is not necessary for personal use.

### Token refresh fails

**Cause:** The stored token has expired or been revoked.

**Solution:**
```bash
cd email-mcp-server
source venv/bin/activate
# Delete the old token
rm token.json
# Re-authenticate
python gmail_auth.py
```

**Additional checks:**
- Verify your Google Cloud project is still active
- Ensure the Gmail API is still enabled
- Check that your OAuth credentials haven't been deleted

## Permission Errors

### "Insufficient Permission" or "Request had insufficient authentication scopes"

**Cause:** Your token was created before all required scopes were added, or scopes are missing.

**Solution:**
1. Delete the existing token:
   ```bash
   rm token.json
   ```
2. Verify all required scopes are in your OAuth consent screen:
   - `https://www.googleapis.com/auth/gmail.readonly`
   - `https://www.googleapis.com/auth/gmail.compose`
   - `https://www.googleapis.com/auth/gmail.modify`
   - `https://www.googleapis.com/auth/gmail.send`
3. Re-authenticate:
   ```bash
   python gmail_auth.py
   ```

### "The caller does not have permission"

**Cause:** The Gmail API might not be enabled, or there's an issue with your credentials.

**Solution:**
1. Verify Gmail API is enabled in Google Cloud Console
2. Check that `credentials.json` is in the project directory
3. Try re-authenticating with `python gmail_auth.py`

## Claude Desktop Integration Issues

### MCP server not appearing in Claude Desktop

**Cause:** Configuration issue or Claude Desktop needs to be restarted.

**Solution:**
1. Verify your `claude_desktop_config.json` is in the correct location:
   - **macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`
   - **Linux**: `~/.config/Claude/claude_desktop_config.json`
   - **Windows**: `%APPDATA%\Claude\claude_desktop_config.json`
2. Check the configuration syntax is valid JSON
3. Verify the paths to Python and `email_server.py` are absolute and correct
4. Restart Claude Desktop completely (quit and reopen)

### Tools not available in Claude

**Cause:** The MCP server isn't starting or has crashed.

**Solution:**
1. Check Claude Desktop logs for errors
2. Verify the virtual environment Python path is correct
3. Test the server manually:
   ```bash
   cd email-mcp-server
   source venv/bin/activate
   python email_server.py
   ```
4. Ensure both `credentials.json` and `token.json` exist in the project directory

### "ANTHROPIC_API_KEY not set" error

**Cause:** The API key is missing or incorrectly configured in Claude Desktop config.

**Solution:**
1. Verify the `ANTHROPIC_API_KEY` is in the `env` section of your config
2. Check that the key starts with `sk-ant-api03-`
3. Ensure there are no extra spaces or quotes around the key
4. Restart Claude Desktop after updating the config

## Email Operation Errors

### Drafts not appearing in Gmail

**Cause:** The draft was saved but Gmail hasn't synced yet, or there's a threading issue.

**Solution:**
- Refresh your Gmail inbox
- Check the Drafts folder specifically
- If replying, verify the original email still exists
- Try saving a new draft without threading (`in_reply_to`)

### "Message not found" when replying

**Cause:** The original email may have been deleted or the message ID is incorrect.

**Solution:**
- Fetch emails again to get current message IDs
- Verify the email still exists in your inbox
- Try composing a new email instead of replying

### Rate limiting or quota errors

**Cause:** Gmail API has usage limits.

**Solution:**
- Wait a few minutes before trying again
- Check your [Google Cloud Console Quotas](https://console.cloud.google.com/apis/api/gmail.googleapis.com/quotas)
- For heavy usage, consider requesting quota increases

## General Debugging

### Enable verbose logging

To see detailed logs from the MCP server, check Claude Desktop's developer console or logs.

### Test authentication manually

```bash
cd email-mcp-server
source venv/bin/activate
python gmail_auth.py
```

This will verify your OAuth setup is working correctly.

### Verify credentials files

Check that both required files exist:
```bash
ls -la credentials.json token.json
```

Both files should be present and have content.

### Reset everything

If all else fails, start fresh:

```bash
# Revoke access
python gmail_auth.py revoke

# Delete tokens
rm token.json

# Re-authenticate
python gmail_auth.py

# Restart Claude Desktop
```

## Getting Help

If you're still experiencing issues:

1. Check the [OAuth Setup Guide](oauth-setup.md) to ensure all steps were completed
2. Review the [Usage Examples](usage-examples.md) for correct usage patterns
3. Verify your Python version is 3.8 or higher: `python --version`
4. Check that all dependencies are installed: `pip list`
5. Look for error messages in Claude Desktop logs or console output

## Common Mistakes

- Forgetting to restart Claude Desktop after config changes
- Using relative paths instead of absolute paths in config
- Not adding yourself as a test user in OAuth consent screen
- Deleting credentials.json or token.json accidentally
- Having incorrect Gmail API scopes
- Missing ANTHROPIC_API_KEY in environment variables
