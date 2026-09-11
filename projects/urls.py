from django.urls import path
from . import views
urlpatterns=[path('',views.home,name='home'),path('projects/create/',views.create,name='project_create'),path('projects/<int:pk>/',views.detail,name='project_detail'),path('projects/<int:pk>/donate/',views.donate,name='donate'),path('projects/<int:pk>/comment/',views.comment,name='comment'),path('projects/<int:pk>/rate/',views.rate,name='rate'),path('projects/<int:pk>/report/',views.report,name='report'),path('projects/<int:pk>/cancel/',views.cancel,name='cancel')]
