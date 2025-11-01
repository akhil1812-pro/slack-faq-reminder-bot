from rest_framework.views import APIView
from rest_framework.response import Response
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from slack_sdk.errors import SlackApiError
import os
from rest_framework import status
from django.conf import settings
from slack_sdk import WebClient
from django.shortcuts import redirect
import json
import logging
import requests
import dateparser
import re
import pytz
from datetime import datetime, timedelta
from .models import FAQ, Feedback, SlackInstallation  # ✅ Added SlackInstallation model
from urllib.parse import urlencode

# -------------------------------
# Config & constants
# -------------------------------
FAQS = {
    "leave policy": "📄 *Leave Policy*\nYou get 24 paid leaves per year. Carry forward up to 12 leaves.",
    "work from home": "🏠 *Work From Home*\nYou can work remotely up to 3 days a week with manager approval.",
    "salary": "💰 *Salary Info*\nSalary is credited on the last working day of each month.",
    "benefits": "🎁 *Benefits*\nWe offer health insurance, wellness reimbursements, and learning budgets.",
    "probation": "📝 *Probation Period*\nNew employees have a 3-month probation period with monthly reviews."
}

logger = logging.getLogger(__name__)
SLACK_VERIFICATION_TOKEN = getattr(settings, 'SLACK_VERIFICATION_TOKEN', None)
SLACK_BOT_USER_TOKEN = getattr(settings, 'SLACK_BOT_USER_TOKEN', None)


def get_slack_client(token=None):
    """Return a Slack WebClient for the given token or the default one."""
    return WebClient(token=token or SLACK_BOT_USER_TOKEN)


# -------------------------------
# OAuth Install Flow
# -------------------------------
class DirectInstallView(APIView):
    """Redirect user to Slack install page"""
    def get(self, request, *args, **kwargs):
        params = {
            "client_id": settings.SLACK_CLIENT_ID,
            "scope": "commands,chat:write,chat:write.public,users:read,channels:read,app_mentions:read",
            "redirect_uri": settings.SLACK_REDIRECT_URI,
        }
        url = "https://slack.com/oauth/v2/authorize?" + urlencode(params)
        logger.info(f"Redirecting to Slack install URL: {url}")
        return redirect(url)


