import factory
from django.contrib.auth import get_user_model
from factory.django import DjangoModelFactory


class UserFactory(DjangoModelFactory):
    class Meta:
        model = get_user_model()
        django_get_or_create = ("username",)

    username = factory.Faker("user_name")
    email = factory.LazyAttribute(lambda obj: f"{obj.username}@example.com")
    password = factory.PostGenerationMethodCall("set_password", "user@123")

    first_name = factory.Faker("first_name")
    last_name = factory.Faker("last_name")
    is_active = True
    is_staff = False
    is_superuser = False

    @classmethod
    def create_superuser(cls, **kwargs):
        kwargs.update(
            {
                "username": "admin",
                "email": "admin@example.com",
                "password": factory.PostGenerationMethodCall(
                    "set_password", "admin@123"
                ),
                "is_staff": True,
                "is_superuser": True,
            }
        )
        return cls.create(**kwargs)
