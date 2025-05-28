# POP3 Mail Downloader

**🌍 Available in English and Spanish** | **Disponible en inglés y español**

A Python script designed to download emails from multiple POP3 accounts, save them locally as `.eml` files, extract metadata, and provide basic spam detection. This tool works seamlessly with the [MailEML Viewer](https://github.com/saulmrto/maileml-viewer) for browsing and managing downloaded emails.

## ✨ Features

### 📧 Email Management
- **Multiple Account Support**: Download emails from various POP3 accounts configured in `accounts.txt`
- **Email Storage**: Save emails as individual `.eml` files, organized by account
- **Duplicate Prevention**: Avoid re-downloading emails using metadata comparison
- **Continuous Operation**: Run in a loop with configurable check intervals

### 🕒 Date & Time Handling
- **Date Normalization**: Convert email dates to Central Standard Time (CST/America/Mexico_City)
- **Timezone Support**: Built-in timezone handling using Python's `zoneinfo` module

### 📊 Metadata & Organization
- **Header Extraction**: Parse From, To, CC, BCC, Subject, Date, and Message-ID
- **Structured Storage**: Organized folder structure and consolidated metadata file
- **Spam Information**: Extract spam scores from email headers

### 🌐 Internationalization
- **Language Support**: Console messages in English or Spanish
- **User Preference**: Configurable via `settings.json`

### 🔧 Advanced Features
- **Manual Trigger**: Force immediate email check by creating `trigger_check.txt`
- **Automatic Setup**: Create necessary directories on first run
- **Comprehensive Logging**: Detailed logs for troubleshooting

## 📋 Requirements

- **Python**: 3.9 or newer (required for `zoneinfo` module)
- **Dependencies**: Uses only standard Python libraries (no pip installs needed)
  - `poplib`, `email`, `hashlib`, `json`, `datetime`, `zoneinfo`, `re`, `logging`, `time`, `os`

## 🚀 Installation & Setup

### 1. First Run Setup
Upon first execution, the script automatically:
- Creates `Pop3MailDownloader_UserData` directory in your Documents folder
- Prompts for language selection (English/Spanish)
- Sets up necessary subdirectories

### 2. Language Configuration
Create or edit `Pop3MailDownloader_UserData/settings.json`:
```json
{
  "lang": "en"  // or "es" for Spanish
}
```

### 3. Email Account Configuration
Create `Pop3MailDownloader_UserData/accounts.txt` with your POP3 accounts:

```
# Format: username:password@pop3server:port
# Lines starting with # are comments

user1@example.com:yourpassword123@mail.example.com:995
anotheruser@domain.net:anotherpass@pop.domain.net:110
```

**Port Information:**
- **995**: POP3 over SSL/TLS (recommended)
- **110**: Standard POP3 (script attempts STARTTLS upgrade)

### 4. Spam Configuration (Optional)
Create `Pop3MailDownloader_UserData/spam_config.json` for future spam filtering:
```json
{
  "mail_whitelist": ["trusted@example.com"],
  "mail_blacklist": ["spam@example.com"],
  "word_whitelist": ["important project"],
  "word_blacklist": ["free money offer"]
}
```
*Note: Current version doesn't actively use this file for filtering*

## 🎯 Usage

### Running the Script
```bash
# Navigate to the script directory
cd /path/to/pop3mail-downloader

# Run the script
python main.py
```

### Stopping the Script
Press `Ctrl+C` in the terminal to stop execution.

### Manual Email Check
Create an empty file named `trigger_check.txt` in the `Pop3MailDownloader_UserData` directory to trigger an immediate email check.

## 📁 Directory Structure

```
Documents/Pop3MailDownloader_UserData/
├── accounts.txt                    # Email account credentials
├── emails_metadata.json           # Consolidated email metadata
├── spam_config.json              # (Optional) Spam filter rules
├── settings.json                  # User preferences
├── trigger_check.txt             # (Optional) Manual trigger file
├── emails/                       # Downloaded .eml files
│   ├── user1@example.com/
│   │   └── YYYY-MM-DD_HH-MM --- Subject --- Sender.eml
│   └── anotheruser@domain.net/
│       └── YYYY-MM-DD_HH-MM --- Subject --- Sender.eml
├── filters/                      # Legacy folder (not actively used)
└── Logs/                         # Log files
    ├── RawDates_Script_YYYY-MM-DD.log
    └── ...
```

## ⚙️ How It Works

### Initialization Phase
1. **Directory Setup**: Creates user data directory and subdirectories
2. **Language Selection**: Prompts for language if not configured
3. **Logging Configuration**: Sets up comprehensive logging system

### Main Operation Loop
1. **Account Processing**: Load credentials from `accounts.txt`
2. **Metadata Loading**: Read existing email metadata to prevent duplicates
3. **Email Download**: For each account:
   - Connect to POP3 server (SSL/TLS support)
   - Authenticate user credentials
   - Download new emails only
   - Parse headers and extract metadata
   - Convert dates to CST timezone
   - Save as `.eml` files with descriptive names
4. **Metadata Update**: Update consolidated `emails_metadata.json`
5. **Wait Cycle**: Wait for next check or manual trigger

### Security Features
- **SSL/TLS Support**: Secure connections for port 995
- **STARTTLS Upgrade**: Automatic encryption upgrade for port 110
- **Hash-based Deduplication**: Prevent duplicate downloads

## 🔗 Integration

This tool is designed to work with [MailEML Viewer](https://github.com/saulmrto/maileml-viewer), which provides:
- Web-based email browsing interface
- Advanced filtering and search capabilities
- Email preview and download functionality
- Spam detection and warnings

## 🐛 Troubleshooting

### Common Issues
- **Connection Errors**: Verify POP3 server settings and credentials
- **Permission Issues**: Ensure write access to Documents folder
- **Date Processing**: Check logs for timezone conversion issues

### Log Files
Check `Pop3MailDownloader_UserData/Logs/` for detailed operation logs.

## 📄 License

This project is open source. Please check the repository for license details.

## 🤝 Contributing

Contributions are welcome! Please feel free to submit issues and pull requests.

---

**Next Update Features:**
- Configurable timezone selection
- Automatic log cleanup
- Enhanced spam filtering
- Improved error handling
