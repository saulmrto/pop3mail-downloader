# pop3mail-downloader

**¡Tambien disponible en español! al ejecutar el programa podras seleccionar el idioma a tu gusto.**
**Puedes traducir este texto con el traductor de tu navegador preferido.**

A Python script (`main.py`) designed to download emails from multiple POP3 accounts, save them locally, extract metadata, and apply basic spam filtering rules.

## Features

*   **Multiple Account Support**: Downloads emails from various POP3 accounts configured in `accounts.txt`.
*   **Email Storage**: Saves downloaded emails as individual `.eml` files, organized into folders per account.
*   **Metadata Extraction**: Parses email headers (From, To, CC, BCC, Subject, Date, Message-ID) and body content.
*   **Date Normalization**: Converts email dates to Central Standard Time (CST/America/Mexico_City). **Next update there will be option to change this.**
*   **Duplicate Prevention**: Avoids re-downloading emails by checking against previously stored metadata (`emails_metadata.json`).
*   **Spam Information**:
    *   Extracts spam scores from email headers (for informational purposes).
*   **Structured Output**:
    *   Emails are saved in: `User_Documents/Pop3MailDownloader_UserData/emails/<account_email>/`
    *   Consolidated metadata is stored in: `User_Documents/Pop3MailDownloader_UserData/emails_metadata.json`
    *   Logs are stored in: `User_Documents/Pop3MailDownloader_UserData/Logs/` **Auto log delete on next update**
*   **Continuous Operation**: Runs in a loop, checking for new emails at a configurable interval (`CHECK_INTERVAL`).
*   **Manual Trigger**: Can be forced to check emails immediately by creating a `trigger_check.txt` file in the user data directory.
*   **Internationalization**: Console messages are available in English (en) or Spanish (es), configurable via `settings.json`.
*   **Automatic Setup**: Creates necessary data directories and prompts for language selection on the first run.

## Setup

1.  **Python**: Ensure you have Python 3.9 or newer installed. The `zoneinfo` module is used for timezone handling and is standard from Python 3.9.
2.  **Dependencies**: The script uses standard Python libraries. No external packages need to be installed via pip if you are using Python 3.9+.
    *   `poplib`
    *   `email`
    *   `hashlib`
    *   `json`
    *   `datetime`
    *   `zoneinfo`
    *   `re`
    *   `logging`
    *   `time`
    *   `os`

## Configuration

Upon first run, the script will create a directory `Pop3MailDownloader_UserData` in your user's "Documents" folder. All configuration files and data will be stored here.

1.  **Language Selection (`settings.json`)**:
    *   On the very first run, the script will ask you to select a language (English or Spanish) for console messages.
    *   This preference is saved in `Pop3MailDownloader_UserData/settings.json`.
        ```json
        {
            "lang": "en" // or "es"
        }
        ```

2.  **Account Configuration (`accounts.txt`)**:
    *   Create a file named `accounts.txt` inside the `Pop3MailDownloader_UserData` directory.
    *   Each line in this file represents one POP3 email account.
    *   The format for each line is: `username:password@pop3server:port`
    *   **Example `accounts.txt`**:
        ```
        # This is a comment, lines starting with # are ignored
        user1@example.com:yourpassword123@mail.example.com:995
        anotheruser@domain.net:anotherpass@pop.domain.net:110
        ```
    *   Port `995` is typically used for POP3 over SSL/TLS.
    *   Port `110` is typically used for standard POP3 (the script will attempt to upgrade to TLS via STARTTLS).

3.  **Spam Configuration (`spam_config.json` - CURRENTLY NOT IN USE)**:
    *   A file named `spam_config.json` can be placed in `Pop3MailDownloader_UserData/`.
    *   **Note**: As of the current version of `main.py`, this file is **not actively read or used** to apply spam filtering rules. The spam filtering logic based on this file has been disabled.
    *   If you intend to implement spam filtering, you would need to modify `main.py` to read and process this file. An example structure for `spam_config.json` would be:
        ```json
        {
          "mail_whitelist": ["good_sender@example.com"],
          "mail_blacklist": ["bad_sender@example.com"],
          "word_whitelist": ["important project"],
          "word_blacklist": ["free money offer"]
        }
        ```

