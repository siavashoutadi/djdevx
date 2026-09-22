import factory
from factory.django import DjangoModelFactory


class PostFactory(DjangoModelFactory):
    class Meta:
        model = "home.Post"

    title = factory.Faker("sentence")
    author = factory.SubFactory("users.UserFactory")


class CommentFactory(DjangoModelFactory):
    class Meta:
        model = "home.Comment"

    post = factory.SubFactory("home.PostFactory")
    author_email = factory.Faker("email")
    user = factory.SubFactory("users.UserFactory")
