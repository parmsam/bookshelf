#!/usr/bin/env python3
"""Build script that parses README.md and generates an interactive bookshelf website using FastHTML."""

import json
import re
from pathlib import Path

from fasthtml.common import (
    Html, Head, Body, Title, Meta, Style, Script,
    Div, H1, P, A, Button, Input, Header, Span,
    to_xml
)


def parse_books(readme_path: Path) -> list[dict]:
    """Extract book entries from README.md."""
    content = readme_path.read_text()
    books = []

    pattern = r'^\s*-\s*\[(.+?)\]\((.+?)\)\s*$'

    for line in content.split('\n'):
        match = re.match(pattern, line)
        if match:
            full_text = match.group(1)
            url = match.group(2)

            if ' by ' in full_text:
                parts = full_text.rsplit(' by ', 1)
                title = parts[0]
                author = parts[1]
            else:
                title = full_text
                author = 'Unknown'

            books.append({
                'title': title,
                'author': author,
                'url': url
            })

    return books


CSS = """
* {
    box-sizing: border-box;
    margin: 0;
    padding: 0;
}

body {
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, sans-serif;
    background: #f8f9fa;
    color: #333;
    line-height: 1.6;
    min-height: 100vh;
}

.container {
    max-width: 1200px;
    margin: 0 auto;
    padding: 2rem;
}

header {
    text-align: center;
    margin-bottom: 2rem;
}

h1 {
    font-size: 2.5rem;
    font-weight: 600;
    color: #1a1a2e;
    margin-bottom: 1.5rem;
}

.controls {
    display: flex;
    flex-wrap: wrap;
    gap: 1rem;
    justify-content: center;
    align-items: center;
    margin-bottom: 2rem;
}

.search-box {
    flex: 1;
    min-width: 250px;
    max-width: 400px;
}

.search-box input {
    width: 100%;
    padding: 0.75rem 1rem;
    font-size: 1rem;
    border: 2px solid #e0e0e0;
    border-radius: 8px;
    outline: none;
    transition: border-color 0.2s;
}

.search-box input:focus {
    border-color: #4a6fa5;
}

.view-toggles {
    display: flex;
    gap: 0.5rem;
}

.view-btn {
    padding: 0.5rem 1rem;
    font-size: 0.875rem;
    border: 2px solid #e0e0e0;
    background: white;
    border-radius: 6px;
    cursor: pointer;
    transition: all 0.2s;
}

.view-btn:hover {
    border-color: #4a6fa5;
}

.view-btn.active {
    background: #4a6fa5;
    border-color: #4a6fa5;
    color: white;
}

.book-count {
    color: #666;
    font-size: 0.875rem;
}

.books-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
    gap: 1.5rem;
}

.book-card {
    background: white;
    border-radius: 12px;
    padding: 1.5rem;
    box-shadow: 0 2px 8px rgba(0,0,0,0.08);
    transition: transform 0.2s, box-shadow 0.2s;
}

.book-card:hover {
    transform: translateY(-2px);
    box-shadow: 0 4px 16px rgba(0,0,0,0.12);
}

.book-card .title {
    font-size: 1.1rem;
    font-weight: 600;
    color: #1a1a2e;
    margin-bottom: 0.5rem;
}

.book-card .author {
    color: #666;
    font-size: 0.9rem;
    margin-bottom: 1rem;
}

.book-card .link {
    display: inline-block;
    color: #4a6fa5;
    text-decoration: none;
    font-size: 0.875rem;
    font-weight: 500;
}

.book-card .link:hover {
    text-decoration: underline;
}

.books-list {
    display: flex;
    flex-direction: column;
    gap: 1rem;
}

.books-list .book-card {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 1rem 1.5rem;
}

.books-list .book-info {
    display: flex;
    align-items: baseline;
    gap: 1rem;
    flex-wrap: wrap;
}

.books-list .title {
    margin-bottom: 0;
}

.books-list .author {
    margin-bottom: 0;
}

.books-compact {
    display: flex;
    flex-direction: column;
    gap: 0.5rem;
}

.books-compact .book-card {
    display: flex;
    align-items: center;
    gap: 1rem;
    padding: 0.75rem 1rem;
    border-radius: 8px;
}

.books-compact .title {
    font-size: 1rem;
    margin-bottom: 0;
}

.books-compact .author {
    font-size: 0.85rem;
    margin-bottom: 0;
    white-space: nowrap;
}

.books-compact .link {
    margin-left: auto;
    white-space: nowrap;
}

.hidden {
    display: none !important;
}

.no-results {
    text-align: center;
    padding: 3rem;
    color: #666;
}

@media (max-width: 600px) {
    .container {
        padding: 1rem;
    }

    h1 {
        font-size: 1.75rem;
    }

    .controls {
        flex-direction: column;
    }

    .search-box {
        width: 100%;
        max-width: none;
    }

    .books-list .book-card,
    .books-compact .book-card {
        flex-direction: column;
        align-items: flex-start;
        gap: 0.5rem;
    }

    .books-list .book-info {
        flex-direction: column;
        gap: 0.25rem;
    }

    .books-compact .link {
        margin-left: 0;
    }
}
"""


