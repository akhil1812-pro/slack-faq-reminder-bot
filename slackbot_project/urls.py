from django.contrib import admin
from django.urls import path
from django.views.generic import TemplateView
from events.views import (
    SlashCommandView,
    Events,
    InteractionView,
    DirectInstallView,
    OAuthRedirectView, 
)

urlpatterns = [
    path('admin/', admin.site.urls),

    # Slack endpoints
    path('slack/events/', Events.as_view(), name='slack-events'),
    path('slack/command/', SlashCommandView.as_view(), name='slash-command'),
    path('slack/interactions/', InteractionView.as_view(), name='slack-interactions'),

    # OAuth install flow
    path('slack/install/', DirectInstallView.as_view(), name='slack-install'),
    path('slack/oauth_redirect/', OAuthRedirectView.as_view(), name='oauth-redirect'),

    # Static pages
    path('about/', TemplateView.as_view(template_name='about.html'), name='about'),

]
