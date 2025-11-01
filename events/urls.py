from django.urls import path
from .views import Events, OAuthRedirectView, SlashCommandView, InteractionView, Events, DirectInstallView, OAuthRedirectView
from .views import DirectInstallView


urlpatterns = [
    path('events/', Events.as_view(), name='slack-events'),
    path('command/', SlashCommandView.as_view(), name='slack-command'),
    path('interact/', InteractionView.as_view(), name='slack-interact'),
    path('oauth_redirect/', OAuthRedirectView.as_view(), name='slack-oauth-redirect'),
    path('install/', DirectInstallView.as_view(), name='slack-direct-install'),
]