def get_js(books_json: str) -> str:
    return f"""
const books = {books_json};

let currentView = localStorage.getItem('bookshelf-view') || 'card';
let searchTimeout = null;

function escapeHtml(text) {{
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}}

function renderBooks(filteredBooks) {{
    const container = document.getElementById('books');
    const noResults = document.getElementById('no-results');
    const countEl = document.getElementById('count');

    countEl.textContent = filteredBooks.length;

    if (filteredBooks.length === 0) {{
        container.innerHTML = '';
        noResults.classList.remove('hidden');
        return;
    }}

    noResults.classList.add('hidden');

    container.innerHTML = filteredBooks.map(book => {{
        if (currentView === 'card') {{
            return `
                <div class="book-card">
                    <div class="title">${{escapeHtml(book.title)}}</div>
                    <div class="author">${{escapeHtml(book.author)}}</div>
                    <a href="${{escapeHtml(book.url)}}" class="link" target="_blank" rel="noopener">View Resource &rarr;</a>
                </div>
            `;
        }} else if (currentView === 'list') {{
            return `
                <div class="book-card">
                    <div class="book-info">
                        <div class="title">${{escapeHtml(book.title)}}</div>
                        <div class="author">${{escapeHtml(book.author)}}</div>
                    </div>
                    <a href="${{escapeHtml(book.url)}}" class="link" target="_blank" rel="noopener">View &rarr;</a>
                </div>
            `;
        }} else {{
            return `
                <div class="book-card">
                    <div class="title">${{escapeHtml(book.title)}}</div>
                    <div class="author">${{escapeHtml(book.author)}}</div>
                    <a href="${{escapeHtml(book.url)}}" class="link" target="_blank" rel="noopener">View</a>
                </div>
            `;
        }}
    }}).join('');
}}

function filterBooks(query) {{
    if (!query) return books;
    const lower = query.toLowerCase();
    return books.filter(book =>
        book.title.toLowerCase().includes(lower) ||
        book.author.toLowerCase().includes(lower)
    );
}}

function setView(view) {{
    currentView = view;
    localStorage.setItem('bookshelf-view', view);

    const container = document.getElementById('books');
    container.className = view === 'card' ? 'books-grid' :
                          view === 'list' ? 'books-list' : 'books-compact';

    document.querySelectorAll('.view-btn').forEach(btn => {{
        btn.classList.toggle('active', btn.dataset.view === view);
    }});

    const query = document.getElementById('search').value;
    renderBooks(filterBooks(query));
}}

document.getElementById('search').addEventListener('input', (e) => {{
    clearTimeout(searchTimeout);
    searchTimeout = setTimeout(() => {{
        renderBooks(filterBooks(e.target.value));
    }}, 150);
}});

document.querySelectorAll('.view-btn').forEach(btn => {{
    btn.addEventListener('click', () => setView(btn.dataset.view));
}});

setView(currentView);
"""


def generate_html(books: list[dict]) -> str:
    """Generate the complete HTML page using FastHTML components."""
    books_json = json.dumps(books)

    page = Html(
        Head(
            Meta(charset="UTF-8"),
            Meta(name="viewport", content="width=device-width, initial-scale=1.0"),
            Title("Bookshelf"),
            Style(CSS)
        ),
        Body(
            Div(
                Header(H1("Bookshelf")),
                Div(
                    Div(
                        Input(
                            type="text",
                            id="search",
                            placeholder="Search by title or author...",
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
                    cls="controls"
                ),
                P(Span(str(len(books)), id="count"), " books", cls="book-count"),
                Div(id="books", cls="books-grid"),
                Div("No books found matching your search.", id="no-results", cls="no-results hidden"),
                Script(get_js(books_json)),
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
