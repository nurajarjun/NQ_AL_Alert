# Security Best Practices

## Environment Variables

**CRITICAL:** Never commit the `.env` file to git!

### Setup Instructions

1. Copy the example file:
   ```bash
   cp .env.example .env
   ```

2. Edit `.env` and add your actual credentials:
   - `TELEGRAM_BOT_TOKEN` - Your Telegram bot token from @BotFather
   - `TELEGRAM_CHAT_ID` - Your Telegram chat ID
   - `GOOGLE_API_KEY` - Your Google Gemini API key
   - `NGROK_AUTHTOKEN` - Your ngrok auth token (for Docker deployment)

3. **NEVER** commit the `.env` file to git!

### What's Protected

The `.env` file is already in `.gitignore` and will not be committed. The repository includes:
- ✅ `.env.example` - Template with placeholder values (SAFE to commit)
- ❌ `.env` - Your actual credentials (NEVER commit)

### If You Accidentally Commit Credentials

If you accidentally commit API keys or tokens:

1. **Immediately rotate/regenerate all exposed credentials:**
   - Telegram: Create a new bot with @BotFather
   - Google API: Regenerate your API key in Google Cloud Console
   - Ngrok: Regenerate your auth token

2. **Remove from git history:**
   ```bash
   git filter-branch --force --index-filter \
     "git rm --cached --ignore-unmatch .env" \
     --prune-empty --tag-name-filter cat -- --all
   
   git push origin --force --all
   ```

3. **Update your local `.env` with new credentials**

### Current Status

✅ `.env` file is NOT in git repository
✅ `.env.example` template is available
✅ `.gitignore` is properly configured
✅ No sensitive data in git history

## Additional Security Measures

1. **Use environment-specific files:**
   - `.env.development`
   - `.env.production`
   - `.env.test`

2. **For production deployments:**
   - Use platform environment variables (Render, Heroku, etc.)
   - Never store credentials in code or config files

3. **Regular security audits:**
   - Check git history: `git log --all --full-history -- .env`
   - Scan for secrets: Use tools like `git-secrets` or `truffleHog`

## Emergency Contacts

If credentials are exposed:
- Telegram Bot: @BotFather - revoke token immediately
- Google Cloud: https://console.cloud.google.com/apis/credentials
- Ngrok: https://dashboard.ngrok.com/get-started/your-authtoken
