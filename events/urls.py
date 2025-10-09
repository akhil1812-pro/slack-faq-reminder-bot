from django.urls import path
from .views import Events

urlpatterns = [
    path('slack/events/', Events.as_view(), name='slack-events'),
]
