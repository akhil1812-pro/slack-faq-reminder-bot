from django.contrib import admin
from .models import Feedback, FAQ, SlackInstallation

@admin.register(Feedback)
class FeedbackAdmin(admin.ModelAdmin):
    list_display = ("user_id", "text", "created_at")
    search_fields = ("user_id", "text")
    ordering = ("-created_at",)

@admin.register(FAQ)
class FAQAdmin(admin.ModelAdmin):
    list_display = ("question", "answer")

@admin.register(SlackInstallation)
class SlackInstallationAdmin(admin.ModelAdmin):
    list_display = ("team_name", "team_id", "bot_token")
