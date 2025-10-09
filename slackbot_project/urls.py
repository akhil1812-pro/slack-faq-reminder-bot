from django.contrib import admin
from django.urls import path, include
from events.views import SlashCommandView, Events  # Updated to match your app name
from events.views import InteractionView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('events.urls')),  # This includes your app's URLs
    path('slack/events/', Events.as_view(), name='slack-events'),
    path('slack/command/', SlashCommandView.as_view(), name='slash-command'),
    path('slack/interactions/', InteractionView.as_view(), name='slack-interactions'),
]