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

### Listing Available Calendars

To see all calendars you have access to:
```bash
./calgen.py create --list-calendars
# or
./calgen.py from-sheet --list-calendars
```

This will display each calendar's ID and name. You can use these IDs with the `--calendar-id` option.

### Creating a Single Event

```bash
./calgen.py create \
  --title "Team Meeting" \
  --date "2024-03-20" \
  --timezone "America/New_York" \
  --calendar-id "your.email@example.com"
```

Arguments:
- `--title`: (Required) Event title
- `--date`: (Required) Event date in YYYY-MM-DD format
- `--timezone`: (Optional) Timezone name. Defaults to UTC
- `--start-time`: (Optional) Start time in HH:MM format (24-hour). Defaults to 00:00
- `--end-time`: (Optional) End time in HH:MM format (24-hour). Defaults to 23:59
- `--attendees`: (Optional) Comma-separated list of attendee email addresses
- `--calendar-id`: (Optional) Calendar ID to create events in. Defaults to primary calendar
- `--list-calendars`: (Optional) List available calendars and their IDs

### Creating Multiple Events from a CSV File

Create a CSV file with the following columns:
- `Country`: (Optional) Country name - this column will be ignored
- `Title`: (Required) Event title
- `Date`: (Required) Event date in YYYY-MM-DD format
- `Timezone`: (Required) Timezone for the event
- `Attendees`: (Optional) Comma-separated list of attendee email addresses

Example CSV format:
```csv
Country,Title,Date,Timezone,Attendees
USA,Team Meeting,2024-03-20,America/New_York,person1@example.com,person2@example.com
UK,Project Review,2024-03-21,Europe/London,person3@example.com
Japan,Board Meeting,2024-03-22,Asia/Tokyo,
```

Basic usage:
```bash
./calgen.py from-sheet events.csv --timezone "UTC" --calendar-id "your.email@example.com"
```

Override timezone and attendees for all events:
```bash
./calgen.py from-sheet events.csv \
  --override-timezone "America/New_York" \
  --attendees "person1@example.com,person2@example.com" \
  --calendar-id "your.email@example.com"
```

Arguments:
- First argument: Path to the CSV file (Required)
- `--timezone`: (Optional) Default timezone for events missing timezone. Defaults to UTC
- `--override-timezone`: (Optional) Override timezone for all events, ignoring values from the CSV
- `--attendees`: (Optional) Override attendees for all events, ignoring values from the CSV
- `--calendar-id`: (Optional) Calendar ID to create events in. Defaults to primary calendar
- `--list-calendars`: (Optional) List available calendars and their IDs

Note: When using `--override-timezone` or `--attendees`, the corresponding values in the CSV file will be ignored.

## Timezones

The tool supports all standard timezone names from the IANA Time Zone Database. Common examples:
- "UTC"
- "America/New_York"
- "Europe/London"
- "Asia/Tokyo"
- "Australia/Sydney"

## First Run

On first run, the script will open your default web browser for Google Calendar authorization. After authorizing, the credentials will be saved locally in `token.json` for future use. 