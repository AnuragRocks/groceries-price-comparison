// DOM Elements
const searchInput = document.getElementById('searchInput');
const searchBtn = document.getElementById('searchBtn');
const clearBtn = document.getElementById('clearBtn');
const resultsSection = document.getElementById('resultsSection');
const resultsTitle = document.getElementById('resultsTitle');
const resultsCount = document.getElementById('resultsCount');
const resultsGrid = document.getElementById('resultsGrid');
const loadingState = document.getElementById('loadingState');
const emptyState = document.getElementById('emptyState');
const errorState = document.getElementById('errorState');
const errorMessage = document.getElementById('errorMessage');
const refreshBtn = document.getElementById('refreshBtn');
const categoryChips = document.querySelectorAll('.category-chip');

// Best Deal Card Elements
const bestDealCard = document.getElementById('bestDealCard');
const bestDealName = document.getElementById('bestDealName');
const bestDealPrice = document.getElementById('bestDealPrice');
const bestDealStore = document.getElementById('bestDealStore');
const bestDealQuantity = document.getElementById('bestDealQuantity');
const bestDealBrand = document.getElementById('bestDealBrand');

// Event Listeners
searchBtn.addEventListener('click', performSearch);
searchInput.addEventListener('keypress', (e) => {
    if (e.key === 'Enter') {
        performSearch();
    }
});

searchInput.addEventListener('input', () => {
    if (searchInput.value.trim()) {
        clearBtn.style.display = 'flex';
    } else {
        clearBtn.style.display = 'none';
    }
});

clearBtn.addEventListener('click', () => {
    searchInput.value = '';
    clearBtn.style.display = 'none';
    searchInput.focus();
});

categoryChips.forEach(chip => {
    chip.addEventListener('click', () => {
        const category = chip.dataset.category;
        searchInput.value = category;
        clearBtn.style.display = 'flex';
        performSearch();
    });
});

refreshBtn.addEventListener('click', refreshData);

// Functions
async function performSearch() {
    const searchTerm = searchInput.value.trim();
    
    if (!searchTerm) {
        return;
    }

    const sortBy = document.querySelector('input[name="sort"]:checked').value;

    // Show loading state
    hideAllStates();
    loadingState.style.display = 'block';
    scrollToResults();

    try {
        const response = await fetch('/search', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                search_term: searchTerm,
                sort_by: sortBy
            })
        });

        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.error || 'Search failed');
        }

        const data = await response.json();
        displayResults(data);
    } catch (error) {
        showError(error.message);
    }
}

function displayResults(data) {
    hideAllStates();

    const { results, count, search_term } = data;

    if (!results || results.length === 0) {
        showError(`No products found matching "${search_term}"`);
        return;
    }

    // Update header
    resultsTitle.textContent = `Results for "${search_term}"`;
    resultsCount.textContent = `${count} ${count === 1 ? 'result' : 'results'}`;

    // Display best deal
    const bestDeal = results[0];
    bestDealName.textContent = bestDeal.product_name;
    bestDealPrice.textContent = bestDeal.price_display;
    bestDealStore.textContent = bestDeal.store;
    
    const quantityText = bestDeal.quantity !== 'N/A' && bestDeal.unit !== 'N/A' 
        ? `${bestDeal.quantity} ${bestDeal.unit}` 
        : '';
    bestDealQuantity.textContent = quantityText;
    
    const brandText = bestDeal.brand !== 'N/A' ? bestDeal.brand : '';
    bestDealBrand.textContent = brandText;

    // Make best deal card clickable
    bestDealCard.onclick = null; // Remove previous handler
    if (bestDeal.product_url) {
        bestDealCard.style.cursor = 'pointer';
        bestDealCard.onclick = () => {
            window.open(bestDeal.product_url, '_blank');
        };
    } else {
        bestDealCard.style.cursor = 'default';
    }

    // Display other results
    resultsGrid.innerHTML = '';
    
    // Show remaining results (skip first one as it's in best deal card)
    const remainingResults = results.slice(1);
    
    remainingResults.forEach((product, index) => {
        const card = createProductCard(product, index + 2); // +2 because we start from #2
        resultsGrid.appendChild(card);
    });

    resultsSection.style.display = 'block';
    scrollToResults();
}

