from django.db import models

# Create your models here.

from django.db import models

from django.db import models


class FAQ(models.Model):
    question = models.CharField(max_length=255, unique=True)
    answer = models.TextField()

    def __str__(self):
        return self.question
    
    from django.db import models

class Feedback(models.Model):
    user_id = models.CharField(max_length=50)
    text = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user_id} - {self.text[:30]}"

class SlackInstallation(models.Model):
    team_id = models.CharField(max_length=100, unique=True)
    team_name = models.CharField(max_length=255, null=True, blank=True)
    bot_token = models.CharField(max_length=255)
    installed_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.team_name or self.team_id}"