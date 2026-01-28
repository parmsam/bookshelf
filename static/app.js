// Books data is injected as a global variable in the HTML

let currentView = localStorage.getItem('bookshelf-view') || 'card';
let isReversed = localStorage.getItem('bookshelf-reversed') === 'true';
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
        const tagsHtml = book.tags && book.tags.length > 0 
            ? `<div class="tags">${book.tags.map(tag => `<span class="tag">#${escapeHtml(tag)}</span>`).join('')}</div>`
            : '';
        
        if (currentView === 'card') {
            return `
                <div class="book-card">
                    <div class="title">${escapeHtml(book.title)}</div>
                    <div class="author">${escapeHtml(book.author)}</div>
                    ${tagsHtml}
                    <a href="${escapeHtml(book.url)}" class="link" target="_blank" rel="noopener">View Resource &rarr;</a>
                </div>
            `;
        } else if (currentView === 'list') {
            return `
                <div class="book-card">
                    <div class="book-info">
                        <div class="title">${escapeHtml(book.title)}</div>
                        <div class="author">${escapeHtml(book.author)}</div>
                        ${tagsHtml}
                    </div>
                    <a href="${escapeHtml(book.url)}" class="link" target="_blank" rel="noopener">View &rarr;</a>
                </div>
            `;
        } else {
            return `
                <div class="book-card">
                    <div class="title">${escapeHtml(book.title)}</div>
                    <div class="author">${escapeHtml(book.author)}</div>
                    ${tagsHtml}
                    <a href="${escapeHtml(book.url)}" class="link" target="_blank" rel="noopener">View</a>
                </div>
            `;
        }
    }).join('');
}

function filterBooks(query) {
    let result = books;
    if (query) {
        const lower = query.toLowerCase();
        result = books.filter(book => {
            const titleMatch = book.title.toLowerCase().includes(lower);
            const authorMatch = book.author.toLowerCase().includes(lower);
            const tagMatch = book.tags && book.tags.some(tag => tag.toLowerCase().includes(lower));
            return titleMatch || authorMatch || tagMatch;
        });
    }
    return isReversed ? [...result].reverse() : result;
}

function toggleReverse() {
    isReversed = !isReversed;
    localStorage.setItem('bookshelf-reversed', isReversed);
    const query = document.getElementById('search').value;
    renderBooks(filterBooks(query));
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

document.getElementById('reverse-btn').addEventListener('click', toggleReverse);

setView(currentView);
