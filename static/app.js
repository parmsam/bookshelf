// Books data is injected as a global variable in the HTML

let currentView = localStorage.getItem('bookshelf-view') || 'card';
let searchTimeout = null;

function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

function renderBooks(filteredBooks) {
    const container = document.getElementById('books');
    const noResults = document.getElementById('no-results');
    const countEl = document.getElementById('count');

    countEl.textContent = filteredBooks.length;

    if (filteredBooks.length === 0) {
        container.innerHTML = '';
        noResults.classList.remove('hidden');
        return;
    }

    noResults.classList.add('hidden');

    container.innerHTML = filteredBooks.map(book => {
        if (currentView === 'card') {
            return `
                <div class="book-card">
                    <div class="title">${escapeHtml(book.title)}</div>
                    <div class="author">${escapeHtml(book.author)}</div>
                    <a href="${escapeHtml(book.url)}" class="link" target="_blank" rel="noopener">View Resource &rarr;</a>
                </div>
            `;
        } else if (currentView === 'list') {
            return `
                <div class="book-card">
                    <div class="book-info">
                        <div class="title">${escapeHtml(book.title)}</div>
                        <div class="author">${escapeHtml(book.author)}</div>
                    </div>
                    <a href="${escapeHtml(book.url)}" class="link" target="_blank" rel="noopener">View &rarr;</a>
                </div>
            `;
        } else {
            return `
                <div class="book-card">
                    <div class="title">${escapeHtml(book.title)}</div>
                    <div class="author">${escapeHtml(book.author)}</div>
                    <a href="${escapeHtml(book.url)}" class="link" target="_blank" rel="noopener">View</a>
                </div>
            `;
        }
    }).join('');
}

function filterBooks(query) {
    if (!query) return books;
    const lower = query.toLowerCase();
    return books.filter(book =>
        book.title.toLowerCase().includes(lower) ||
        book.author.toLowerCase().includes(lower)
    );
}

function setView(view) {
    currentView = view;
    localStorage.setItem('bookshelf-view', view);

    const container = document.getElementById('books');
    container.className = view === 'card' ? 'books-grid' :
                          view === 'list' ? 'books-list' : 'books-compact';

    document.querySelectorAll('.view-btn').forEach(btn => {
        btn.classList.toggle('active', btn.dataset.view === view);
    });

    const query = document.getElementById('search').value;
    renderBooks(filterBooks(query));
}

// Initialize
document.getElementById('search').addEventListener('input', (e) => {
    clearTimeout(searchTimeout);
    searchTimeout = setTimeout(() => {
        renderBooks(filterBooks(e.target.value));
    }, 150);
});

document.querySelectorAll('.view-btn').forEach(btn => {
    btn.addEventListener('click', () => setView(btn.dataset.view));
});

setView(currentView);