class OAuthRedirectView(APIView):
    """Handles Slack OAuth redirect after install"""
    def get(self, request, *args, **kwargs):
        code = request.GET.get("code")
        if not code:
            return Response({"error": "Missing code"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            resp = requests.post(
                "https://slack.com/api/oauth.v2.access",
                data={
                    "client_id": settings.SLACK_CLIENT_ID,
                    "client_secret": settings.SLACK_CLIENT_SECRET,
                    "code": code,
                    "redirect_uri": settings.SLACK_REDIRECT_URI,
                },
                timeout=10
            )
            data = resp.json()
            logger.info(f"Slack OAuth response (without secrets): { {k:v for k,v in data.items() if 'token' not in k} }")

            if not data.get("ok"):
                return Response({"error": "OAuth failed", "details": data}, status=status.HTTP_400_BAD_REQUEST)

            bot_token = data.get("access_token") or data.get("bot", {}).get("bot_access_token")
            team_id = data.get("team", {}).get("id")
            team_name = data.get("team", {}).get("name")

            if bot_token and team_id:
                SlackInstallation.objects.update_or_create(
                    team_id=team_id,
                    defaults={"bot_token": bot_token, "team_name": team_name}
                )
                logger.info(f"✅ Saved bot token for team: {team_name} ({team_id})")

            # Optional welcome message
            try:
                client = get_slack_client(bot_token)
                client.chat_postMessage(channel="#general", text="✅ App successfully installed and ready to go!")
            except Exception as e:
                logger.warning(f"Post-install message failed: {e}")

            app_id = data.get("app_id")
            if app_id:
                return redirect(f"https://slack.com/app_redirect?app={app_id}")
            return Response({"status": "Installation successful"}, status=status.HTTP_200_OK)

        except Exception as e:
            logger.error(f"OAuth error: {e}", exc_info=True)
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# -------------------------------
# Helpers for fetching workspace token
# -------------------------------
def get_token_for_team(request):
    """Extract team_id and fetch its token from DB"""
    team_id = request.data.get("team_id") or request.data.get("team")
    if not team_id and isinstance(request.data, dict) and "event" in request.data:
        team_id = request.data.get("team_id") or request.data["event"].get("team")
    token = None
    if team_id:
        try:
            token = SlackInstallation.objects.get(team_id=team_id).bot_token
        except SlackInstallation.DoesNotExist:
            logger.warning(f"No bot token found for team {team_id}")
    return token


# -------------------------------
# Interaction View
# -------------------------------
class InteractionView(APIView):
    def post(self, request, *args, **kwargs):
        try:
            payload = json.loads(request.data.get("payload"))
            user_id = payload["user"]["id"]
            action_value = payload["actions"][0]["value"]
            channel_id = payload["channel"]["id"]
            team_id = payload.get("team", {}).get("id")

            token = None
            if team_id:
                try:
                    token = SlackInstallation.objects.get(team_id=team_id).bot_token
                except SlackInstallation.DoesNotExist:
                    logger.warning(f"No token for team {team_id}")

            client = get_slack_client(token)
            mood_map = {
                "great": "😊 Glad you're feeling great!",
                "okay": "😐 Hope your day gets better!",
                "meh": "😞 Sending good vibes your way!"
            }
            reply = mood_map.get(action_value, "Thanks for checking in!")
            client.chat_postMessage(channel=channel_id, text=f"<@{user_id}> {reply}")
            return Response(status=status.HTTP_200_OK)
        except Exception as e:
            logger.error(f"Interaction error: {e}", exc_info=True)
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# -------------------------------
# Event View
# -------------------------------
class Events(APIView):
    def post(self, request, *args, **kwargs):
        try:
            slack_message = request.data
            logger.warning(f"Incoming Slack event: {slack_message}")

            if slack_message.get("token") != SLACK_VERIFICATION_TOKEN:
                return Response(status=status.HTTP_403_FORBIDDEN)

            if slack_message.get("type") == "url_verification":
                return Response({"challenge": slack_message.get("challenge")}, status=status.HTTP_200_OK)

            event = slack_message.get("event", {})
            if not event:
                return Response(status=status.HTTP_200_OK)

            token = get_token_for_team(request)
            client = get_slack_client(token)

            # Ignore bot messages
            if event.get("bot_id") or event.get("subtype") == "bot_message":
                return Response(status=status.HTTP_200_OK)

            # Welcome new member
            if event.get("type") == "member_joined_channel":
                user = event["user"]
                channel = event["channel"]
                welcome_text = (
                    f"Hi <@{user}> 👋 Thanks for adding me!\n"
                    "Here’s what I can do:\n"
                    "• `/mybot faq [topic]`\n"
                    "• `/mybot feedback [your thoughts]`\n"
                    "• `/mybot remind me to [task] in [time]`\n"
                    "• `/mybot checkin`\n"
                    "• `/mybot help`"
                )
                client.chat_postMessage(channel=channel, text=welcome_text)
                return Response(status=status.HTTP_200_OK)

            # Respond to user messages
            user = event.get("user")
            text = event.get("text", "")
            lowered = text.lower() if isinstance(text, str) else ""

            bot_text = None
            if user and text:
                if "hello" in lowered or "start" in lowered:
                    bot_text = (
                        f"Hi <@{user}> 👋 I'm your team assistant bot!\n"
                        "Try `/mybot help` for a list of commands."
                    )
                elif "hi" in lowered:
                    bot_text = f"Hi <@{user}> 👋"
                elif "help" in lowered:
                    bot_text = (
                        "*Welcome to MyBot!* 🤖\n"
                        "• `/mybot faq [topic]`\n"
                        "• `/mybot feedback [your thoughts]`\n"
                        "• `/mybot remind me to [task] in [time]`\n"
                        "• `/mybot checkin`\n"
                        "• `/mybot joke`\n"
                        "• `/mybot status`"
                    )
                elif "joke" in lowered:
                    bot_text = "Why don’t programmers like nature? It has too many bugs. 🐛"
                elif "status" in lowered:
                    bot_text = "All systems go! ✅ I'm running smoothly."

            if bot_text:
                client.chat_postMessage(channel=event.get("channel"), text=bot_text)
            return Response(status=status.HTTP_200_OK)

        except Exception as e:
            logger.error(f"Event error: {e}", exc_info=True)
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# -------------------------------
# Slash Commands (Fixed)
# -------------------------------
@method_decorator(csrf_exempt, name='dispatch')
class SlashCommandView(APIView):
    def post(self, request, *args, **kwargs):
        logger.warning(f"Slash command received: {request.data}")

        text = (request.data.get("text") or "").strip().lower()
        user_id = request.data.get("user_id")
        channel_id = request.data.get("channel_id")

        token = get_token_for_team(request)
        client = get_slack_client(token)
        reply = "I didn’t understand that. Try `/mybot help`"

        try:
            # ---- BASIC COMMANDS ----
            if text in ["hi", "hello"]:
                reply = f"Hi <@{user_id}> 👋"

            elif text == "help":
                reply = (
                    "*Welcome to MyBot!* 🤖\n"
                    "• `/mybot faq [topic]`\n"
                    "• `/mybot feedback [your thoughts]`\n"
                    "• `/mybot remind me to [task] in [time]`\n"
                    "• `/mybot checkin`\n"
                    "• `/mybot joke`\n"
                    "• `/mybot status`"
                )

            elif text == "status":
                reply = "Bot is alive and kicking! ✅"

            elif text == "joke":
                reply = "Why do Java developers wear glasses? Because they don’t C#."

            # ---- FAQ HANDLING ----
            elif text in ["faq", "faq list", "list faqs"]:
                # Return all FAQ topics
                try:
                    faqs = FAQ.objects.all()
                    if faqs.exists():
                        faq_lines = "\n".join([f"• {f.question}" for f in faqs])
                    else:
                        faq_lines = "\n".join([f"• {k}" for k in FAQS])
                    reply = "*Here are the available FAQ topics:*\n" + faq_lines
                except Exception as e:
                    logger.warning(f"FAQ list fallback: {e}")
                    reply = "*Here are the available FAQ topics:*\n" + "\n".join([f"• {k}" for k in FAQS])

            elif text.startswith("faq "):
                # Search FAQ for a specific topic
                query = text.replace("faq", "", 1).strip()
                matched = None

                # Try database FAQs first
                try:
                    for f in FAQ.objects.all():
                        if query in f.question.lower():
                            matched = f.answer
                            break
                except Exception:
                    pass

                # Then fallback to static FAQS
                if not matched:
                    for k, v in FAQS.items():
                        if query in k or k in query:
                            matched = v
                            break

                # Default response
                reply = matched or "❓ I couldn’t find that FAQ. Try `/mybot faq list`."

            # ---- FEEDBACK ----
            elif text.startswith("feedback"):
                feedback_text = text.replace("feedback", "", 1).strip()
                if len(feedback_text) > 1:
                    Feedback.objects.create(user_id=user_id, text=feedback_text)
                    reply = "Thanks for your feedback! 🙌"
                else:
                    reply = "Please provide feedback after the command, like `/mybot feedback I love this bot!`"

            # ---- REMINDER ----
            elif "remind me to" in text:
                parts = text.split("remind me to", 1)
                if len(parts) > 1:
                    task_part = parts[1].strip()
                    if " in " in task_part:
                        task, time_phrase = task_part.rsplit(" in ", 1)
                    elif " at " in task_part:
                        task, time_phrase = task_part.rsplit(" at ", 1)
                    else:
                        reply = "Use: `/mybot remind me to [task] in [time]`"
                        return Response({"text": reply}, status=status.HTTP_200_OK)

                    time_phrase = time_phrase.strip()
                    match = re.search(r"(\d+)\s*(min|mins|minutes?)", time_phrase)
                    if match:
                        minutes = int(match.group(1))
                        reminder_time = datetime.now() + timedelta(minutes=minutes)
                    else:
                        reminder_time = dateparser.parse(time_phrase)

                    if reminder_time:
                        post_at = int(reminder_time.timestamp())
                        client.chat_scheduleMessage(channel=channel_id, text=f"⏰ Reminder: {task}", post_at=post_at)
                        reply = f"Reminder set for *{task}*! ⏰"
                    else:
                        reply = "Could not parse time."

            # ---- CHECKIN ----
            elif "checkin" in text:
                client.chat_postMessage(
                    channel=channel_id,
                    text="How are you feeling today?",
                    blocks=[{
                        "type": "actions",
                        "elements": [
                            {"type": "button", "text": {"type": "plain_text", "text": "😊 Great"}, "value": "great"},
                            {"type": "button", "text": {"type": "plain_text", "text": "😐 Okay"}, "value": "okay"},
                            {"type": "button", "text": {"type": "plain_text", "text": "😞 Meh"}, "value": "meh"}
                        ]
                    }]
                )
                reply = "Check-in sent!"

        except Exception as e:
            logger.error(f"Slash command error: {e}", exc_info=True)
            reply = "Something went wrong."

        # ✅ Always return HTTP 200 OK with text
        return Response({"text": reply}, status=status.HTTP_200_OK)

from django.contrib.auth.models import User
from django.http import HttpResponse

class CreateAdminView(APIView):
    """Temporary route to create a superuser securely (use once, then delete)."""
    def get(self, request, *args, **kwargs):
        secret = request.GET.get("secret")
        if secret != os.getenv("ADMIN_SETUP_SECRET", "mysecretkey"):
            return HttpResponse("Unauthorized", status=401)

        username = os.getenv("ADMIN_USERNAME", "admin")
        password = os.getenv("ADMIN_PASSWORD", "admin123")
        email = os.getenv("ADMIN_EMAIL", "admin@example.com")

        if not User.objects.filter(username=username).exists():
            User.objects.create_superuser(username=username, password=password, email=email)
            return HttpResponse(f"✅ Superuser '{username}' created successfully.")
        return HttpResponse("User already exists.")
