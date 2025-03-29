__all__ = ["find_value", "extract_text", "extract_sibling_text"]

import re

from bs4 import BeautifulSoup


# --------------------------------------------------
def find_value(label: str, soup: BeautifulSoup) -> str:
    """Finds the value next to a label in the HTML."""
    element = soup.find(text=label)
    if element:
        value = element.find_next("b").text.strip()
        return value.split()[0]  # Toma solo la primera parte del valor
    return ""


# --------------------------------------------------
def extract_text(selector: str, soup: BeautifulSoup) -> str:
    """Extracts text from the HTML using a CSS selector."""
    elem = soup.select_one(selector)
    return elem.get_text(strip=True) if elem else ""


def extract_sibling_text(
    label,
    soup: BeautifulSoup,
    tag_name="b",
):
    """
    Searches for a specific tag (default is <b>) containing the given label text
    and returns the following sibling text.

    :param label: The label text to search for.
    :param tag_name: The type of tag to search within (default is "b").
    :return: The text associated with the label or None if not found.
    """
    tag = soup.find(tag_name, string=re.compile(label, re.IGNORECASE))
    if tag and tag.next_sibling:
        return tag.next_sibling.strip()
    return None
