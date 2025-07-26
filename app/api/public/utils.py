import re


def slugify(text: str) -> str:
    # Lowercase, replace non-alphanumeric chars with hyphens, strip hyphens at ends
    slug = re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")
    return slug or "project"