function createProductCard(product, rank) {
    const card = document.createElement('a');
    card.className = 'product-card';
    
    // Set link if product URL exists
    if (product.product_url) {
        card.href = product.product_url;
        card.target = '_blank';
        card.rel = 'noopener noreferrer';
    } else {
        card.href = '#';
        card.onclick = (e) => e.preventDefault();
        card.style.cursor = 'default';
    }

    const rankBadge = `<div class="product-rank">#${rank}</div>`;
    
    const productName = `<div class="product-name">${escapeHtml(product.product_name)}</div>`;
    
    const price = `<div class="product-price">${escapeHtml(product.price_display)}</div>`;
    
    let details = '<div class="product-details">';
    
    if (product.quantity !== 'N/A' && product.unit !== 'N/A') {
        details += `
            <div class="product-detail">
                <span class="detail-label">Quantity:</span>
                <span>${escapeHtml(product.quantity)} ${escapeHtml(product.unit)}</span>
            </div>
        `;
    }
    
    if (product.unit_price !== 'N/A') {
        details += `
            <div class="product-detail">
                <span class="detail-label">Unit Price:</span>
                <span>${escapeHtml(product.unit_price)}/100g</span>
            </div>
        `;
    }
    
    if (product.brand !== 'N/A') {
        details += `
            <div class="product-detail">
                <span class="detail-label">Brand:</span>
                <span>${escapeHtml(product.brand)}</span>
            </div>
        `;
    }
    
    details += '</div>';
    
    const store = `<div class="product-store">${escapeHtml(product.store)}</div>`;
    
    const linkIndicator = product.product_url ? `
        <div class="product-link-indicator">
            <svg width="14" height="14" viewBox="0 0 16 16" fill="none">
                <path d="M6 12L10 8L6 4" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
            </svg>
            View on Flipp
        </div>
    ` : '';
    
    card.innerHTML = rankBadge + productName + price + details + store + linkIndicator;
    
    return card;
}

function hideAllStates() {
    loadingState.style.display = 'none';
    emptyState.style.display = 'none';
    errorState.style.display = 'none';
    resultsSection.style.display = 'none';
}

function showError(message) {
    hideAllStates();
    errorMessage.textContent = message;
    errorState.style.display = 'block';
    scrollToResults();
}

function scrollToResults() {
    setTimeout(() => {
        const searchSection = document.querySelector('.search-section');
        const offset = searchSection.offsetTop + searchSection.offsetHeight;
        window.scrollTo({
            top: offset - 20,
            behavior: 'smooth'
        });
    }, 100);
}

async function refreshData() {
    refreshBtn.disabled = true;
    refreshBtn.innerHTML = `
        <svg width="16" height="16" viewBox="0 0 16 16" fill="none" class="spin-animation">
            <path d="M14 8C14 11.3137 11.3137 14 8 14C4.68629 14 2 11.3137 2 8C2 4.68629 4.68629 2 8 2C9.84873 2 11.5102 2.81975 12.6365 4.10547M12.6365 4.10547V1M12.6365 4.10547H9.5" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>
        </svg>
        Refreshing...
    `;

    try {
        const response = await fetch('/refresh-data', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            }
        });

        const data = await response.json();
        
        if (data.success) {
            // Show success message
            alert(`Data refreshed successfully! ${data.product_count} products loaded.`);
            
            // Reload page to update categories
            location.reload();
        }
    } catch (error) {
        alert('Failed to refresh data. Please try again.');
    } finally {
        refreshBtn.disabled = false;
        refreshBtn.innerHTML = `
            <svg width="16" height="16" viewBox="0 0 16 16" fill="none">
                <path d="M14 8C14 11.3137 11.3137 14 8 14C4.68629 14 2 11.3137 2 8C2 4.68629 4.68629 2 8 2C9.84873 2 11.5102 2.81975 12.6365 4.10547M12.6365 4.10547V1M12.6365 4.10547H9.5" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>
            </svg>
            Refresh Data
        `;
    }
}

function escapeHtml(text) {
    const map = {
        '&': '&amp;',
        '<': '&lt;',
        '>': '&gt;',
        '"': '&quot;',
        "'": '&#039;'
    };
    return String(text).replace(/[&<>"']/g, m => map[m]);
}

// Add spin animation style
const style = document.createElement('style');
style.textContent = `
    .spin-animation {
        animation: spin 1s linear infinite;
    }
    @keyframes spin {
        to { transform: rotate(360deg); }
    }
`;
document.head.appendChild(style);
