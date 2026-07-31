from settings.django.base import INSTALLED_APPS

# Insert django_sp_admin before django.contrib.admin
admin_index = INSTALLED_APPS.index("django.contrib.admin")
INSTALLED_APPS.insert(admin_index, "django_sp_admin")
