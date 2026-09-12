from django.contrib import admin
from .models import Category, Tag, Project, ProjectImage, Donation


admin.site.register(Category)
admin.site.register(Tag)
admin.site.register(Project)
admin.site.register(ProjectImage)
admin.site.register(Donation)