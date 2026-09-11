from django.contrib import admin
from .models import *
admin.site.register([Category,Tag,Project,ProjectImage,Donation,Comment,Rating,Report])
