import re


class LoadTagManager:
    """Utility for adding/removing Django template {% load %} tags."""

    @staticmethod
    def add_load_tag(content: str, tag: str) -> str:
        """Add a tag to an existing {% load %} statement.

        Uses regex to check if the tag already exists (load.*TAG).
        If not found, inserts the tag inline into the first {% load %} statement.
        If no {% load %} statement exists, prepends {% load TAG %} at the top.
        """
        if re.search(rf"\{{%\s*load\s+[^%]*\b{re.escape(tag)}\b[^%]*%\}}", content):
            return content

        load_re = re.compile(r"\{%\s*load\s+([^%]*?)%\}")
        m = load_re.search(content)
        if m:
            existing = m.group(1).strip()
            replacement = f"{{% load {existing} {tag} %}}"
            return content[: m.start()] + replacement + content[m.end() :]

        return f"{{% load {tag} %}}\n{content}"

    @staticmethod
    def remove_load_tag(content: str, tag: str) -> str:
        """Remove a tag from {% load %} statements.

        If the tag is the only one on a line, removes the entire line.
        If other tags remain, only removes the specified tag.
        """
        lines = content.split("\n")
        new_lines = []

        for line in lines:
            m = re.search(r"\{%\s*load\s+([^%]*?)%\}", line)
            if not m:
                new_lines.append(line)
                continue

            tags = m.group(1).strip().split()
            if tag not in tags:
                new_lines.append(line)
                continue

            tags.remove(tag)
            if not tags:
                continue

            new_line = (
                line[: m.start()]
                + "{% load "
                + " ".join(tags)
                + " %}"
                + line[m.end() :]
            )
            new_lines.append(new_line)

        return "\n".join(new_lines)
