import json

import pika


routing_keys = [
    "evolution.mail.*",
    "evolution.mail.*.*",
    "evolution.contacts.*",
    "evolution.contacts.*.*",
    "evolution.calendar.*",
    "chromium.*",
    "nautilus.*",
    ]
exchange_name = "app.data"
exchange_type = "topic"
params = pika.ConnectionParameters(host="localhost")
json_account_settings = {
    "imap host": "imap.example.com",
    "smtp host": "smtp.example.com",
    "user": "alice",
    "password": "s3cr3t",
    }
json_mail_notifications = [
    {"subject": "Wassup!", "from": "bff@exmaple.com"},
    {"subject": "You're fired.", "from": "boss@example.com"},
    ]
rfc2822_message = """
Delivered-To: me@example.com
Date: Tue, 28 Jun 2011 17:55:19 +0100
From: bff@example.com
Subject: Beers at the pub NOW!!!

body body body text text text long running line text text text
 long line continues long long long text text text text text 
"""
vcal_message = """
BEGIN:VCALENDAR
VERSION:2.0
PRODID:-//hacksw/handcal//NONSGML v1.0//EN
BEGIN:VEVENT
UID:uid1@example.com
DTSTAMP:19970714T170000Z
ORGANIZER;CN=John Doe:MAILTO:john.doe@example.com
DTSTART:19970714T170000Z
DTEND:19970715T035959Z
SUMMARY:Bastille Day Party
END:VEVENT
END:VCALENDAR
"""
message_data = [
    ("evolution.mail.settings.accounts", json.dumps(json_account_settings)),
    ("evolution.not.routed", "Should never see this..."),
    ("evolution.mail.notifications", json.dumps(json_mail_notifications)),
    ("evolution.mail.drafts", rfc2822_message),
    ("evolution.contacts.contact.open", vcal_message),
    ]
