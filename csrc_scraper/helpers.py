import re


def condense_inner_whitespace(text: str) -> str:
    return re.sub(r'\s+', ' ', text).strip()


def remove_newlines(text: str) -> str:
    return text.replace('\n', '').strip()
