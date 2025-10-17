from django.contrib import admin

# Register your models here.

from django.contrib import admin
from .models import FAQ

admin.site.register(FAQ)

from django.contrib import admin
from .models import Feedback

admin.site.register(Feedback)