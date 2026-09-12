from django.urls import path
from . import views

urlpatterns = [
    path("", views.project_list, name="project_list"),
    path("create/", views.project_create, name="project_create"),
    path("<int:pk>/", views.project_detail, name="project_detail"),
    path("<int:pk>/donate/", views.donate, name="donate"),
    path("<int:pk>/comment/", views.add_comment, name="add_comment"),
    path("<int:pk>/rate/", views.add_rating, name="add_rating"),
    path("<int:pk>/report/", views.report_project, name="report_project"),
    path("<int:pk>/cancel/", views.cancel_project, name="cancel_project"),
    path("<int:pk>/comment/<int:comment_id>/reply/", views.add_reply, name="add_reply"),
    path("<int:pk>/comment/<int:comment_id>/report/", views.report_comment, name="report_comment"),
]