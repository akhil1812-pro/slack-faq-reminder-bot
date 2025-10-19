from django.urls import path
from .views import Events, OAuthRedirectView, SlashCommandView, InteractionView

urlpatterns = [
    path('events/', Events.as_view(), name='slack-events'),
    path('commands/', SlashCommandView.as_view(), name='slack-commands'),
    path('interact/', InteractionView.as_view(), name='slack-interact'),
    path('oauth_redirect/', OAuthRedirectView.as_view(), name='slack-oauth-redirect'),
]