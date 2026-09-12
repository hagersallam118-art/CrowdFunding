from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path("admin/", admin.site.urls),

    # Homepage بتاعتك
    path("", include("core.urls")),

    # شغل الشخص الثاني
    path("", include("projects.urls")),

    # شغل الشخص الأول
    path("", include("accounts.urls")),
]

if settings.DEBUG:
    urlpatterns += static(
        settings.MEDIA_URL,
        document_root=settings.MEDIA_ROOT
    )