## Running the Script

1.  Navigate to the directory where `main.py` is located using your terminal or command prompt.
2.  Run the script using Python:
    ```bash
    python main.py
    ```
3.  The script will start, perform the initial setup if needed (language selection, directory creation), and then begin its email checking loop.
4.  To stop the script, press `Ctrl+C` in the terminal.

## How `main.py` Works

1.  **Initialization**:
    *   Determines the user data directory path (`User_Documents/Pop3MailDownloader_UserData/`).
    *   Creates this directory and essential subdirectories (`emails`, `filters`, `Logs`) if they don't exist.
    *   Handles language selection (prompts user if `settings.json` or language preference is missing) and loads localized messages.
    *   Configures logging.
2.  **Main Loop**:
    *   The script enters an infinite loop, performing checks at intervals defined by `CHECK_INTERVAL` (default 15 minutes).
    *   **Account Processing**:
        *   Loads account credentials from `Pop3MailDownloader_UserData/accounts.txt`.
        *   (Currently, spam filter lists are initialized as empty, as `spam_config.json` is not read by default).
        *   Loads existing email metadata from `Pop3MailDownloader_UserData/emails_metadata.json` to identify already downloaded emails.
        *   For each configured account:
            *   Connects to the POP3 server (handles SSL for port 995, attempts STARTTLS for port 110).
            *   Authenticates the user.
            *   Retrieves the list of emails in the mailbox.
            *   For each email:
                *   Calculates a hash of its headers to check against `existing_hashes`.
                *   If the email is new:
                    *   Downloads the full email content.
                    *   Parses the email (headers like From, To, Subject, Date; and body).
                    *   Converts the email's date to CST (America/Mexico_City).
                    *   Extracts plain text from the email body.
                    *   Extracts `X-Spam-Score` or similar headers (informational). No active filtering based on whitelists/blacklists is performed by default.
                    *   Saves the email as a `.eml` file in `Pop3MailDownloader_UserData/emails/<account_email>/`. The filename is generated using the date, subject, and sender.
                    *   Appends the extracted metadata (including path, sender, subject, date, spam status, etc.) to the `all_emails_metadata` list and updates the `existing_hashes` set.
    *   **Metadata Update**: After processing all accounts, `Pop3MailDownloader_UserData/emails_metadata.json` is overwritten with the updated list of all email metadata.
    *   **Wait or Trigger**:
        *   Waits for `CHECK_INTERVAL` seconds.
        *   During the wait, it checks for the existence of `Pop3MailDownloader_UserData/trigger_check.txt`. If found, the wait is interrupted, the trigger file is deleted, and a new cycle begins immediately.

## Directory Structure (within `User_Documents/Pop3MailDownloader_UserData/`)

```
/Pop3MailDownloader_UserData/
├── accounts.txt                # User's email account credentials
├── emails_metadata.json        # JSON file storing metadata of all downloaded emails
├── spam_config.json            # (Optional) For spam filter rules - NOT CURRENTLY USED by main.py
├── settings.json               # Stores user preferences like language
├── trigger_check.txt           # (Optional) Create this file to trigger an immediate check
├── emails/                     # Root folder for downloaded .eml files
│   ├── user1@example.com/      # Emails for user1
│   │   └── YYYY-MM-DD_HH-MM --- Subject --- Sender.eml
│   └── anotheruser@domain.net/ # Emails for anotheruser
│       └── ...
├── filters/                    # Legacy folder, not actively used for spam rules by main.py
└── Logs/                       # Log files
    ├── RawDates_Script_YYYY-MM-DD.log # Logs raw date strings and their conversions
    └── ... (other potential log files)
```