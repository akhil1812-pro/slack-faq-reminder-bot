from django.contrib import admin
from django.urls import path, include   
from django.views.generic import TemplateView
from events.views import SlashCommandView, Events, InteractionView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('slack/events/', Events.as_view(), name='slack-events'),
    path('slack/command/', SlashCommandView.as_view(), name='slash-command'),
    path('slack/interactions/', InteractionView.as_view(), name='slack-interactions'),
    path('about/', TemplateView.as_view(template_name='about.html'), name='about'),
    path('slack/', include('events.urls')),
]