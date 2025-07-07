from bs4 import BeautifulSoup
import re


def extract_data_content(html):
    soup = BeautifulSoup(html, "html.parser")

    # Try to find tables first
    tables = [str(tag) for tag in soup.find_all("table")]
    if tables:
        return "\n\n".join(list(tables))  # Return just the first/main table

    # Look for div-based table structures
    table_like = soup.find_all("div", {"role": "table"}) or soup.find_all(
        "div", class_=re.compile(r"table|grid|data")
    )

    if table_like:
        return str(table_like[0])

    # Return full HTML if no clear table structure
    return html


def remove_stealth_artifacts(html):
    # Remove repeated "word" patterns
    html = re.sub(r"\bword\s+(?:word\s+){10,}", "", html, flags=re.IGNORECASE)

    # Remove font fingerprinting strings
    html = re.sub(
        r"mmMwWLliI0fiflO&amp;1(?:<br/>|<br>|\s)*", "", html, flags=re.IGNORECASE
    )
    html = re.sub(r"mmMwWLliI0fiflO&1(?:<br/>|<br>|\s)*", "", html, flags=re.IGNORECASE)

    # Remove other common stealth patterns
    stealth_patterns = [
        r"(?:word\s+){20,}",
        r"(?:test\s+){10,}",
        r"(?:a\s+){50,}",
        r"mmMwWLliI0fiflO.*?(?:<br/>|$)",
    ]

    for pattern in stealth_patterns:
        html = re.sub(pattern, "", html, flags=re.IGNORECASE | re.MULTILINE)

    return html


def comprehensive_clean(html):
    # Remove stealth artifacts first
    html = remove_stealth_artifacts(html)

    soup = BeautifulSoup(html, "html.parser")

    # Remove stealth/tracking elements
    stealth_selectors = [
        'iframe[id*="gsi_"]',
        'div[id*="one-tap"]',
        'div[id*="fpjs"]',
        'div[id*="warp-metadata"]',
    ]

    for selector in stealth_selectors:
        for element in soup.select(selector):
            element.decompose()

    # Remove empty elements that might contain stealth content
    for element in soup.find_all():
        if not element.get_text().strip() and not element.find_all(
            ["input", "button", "img"]
        ):
            element.decompose()

    return str(soup)


def clean_html_for_llm_v2(html_content):

    html_content = comprehensive_clean(html=html_content)
    soup = BeautifulSoup(html_content, "html.parser")

    # Remove unnecessary tags
    for tag in soup(
        ["script", "style", "meta", "link", "noscript", "footer", "video", "audio"]
    ):
        tag.decompose()

    # Remove all class and style attributes
    for tag in soup.find_all():
        tag.attrs = {
            k: v
            for k, v in tag.attrs.items()
            if k
            in [
                "id",
                "name",
                "type",
                "for",
                "href",
                "value",
                "placeholder",
                "data-testid",
            ]
        }

    # Unwrap unnecessary containers
    for tag in soup.find_all(["div", "span"]):
        if not tag.attrs and len(tag.find_all()) <= 1:
            tag.unwrap()

    # Replace i18n strings with text
    for i18n in soup.find_all("i18n-string"):
        i18n.replace_with(i18n.get_text())

    return str(soup)
