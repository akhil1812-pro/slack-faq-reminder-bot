# 🤖 Slack FAQ & Reminder Bot

A smart Slack bot built with Django and Slack SDK that handles FAQs, reminders, check-ins, and interactive responses — perfect for teams who want quick answers and light automation inside Slack.

---

## 🚀 Features

- `/mybot help` — Lists all available commands
- `/mybot faq [topic]` — Answers company FAQs (e.g. leave policy, benefits)
- `/mybot list faqs` — Lists all available FAQ topics
- `/mybot remind me to [task] in/at [time]` — Schedules reminders
- `/mybot checkin` — Sends a mood check-in with interactive buttons
- Responds to messages like “hi”, “joke”, “status” in channels

---

## 🛠️ Tech Stack

- Django + Django REST Framework
- Slack SDK (`slack_sdk`)
- Render for deployment
- Python 3.13
- PostgreSQL (optional for storing FAQs)

---

## ⚙️ Setup Instructions

### 1. Clone the repo

```bash
git clone https://github.com/akhil1812-pro/slack-faq-reminder-bot.git
cd slack-faq-reminder-bot
```

### 2. Install dependencies

```
pip install -r requirements.txt
```

### 3. Set environment variables
Create a .env file

```
SLACK_BOT_USER_TOKEN=...
SLACK_VERIFICATION_TOKEN=...
SLACK_SIGNING_SECRET=...
```

### 4. Run locally

```
python manage.py runserver
```

---


## 🌐 Slack App Configuration

### In your Slack App dashboard:

- Slash Commands → /mybot → Request URL:
https://yourdomain.com/slack/commands/
- Interactivity & Shortcuts → Request URL:
https://yourdomain.com/slack/interactions/
- Event Subscriptions → Subscribe to message.channels →
Request URL: https://yourdomain.com/slack/events/

---


## 📦 Deployment (Render)

Set your start command:
```
gunicorn slackbot_project.wsgi:application --bind 0.0.0.0:$PORT
```
Add environment variables in Render dashboard.

---

## 🧪Example Commands

```
/mybot faq leave policy
/mybot list faqs
/mybot remind me to stretch in 30 minutes
/mybot checkin
```






