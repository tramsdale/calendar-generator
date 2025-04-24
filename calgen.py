#!/usr/bin/env python3

import os
import json
import argparse
from datetime import datetime
from typing import List, Optional

import pandas as pd
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from dateutil import parser
import pytz

# If modifying these scopes, delete the file token.json.
SCOPES = ['https://www.googleapis.com/auth/calendar']

def get_google_calendar_service():
    """Get or create Google Calendar API service."""
    creds = None
    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first time.
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            if not os.path.exists('credentials.json'):
                raise FileNotFoundError(
                    "Missing credentials.json file. Please download it from Google Cloud Console "
                    "and save it in the current directory."
                )
            flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token.json', 'w') as token:
            token.write(creds.to_json())

    return build('calendar', 'v3', credentials=creds)

def list_calendars(service):
    """List available calendars and their IDs."""
    calendars = service.calendarList().list().execute()
    print("\nAvailable calendars:")
    print("-" * 50)
    for calendar in calendars['items']:
        print(f"Calendar ID: {calendar['id']}")
        print(f"Name: {calendar['summary']}")
        print("-" * 50)

def create_calendar_event(
    service,
    title: str,
    date: str,
    timezone: str = "UTC",
    start_time: str = "00:00",
    end_time: str = "23:59",
    attendees: Optional[List[str]] = None,
    calendar_id: str = "primary"
):
    """Create a calendar event with the given parameters."""
    # Parse the date and times
    start_dt = parser.parse(f"{date} {start_time}")
    end_dt = parser.parse(f"{date} {end_time}")
    
    # Set timezone
    tz = pytz.timezone(timezone)
    start_dt = tz.localize(start_dt)
    end_dt = tz.localize(end_dt)

    event = {
        'summary': title,
        'start': {
            'dateTime': start_dt.isoformat(),
            'timeZone': timezone,
        },
        'end': {
            'dateTime': end_dt.isoformat(),
            'timeZone': timezone,
        },
    }

    if attendees:
        event['attendees'] = [{'email': email.strip()} for email in attendees]

    event = service.events().insert(calendarId=calendar_id, body=event).execute()
    return event

def process_sheet(sheet_path: str, default_timezone: str = "UTC", calendar_id: str = "primary"):
    """Process events from a CSV file."""
    try:
        df = pd.read_csv(sheet_path)
        required_columns = {'Title', 'Date', 'Timezone'}
        if not required_columns.issubset(df.columns):
            raise ValueError(
                f"Sheet must contain the following columns: {required_columns}. "
                f"Found columns: {list(df.columns)}"
            )

        service = get_google_calendar_service()
        events_created = 0

        for _, row in df.iterrows():
            # Use row's timezone if available, otherwise use default
            timezone = row.get('Timezone', default_timezone).strip()
            
            create_calendar_event(
                service=service,
                title=row['Title'],
                date=row['Date'],
                timezone=timezone,
                start_time="00:00",
                end_time="23:59",
                calendar_id=calendar_id
            )
            events_created += 1

        return events_created
    except Exception as e:
        print(f"Error processing sheet: {str(e)}")
        return 0

def create_single_event(args):
    """Handle creation of a single calendar event."""
    try:
        service = get_google_calendar_service()
        
        # If requested, list available calendars
        if args.list_calendars:
            list_calendars(service)
            return

        attendee_list = args.attendees.split(',') if args.attendees else None
        event = create_calendar_event(
            service=service,
            title=args.title,
            date=args.date,
            start_time=args.start_time,
            end_time=args.end_time,
            timezone=args.timezone,
            attendees=attendee_list,
            calendar_id=args.calendar_id
        )
        print(f"Event created successfully! Event ID: {event['id']}")
    except Exception as e:
        print(f"Error creating event: {str(e)}")

def create_from_sheet(args):
    """Handle creation of events from a CSV file."""
    try:
        service = get_google_calendar_service()
        
        # If requested, list available calendars
        if args.list_calendars:
            list_calendars(service)
            return

        events_created = process_sheet(args.file, args.timezone, args.calendar_id)
        print(f"Successfully created {events_created} events!")
    except Exception as e:
        print(f"Error: {str(e)}")

def main():
    # Create the top-level parser
    parser = argparse.ArgumentParser(
        description='Calendar event generator for Google Calendar',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  Create a single event:
    %(prog)s create --title "Team Meeting" --date "2024-03-20" --timezone "America/New_York"

  Create events from CSV:
    %(prog)s from-sheet events.csv --timezone "UTC"

  List available calendars:
    %(prog)s create --list-calendars
    %(prog)s from-sheet --list-calendars
        """
    )
    subparsers = parser.add_subparsers(dest='command', help='Commands')
    subparsers.required = True

    # Common arguments for both commands
    calendar_args = {
        '--calendar-id': {
            'default': "primary",
            'help': 'Calendar ID to create events in. Use --list-calendars to see available calendars.'
        },
        '--list-calendars': {
            'action': 'store_true',
            'help': 'List available calendars and their IDs'
        }
    }

    # Parser for the 'create' command
    create_parser = subparsers.add_parser('create', help='Create a single calendar event')
    create_parser.add_argument(
        '--title',
        required=True,
        help='Event title'
    )
    create_parser.add_argument(
        '--date',
        required=True,
        help='Event date in YYYY-MM-DD format'
    )
    create_parser.add_argument(
        '--timezone',
        default="UTC",
        help='Timezone (e.g., "America/New_York", "Europe/London"). Defaults to UTC'
    )
    create_parser.add_argument(
        '--start-time',
        default="00:00",
        help='Start time in HH:MM format (24-hour). Defaults to 00:00'
    )
    create_parser.add_argument(
        '--end-time',
        default="23:59",
        help='End time in HH:MM format (24-hour). Defaults to 23:59'
    )
    create_parser.add_argument(
        '--attendees',
        help='Comma-separated list of attendee email addresses'
    )
    for arg, kwargs in calendar_args.items():
        create_parser.add_argument(arg, **kwargs)
    create_parser.set_defaults(func=create_single_event)

    # Parser for the 'from-sheet' command
    sheet_parser = subparsers.add_parser(
        'from-sheet',
        help='Create events from a CSV file',
        description="""
Create multiple calendar events from a CSV file. The CSV must contain these columns:
- Country (optional): Country name (will be ignored)
- Title (required): Event title
- Date (required): Event date in YYYY-MM-DD format
- Timezone (required): Timezone for the event
        """
    )
    sheet_parser.add_argument(
        'file',
        help='Path to the CSV file containing event details'
    )
    sheet_parser.add_argument(
        '--timezone',
        default="UTC",
        help='Default timezone for events missing timezone. Defaults to UTC'
    )
    for arg, kwargs in calendar_args.items():
        sheet_parser.add_argument(arg, **kwargs)
    sheet_parser.set_defaults(func=create_from_sheet)

    # Parse arguments and call the appropriate function
    args = parser.parse_args()
    args.func(args)

if __name__ == '__main__':
    main() 