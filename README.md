# Calendar Event Generator

A command-line tool to create Google Calendar events either individually or in bulk from a CSV file.

## Setup

1. Create a Google Cloud Project and enable the Google Calendar API:
   - Go to the [Google Cloud Console](https://console.cloud.google.com/)
   - Create a new project or select an existing one
   - Enable the Google Calendar API
   - Configure the OAuth consent screen
   - Create OAuth 2.0 credentials (Desktop application)
   - Download the credentials and save them as `credentials.json` in the project directory

2. Install the required dependencies:
```bash
pip install -r requirements.txt
```

3. Make the script executable:
```bash
chmod +x calgen.py
```

## Usage

The script provides two main commands: `create` for single events and `from-sheet` for bulk creation from a CSV file.

To see all available commands and options:
```bash
./calgen.py --help
```

To see help for a specific command:
```bash
./calgen.py create --help
./calgen.py from-sheet --help
```

### Creating a Single Event

```bash
./calgen.py create \
  --summary "Meeting with Team" \
  --date "2024-03-20" \
  --start-time "09:00" \
  --end-time "10:00" \
  --timezone "America/New_York" \
  --attendees "person1@example.com,person2@example.com"
```

Arguments:
- `--summary`: (Required) Event title/summary
- `--date`: (Required) Event date in YYYY-MM-DD format
- `--start-time`: (Optional) Start time in HH:MM format (24-hour). Defaults to 00:00
- `--end-time`: (Optional) End time in HH:MM format (24-hour). Defaults to 23:59
- `--timezone`: (Optional) Timezone name. Defaults to UTC
- `--attendees`: (Optional) Comma-separated list of attendee email addresses

### Creating Multiple Events from a CSV File

Create a CSV file with the following columns:
- `summary` (required): Event title
- `date` (required): Event date in YYYY-MM-DD format
- `start_time` (optional): Start time in HH:MM format
- `end_time` (optional): End time in HH:MM format
- `attendees` (optional): Comma-separated list of attendee emails

Example CSV format:
```csv
summary,date,start_time,end_time,attendees
Team Meeting,2024-03-20,09:00,10:00,person1@example.com,person2@example.com
Project Review,2024-03-21,14:00,15:30,person3@example.com
```

Then run:
```bash
./calgen.py from-sheet events.csv --timezone "America/New_York"
```

Arguments:
- First argument: Path to the CSV file (Required)
- `--timezone`: (Optional) Default timezone for all events. Defaults to UTC

## Timezones

The tool supports all standard timezone names from the IANA Time Zone Database. Common examples:
- "UTC"
- "America/New_York"
- "Europe/London"
- "Asia/Tokyo"
- "Australia/Sydney"

## First Run

On first run, the script will open your default web browser for Google Calendar authorization. After authorizing, the credentials will be saved locally in `token.json` for future use. 