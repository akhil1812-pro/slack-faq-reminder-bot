from django.contrib import admin
from django.urls import path, include
from events.views import SlashCommandView, Events, InteractionView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('events.urls')),  # Optional if you have other routes
    path('slack/events/', Events.as_view(), name='slack-events'),
    path('slack/commands/', SlashCommandView.as_view(), name='slash-command'),  # ✅ fixed
    path('slack/interactions/', InteractionView.as_view(), name='slack-interactions'),
]