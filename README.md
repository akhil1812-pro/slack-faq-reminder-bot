# Slack Assistant Bot 🤖

A Django-powered Slack bot that handles reminders, check-ins, and dynamic FAQs for teams.

## 🚀 Features

- 💬 Dynamic FAQ system powered by Django admin
- ✅ Smart reminders triggered by keywords or buttons
- 👋 Onboarding flow for new users
- 🎯 Slash command support
- `/mybot remind` — Schedule smart reminders like “remind me to stretch in 30 minutes”
- `/mybot faq` — Ask HR-style questions like “leave policy” or “salary credit date”
- `/mybot list faqs` — View all available FAQ topics
- `/mybot checkin` — Send a mood check-in with interactive buttons


## 🛠️ Setup Instructions

1. **Clone the repo**  
   ```bash
   git clone https://github.com/akhil1812-pro/slack-bot.git
   cd slack-bot

2. **Create a virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt

4. **- Create a .env file, add the following environment variables:**
   ```bash
   SLACK_CLIENT_ID=your_client_id
   SLACK_CLIENT_SECRET=your_client_secret
   SLACK_VERIFICATION_TOKEN=your_verification_token
   SLACK_BOT_USER_TOKEN=your_bot_token

5. **Run the server**
   ```bash
   python manage.py runserver

