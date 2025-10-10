from rest_framework.views import APIView
class SlashCommandView(APIView):
    def post(self, request, *args, **kwargs):
        logger.warning(f"Slash command received: {request.data}")

        # Optional: verify token
        if request.data.get('token') != SLACK_VERIFICATION_TOKEN:
            return Response(status=status.HTTP_403_FORBIDDEN)

        text = request.data.get('text', '').lower()
        user_id = request.data.get('user_id')
        channel_id = request.data.get('channel_id')

        reply = "I didn’t understand that. Try `/mybot help`"

        try:
            if "hi" in text:
                reply = f"Hi <@{user_id}> 👋"
            elif "help" in text:
                reply = "Try `/mybot joke`, `/mybot status`, `/mybot faq`, `/mybot remind`, or `/mybot checkin`"
            elif "joke" in text:
                reply = "Why do Java developers wear glasses? Because they don’t C#."
            elif "status" in text:
                reply = "Bot is alive and kicking! ✅"
            elif "list faqs" in text:
                faqs = FAQ.objects.all()
                if faqs:
                    reply = "*Here are the available FAQ topics:*\n"
                    for faq in faqs:
                        reply += f"• {faq.question}\n"
                else:
                    reply = "There are no FAQs available right now. Please check back later."
            elif "faq" in text:
                matched = None
                faqs = FAQ.objects.all()
                for faq in faqs:
                    if faq.question.lower() in text:
                        matched = faq.answer
                        break
                reply = matched or "❓ I couldn’t find that FAQ. Try asking about something listed in the admin panel."
            elif "remind" in text:
                parts = text.split("remind me to", 1)
                if len(parts) < 2:
                    reply = "Please use the format: `/mybot remind me to [task] in [time]`"
                else:
                    task_part = parts[1].strip()
                    if " in " in task_part:
                        task, time_phrase = task_part.rsplit(" in ", 1)
                    elif " at " in task_part:
                        task, time_phrase = task_part.rsplit(" at ", 1)
                    else:
                        return Response({"text": "Please include both the task and time, like 'remind me to stretch in 30 minutes' or 'submit report at 5:30pm'."}, status=status.HTTP_200_OK)

                    reminder_time = dateparser.parse(time_phrase.strip())
                    logger.warning(f"Parsed reminder time: {reminder_time}")

                    if not reminder_time:
                        reply = "I couldn’t understand the time. Try something like 'in 30 minutes' or 'at 5pm'."
                    else:
                        post_at = int(reminder_time.timestamp())
                        now = int(datetime.now().timestamp())
                        if post_at - now < 60:
                            post_at = now + 120
                            reply = f"Reminder set for *{task}* in 2 minutes (adjusted for safety)."
                        else:
                            reply = f"Reminder set for *{task}* at {reminder_time.strftime('%I:%M %p')}!"

                        Client.chat_scheduleMessage(channel=channel_id, text=f"⏰ Reminder: {task}", post_at=post_at)
            elif "checkin" in text:
                Client.chat_postMessage(
                    channel=channel_id,
                    text="Good morning! How are you feeling today?",
                    blocks=[
                        {
                            "type": "actions",
                            "elements": [
                                {"type": "button", "text": {"type": "plain_text", "text": "😊 Great"}, "value": "great"},
                                {"type": "button", "text": {"type": "plain_text", "text": "😐 Okay"}, "value": "okay"},
                                {"type": "button", "text": {"type": "plain_text", "text": "😞 Meh"}, "value": "meh"}
                            ]
                        }
                    ]
                )
                reply = "Check-in sent!"
        except Exception as e:
            logger.error(f"Slash command error: {e}", exc_info=True)
            reply = "Something went wrong while processing your command."

        return Response({"text": reply}, status=status.HTTP_200_OK)