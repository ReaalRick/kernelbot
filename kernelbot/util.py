"""Utility helpers for kernelbot."""


def split_string(text, chars_per_string):
    """Split text into chunks of at most `chars_per_string` characters."""
    return [text[i:i + chars_per_string] for i in range(0, len(text), chars_per_string)]


def smart_split(text, chars_per_string=3000):
    """Split text preferring '\\n', '. ' and ' ' boundaries."""
    if len(text) <= chars_per_string:
        return [text]

    parts = []
    remaining = text
    while len(remaining) > chars_per_string:
        chunk = remaining[:chars_per_string]
        for sep in ("\n", ". ", " "):
            idx = chunk.rfind(sep)
            if idx != -1:
                chunk = remaining[:idx + len(sep)]
                break
        parts.append(chunk)
        remaining = remaining[len(chunk):]
    if remaining:
        parts.append(remaining)
    return parts
