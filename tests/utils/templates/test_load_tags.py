"""Tests for djdevx.utils.templates.load_tags.LoadTagManager."""

from djdevx.utils.templates.load_tags import LoadTagManager


class TestAddLoadTag:
    def test_add_to_combined_load(self):
        content = "{% load i18n static %}\n<html>"
        result = LoadTagManager.add_load_tag(content, "django_htmx")
        assert "{% load i18n static django_htmx %}" in result
        assert result.count("{% load") == 1

    def test_add_to_standalone_load(self):
        content = "{% load i18n %}\n<html>"
        result = LoadTagManager.add_load_tag(content, "django_htmx")
        assert "{% load i18n django_htmx %}" in result

    def test_add_when_tag_already_exists(self):
        content = "{% load i18n django_htmx %}\n<html>"
        result = LoadTagManager.add_load_tag(content, "django_htmx")
        assert result == content

    def test_add_when_no_load_statement(self):
        content = "<html>\n<body></body>\n</html>"
        result = LoadTagManager.add_load_tag(content, "snakeoil")
        assert result.startswith("{% load snakeoil %}\n")
        assert "<html>" in result

    def test_add_preserves_rest_of_template(self):
        content = "{% load i18n static %}\n<html>\n  <body></body>\n</html>"
        result = LoadTagManager.add_load_tag(content, "snakeoil")
        assert "{% load i18n static snakeoil %}" in result
        assert "<html>" in result
        assert "<body></body>" in result


class TestRemoveLoadTag:
    def test_remove_only_tag_drops_line(self):
        content = "{% load snakeoil %}\n<html>"
        result = LoadTagManager.remove_load_tag(content, "snakeoil")
        assert "snakeoil" not in result
        assert result == "<html>"

    def test_remove_one_of_multiple_tags(self):
        content = "{% load i18n snakeoil %}\n<html>"
        result = LoadTagManager.remove_load_tag(content, "snakeoil")
        assert "{% load i18n %}" in result
        assert "snakeoil" not in result

    def test_remove_tag_not_present(self):
        content = "{% load i18n static %}\n<html>"
        result = LoadTagManager.remove_load_tag(content, "snakeoil")
        assert result == content

    def test_remove_preserves_other_content(self):
        content = "{% load i18n static snakeoil %}\n{% meta %}\n<html>"
        result = LoadTagManager.remove_load_tag(content, "snakeoil")
        assert "{% load i18n static %}" in result
        assert "{% meta %}" in result
        assert "<html>" in result

    def test_remove_from_combined_load(self):
        content = "{% load i18n static %}\n<html>"
        result = LoadTagManager.remove_load_tag(content, "static")
        assert "{% load i18n %}" in result
        assert "static" not in result.split("\n")[0]

    def test_remove_drops_blank_line(self):
        content = "line1\n{% load snakeoil %}\nline3"
        result = LoadTagManager.remove_load_tag(content, "snakeoil")
        assert result == "line1\nline3"

    def test_remove_middle_tag(self):
        content = "{% load i18n snakeoil static %}\n<html>"
        result = LoadTagManager.remove_load_tag(content, "snakeoil")
        assert "{% load i18n static %}" in result
        assert "snakeoil" not in result

    def test_remove_first_tag(self):
        content = "{% load snakeoil i18n static %}\n<html>"
        result = LoadTagManager.remove_load_tag(content, "snakeoil")
        assert "{% load i18n static %}" in result
        assert "snakeoil" not in result
