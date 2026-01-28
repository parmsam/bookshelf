#!/usr/bin/env python3
"""Build script that parses README.md and generates an interactive bookshelf website using FastHTML."""

import json
import re
from pathlib import Path

from fasthtml.common import (
    Html, Head, Body, Title, Meta, Link, Script,
    Div, H1, P, Button, Input, Header, Span,
    to_xml
)


def parse_books(readme_path: Path) -> list[dict]:
    """Extract book entries from README.md."""
    content = readme_path.read_text()
    books = []

    # Pattern for anchor tag format with optional hashtags
    anchor_pattern = r'^\s*-\s*<a href="(.+?)">(.+?)</a>\s*((?:#\w+\s*)*)\s*$'
    # Pattern for markdown link format (for backwards compatibility)
    markdown_pattern = r'^\s*-\s*\[(.+?)\]\((.+?)\)\s*((?:#\w+\s*)*)\s*$'

    for line in content.split('\n'):
        # Try anchor tag format first
        match = re.match(anchor_pattern, line)
        if match:
            url = match.group(1)
            full_text = match.group(2)
            tags_str = match.group(3).strip()
        else:
            # Fall back to markdown format
            match = re.match(markdown_pattern, line)
            if match:
                full_text = match.group(1)
                url = match.group(2)
                tags_str = match.group(3).strip()
            else:
                continue

        # Parse title and author
        if ' by ' in full_text:
            parts = full_text.rsplit(' by ', 1)
            title = parts[0]
            author = parts[1]
        else:
            title = full_text
            author = 'Unknown'

        # Parse tags
        tags = []
        if tags_str:
            tags = [tag.strip('#') for tag in tags_str.split() if tag.startswith('#')]

        books.append({
            'title': title,
            'author': author,
            'url': url,
            'tags': tags
        })

    return books


def generate_html(books: list[dict]) -> str:
    """Generate the complete HTML page using FastHTML components."""
    books_json = json.dumps(books)

    page = Html(
        Head(
            Meta(charset="UTF-8"),
            Meta(name="viewport", content="width=device-width, initial-scale=1.0"),
            Title("Bookshelf"),
            Link(rel="stylesheet", href="static/styles.css")
        ),
        Body(
            Div(
                Header(H1("Bookshelf")),
                Div(
                    Div(
                        Input(
                            type="text",
                            id="search",
                            placeholder="Search by title, author, or tags...",
                            autocomplete="off"
                        ),
                        cls="search-box"
                    ),
                    Div(
                        Button("Card", cls="view-btn active", data_view="card"),
                        Button("List", cls="view-btn", data_view="list"),
                        Button("Compact", cls="view-btn", data_view="compact"),
                        cls="view-toggles"
                    ),
                    Button("Reverse", cls="reverse-btn", id="reverse-btn"),
                    cls="controls"
                ),
                P(Span(str(len(books)), id="count"), " books", cls="book-count"),
                Div(id="books", cls="books-grid"),
                Div("No books found matching your search.", id="no-results", cls="no-results hidden"),
                Script(f"const books = {books_json};"),
                Script(src="static/app.js"),
                cls="container"
            )
        ),
        lang="en"
    )

    return to_xml(page)


def main():
    script_dir = Path(__file__).parent
    project_root = script_dir.parent
    readme_path = project_root / 'README.md'
    output_path = project_root / 'index.html'

    print(f'Parsing {readme_path}...')
    books = parse_books(readme_path)
    print(f'Found {len(books)} books')

    html = generate_html(books)
    output_path.write_text(html)
    print(f'Generated {output_path}')


if __name__ == '__main__':
    main()
