"""Tests for the factory mapper (field -> factory-boy declaration logic)."""

from djdevx.create.factory_boy import mapper
from tests.create.factory_fixtures import home_comment, home_post, users_user


class TestBuildFactory:
    def test_skips_pk_and_auto_now(self):
        """Primary key and auto_now fields must not produce assignments."""
        body = mapper.build_factory(home_post())["class_body"]
        assert "id = " not in body
        assert "created_at" not in body

    def test_model_meta_ref(self):
        body = mapper.build_factory(home_post())["class_body"]
        assert 'model = "home.Post"' in body

    def test_unique_field_in_get_or_create(self):
        body = mapper.build_factory(home_post())["class_body"]
        assert 'django_get_or_create = ("slug",)' in body

    def test_choices_become_iterator(self):
        body = mapper.build_factory(home_post())["class_body"]
        assert 'status = factory.Iterator(["draft", "published"])' in body

    def test_foreign_key_becomes_subfactory(self):
        body = mapper.build_factory(home_post())["class_body"]
        assert 'author = factory.SubFactory("users.UserFactory")' in body

    def test_one_to_one_becomes_subfactory(self):
        body = mapper.build_factory(home_comment())["class_body"]
        assert 'user = factory.SubFactory("users.UserFactory")' in body

    def test_many_to_many_post_generation(self):
        body = mapper.build_factory(home_post())["class_body"]
        assert "def tags(self, create, extracted, **kwargs):" in body
        assert "self.tags.add(item)" in body

    def test_name_heuristics(self):
        body = mapper.build_factory(home_comment())["class_body"]
        assert 'author_email = factory.Faker("email")' in body

    def test_user_specials(self):
        body = mapper.build_factory(users_user())["class_body"]
        assert "model = get_user_model()" in body
        assert 'django_get_or_create = ("username", "email")' in body
        assert (
            'password = factory.PostGenerationMethodCall("set_password", "password123")'
            in body
        )
        assert "def create_superuser(cls, **kwargs):" in body

    def test_user_import_needed(self):
        info = mapper.build_factory(users_user())
        assert info["imports"] == ["from django.contrib.auth import get_user_model"]
        assert mapper.build_factory(home_post())["imports"] == []


class TestAssembleModule:
    def test_fresh_module(self):
        content, added, skipped = mapper.assemble_module([home_post()])
        assert added == ["PostFactory"]
        assert skipped == []
        assert content.startswith(
            "import factory\nfrom factory.django import DjangoModelFactory\n"
        )
        assert content.rstrip().endswith("self.tags.add(item)")

    def test_factories_separated_by_two_blank_lines(self):
        content, _, _ = mapper.assemble_module([home_post(), home_comment()])
        assert "class PostFactory" in content
        assert "class CommentFactory" in content
        # top-level classes must be separated by exactly two blank lines
        assert "\n\n\nclass CommentFactory" in content

    def test_append_merges_import_keeps_existing(self):
        existing = (
            "import factory\n"
            "from factory.django import DjangoModelFactory\n"
            "\n"
            "\n"
            "class PostFactory(DjangoModelFactory):\n"
            "    class Meta:\n"
            '        model = "home.Post"\n'
            "\n"
            '    title = factory.Faker("sentence")\n'
        )
        content, added, skipped = mapper.assemble_module(
            [users_user()], existing=existing
        )
        assert added == ["UserFactory"]
        assert skipped == []
        assert "class PostFactory" in content
        assert "class UserFactory" in content
        assert "from django.contrib.auth import get_user_model" in content
        assert "import factory" in content.split("class PostFactory")[0]

    def test_append_skips_existing_factory(self):
        existing = (
            "import factory\n"
            "from factory.django import DjangoModelFactory\n"
            "\n"
            "\n"
            "class PostFactory(DjangoModelFactory):\n"
            "    class Meta:\n"
            '        model = "home.Post"\n'
        )
        content, added, skipped = mapper.assemble_module(
            [home_post()], existing=existing
        )
        assert added == []
        assert skipped == ["PostFactory"]
        assert content == existing

    def test_module_path(self, temp_dir):
        assert (
            mapper.module_path(temp_dir, "home") == temp_dir / "home" / "factories.py"
        )
