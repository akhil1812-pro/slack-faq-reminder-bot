from django.contrib import admin
from django.urls import path
from events.views import SlashCommandView, Events, InteractionView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('slack/events/', Events.as_view(), name='slack-events'),
    path('slack/commands/', SlashCommandView.as_view(), name='slash-command'),
    path('slack/interactions/', InteractionView.as_view(), name='slack-interactions'),
]