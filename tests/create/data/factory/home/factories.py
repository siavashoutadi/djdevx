import factory
from factory.django import DjangoModelFactory


class PostFactory(DjangoModelFactory):
    class Meta:
        model = "home.Post"
        django_get_or_create = ("slug",)

    title = factory.Faker("sentence")
    slug = factory.Faker("slug")
    body = factory.Faker("paragraph", nb_sentences=3)
    status = factory.Iterator(["draft", "published"])
    is_active = False
    author = factory.SubFactory("users.UserFactory")

    @factory.post_generation
    def tags(self, create, extracted, **kwargs):
        if not create:
            return
        if extracted:
            for item in extracted:
                self.tags.add(item)
