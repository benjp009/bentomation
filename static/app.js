// API Base URL
const API_BASE = window.location.origin + '/api';

// State
let currentView = 'dashboard';
let partners = [];
let links = [];
let transactions = [];

// Initialize app
document.addEventListener('DOMContentLoaded', () => {
    setupNavigation();
    loadDashboard();
});

// Navigation
function setupNavigation() {
    const navLinks = document.querySelectorAll('.nav-link');
    navLinks.forEach(link => {
        link.addEventListener('click', (e) => {
            e.preventDefault();
            const view = link.dataset.view;
            switchView(view);
        });
    });
}

function switchView(view) {
    // Update navigation
    document.querySelectorAll('.nav-link').forEach(link => {
        link.classList.remove('active');
        if (link.dataset.view === view) {
            link.classList.add('active');
        }
    });

    // Update views
    document.querySelectorAll('.view').forEach(v => {
        v.classList.remove('active');
    });
    document.getElementById(`${view}-view`).classList.add('active');

    // Load view data
    currentView = view;
    switch(view) {
        case 'dashboard':
            loadDashboard();
            break;
        case 'partners':
            loadPartners();
            break;
        case 'links':
            loadLinks();
            break;
        case 'transactions':
            loadTransactions();
            break;
    }
}

// Dashboard
async function loadDashboard() {
    try {
        const response = await fetch(`${API_BASE}/analytics/overview`);
        const data = await response.json();

        // Update stats
        document.getElementById('stat-partners').textContent = data.overview.active_partners;
        document.getElementById('stat-links').textContent = data.overview.active_links;
        document.getElementById('stat-clicks').textContent = data.overview.total_clicks;
        document.getElementById('stat-collected').textContent = `$${data.overview.total_collected}`;
        document.getElementById('stat-paid').textContent = `$${data.overview.total_paid}`;
        document.getElementById('stat-pending').textContent = `$${data.overview.pending_amount}`;

        // Update top links
        const topLinksContainer = document.getElementById('top-links');
        if (data.top_links.length === 0) {
            topLinksContainer.innerHTML = '<div class="empty-state"><p>No links yet</p></div>';
        } else {
            topLinksContainer.innerHTML = data.top_links.map(item => `
                <div class="data-item">
                    <div class="data-item-header">
                        <span class="data-item-title">${item.link.brand_name} - ${item.link.product_name || 'General'}</span>
                        <span class="data-item-value">$${item.revenue.toFixed(2)}</span>
                    </div>
                    <div class="data-item-meta">
                        ${item.link.stats.total_clicks} clicks · ${item.link.stats.conversion_rate}% conversion
                    </div>
                </div>
            `).join('');
        }

        // Update recent transactions
        const recentTransactionsContainer = document.getElementById('recent-transactions');
        if (data.recent_transactions.length === 0) {
            recentTransactionsContainer.innerHTML = '<div class="empty-state"><p>No transactions yet</p></div>';
        } else {
            recentTransactionsContainer.innerHTML = data.recent_transactions.map(t => `
                <div class="data-item">
                    <div class="data-item-header">
                        <span class="data-item-title">${t.brand_name || 'Unknown'}</span>
                        <span class="data-item-value">$${t.amount_collected}</span>
                    </div>
                    <div class="data-item-meta">
                        ${new Date(t.transaction_date).toLocaleDateString()} · ${t.status}
                    </div>
                </div>
            `).join('');
        }
    } catch (error) {
        console.error('Error loading dashboard:', error);
    }
}

// Partners
async function loadPartners() {
    try {
        const response = await fetch(`${API_BASE}/partners`);
        partners = await response.json();

        const container = document.getElementById('partners-list');
        if (partners.length === 0) {
            container.innerHTML = `
                <div class="empty-state">
                    <div class="empty-state-icon">💼</div>
                    <p class="empty-state-message">No partners yet</p>
                    <p>Add your first affiliate partner to get started</p>
                </div>
            `;
        } else {
            container.innerHTML = partners.map(partner => `
                <div class="partner-card">
                    <div class="partner-header">
                        <div>
                            <div class="partner-name">${partner.name}</div>
                            <div class="partner-platform">${partner.platform}</div>
                        </div>
                        <span class="badge ${partner.status}">${partner.status}</span>
                    </div>
                    <div class="partner-stats">
                        <div class="partner-stat">
                            <div class="partner-stat-value">${partner.total_links}</div>
                            <div class="partner-stat-label">Total Links</div>
                        </div>
                        <div class="partner-stat">
                            <div class="partner-stat-value">${partner.active_links}</div>
                            <div class="partner-stat-label">Active</div>
                        </div>
                    </div>
                    <div class="partner-actions">
                        <button class="btn btn-sm btn-primary" onclick="viewPartnerDetails(${partner.id})">View Details</button>
                        <button class="btn btn-sm btn-danger" onclick="deletePartner(${partner.id})">Delete</button>
                    </div>
                </div>
            `).join('');
        }

        // Update partner selects
        updatePartnerSelects();
    } catch (error) {
        console.error('Error loading partners:', error);
    }
}

function updatePartnerSelects() {
    const filterSelect = document.getElementById('filter-partner');
    const linkPartnerSelect = document.getElementById('link-partner-select');

    const options = partners.map(p =>
        `<option value="${p.id}">${p.name} (${p.platform})</option>`
    ).join('');

    filterSelect.innerHTML = '<option value="">All Partners</option>' + options;
    linkPartnerSelect.innerHTML = '<option value="">Select Partner</option>' + options;
}

async function viewPartnerDetails(partnerId) {
    try {
        const response = await fetch(`${API_BASE}/analytics/partner/${partnerId}`);
        const data = await response.json();

        alert(`${data.partner.name} Analytics\n\n` +
              `Total Links: ${data.stats.total_links}\n` +
              `Total Clicks: ${data.stats.total_clicks}\n` +
              `Total Collected: $${data.stats.total_collected}\n` +
              `Total Paid: $${data.stats.total_paid}\n` +
              `Conversion Rate: ${data.stats.conversion_rate}%`);
    } catch (error) {
        console.error('Error loading partner details:', error);
    }
}

async function deletePartner(partnerId) {
    if (!confirm('Are you sure you want to delete this partner? This will also delete all associated links.')) {
        return;
    }

    try {
        await fetch(`${API_BASE}/partners/${partnerId}`, { method: 'DELETE' });
        loadPartners();
    } catch (error) {
        console.error('Error deleting partner:', error);
        alert('Error deleting partner');
    }
}

// Links
async function loadLinks() {
    try {
        const partnerId = document.getElementById('filter-partner').value;
        const status = document.getElementById('filter-status').value;

        let url = `${API_BASE}/links?`;
        if (partnerId) url += `partner_id=${partnerId}&`;
        if (status) url += `status=${status}&`;

        const response = await fetch(url);
        links = await response.json();

        const container = document.getElementById('links-list');
        if (links.length === 0) {
            container.innerHTML = `
                <div class="empty-state">
                    <div class="empty-state-icon">🔗</div>
                    <p class="empty-state-message">No links found</p>
                    <p>Add your first affiliate link to start tracking</p>
                </div>
            `;
        } else {
            container.innerHTML = `
                <table>
                    <thead>
                        <tr>
                            <th>Brand</th>
                            <th>Product</th>
                            <th>Partner</th>
                            <th>Commission</th>
                            <th>Clicks</th>
                            <th>Revenue</th>
                            <th>Status</th>
                            <th>Actions</th>
                        </tr>
                    </thead>
                    <tbody>
                        ${links.map(link => `
                            <tr>
                                <td><strong>${link.brand_name}</strong></td>
                                <td>${link.product_name || '-'}</td>
                                <td>${link.partner_name}</td>
                                <td>${link.commission_rate}%</td>
                                <td>${link.stats.total_clicks}</td>
                                <td>$${link.stats.total_collected}</td>
                                <td><span class="badge ${link.status}">${link.status}</span></td>
                                <td>
                                    <button class="btn btn-sm btn-primary" onclick="copyLink('${link.affiliate_url}')">Copy</button>
                                    <button class="btn btn-sm btn-danger" onclick="deleteLink(${link.id})">Delete</button>
                                </td>
                            </tr>
                        `).join('')}
                    </tbody>
                </table>
            `;
        }

        // Update link selects
        updateLinkSelects();
    } catch (error) {
        console.error('Error loading links:', error);
    }
}

function updateLinkSelects() {
    const transactionLinkSelect = document.getElementById('transaction-link-select');

    const options = links.map(link =>
        `<option value="${link.id}">${link.brand_name} - ${link.product_name || 'General'}</option>`
    ).join('');

    transactionLinkSelect.innerHTML = '<option value="">Select Link</option>' + options;
}

function copyLink(url) {
    navigator.clipboard.writeText(url);
    alert('Link copied to clipboard!');
}

async function deleteLink(linkId) {
    if (!confirm('Are you sure you want to delete this link?')) {
        return;
    }

    try {
        await fetch(`${API_BASE}/links/${linkId}`, { method: 'DELETE' });
        loadLinks();
    } catch (error) {
        console.error('Error deleting link:', error);
        alert('Error deleting link');
    }
}

// Setup filter listeners
document.getElementById('filter-partner')?.addEventListener('change', loadLinks);
document.getElementById('filter-status')?.addEventListener('change', loadLinks);

// Transactions
async function loadTransactions() {
    try {
        const response = await fetch(`${API_BASE}/transactions`);
        transactions = await response.json();

        const container = document.getElementById('transactions-list');
        if (transactions.length === 0) {
            container.innerHTML = `
                <div class="empty-state">
                    <div class="empty-state-icon">💰</div>
                    <p class="empty-state-message">No transactions yet</p>
                    <p>Add transactions as they occur from your affiliate platforms</p>
                </div>
            `;
        } else {
            container.innerHTML = `
                <table>
                    <thead>
                        <tr>
                            <th>Date</th>
                            <th>Brand</th>
                            <th>Order ID</th>
                            <th>Collected</th>
                            <th>Paid</th>
                            <th>Status</th>
                            <th>Actions</th>
                        </tr>
                    </thead>
                    <tbody>
                        ${transactions.map(t => `
                            <tr>
                                <td>${new Date(t.transaction_date).toLocaleDateString()}</td>
                                <td>${t.brand_name || 'Unknown'}</td>
                                <td>${t.order_id || '-'}</td>
                                <td>$${t.amount_collected}</td>
                                <td>$${t.amount_paid}</td>
                                <td><span class="badge ${t.status}">${t.status}</span></td>
                                <td>
                                    ${t.status === 'pending' ?
                                        `<button class="btn btn-sm btn-primary" onclick="markAsPaid(${t.id}, ${t.amount_collected})">Mark Paid</button>` :
                                        '-'}
                                </td>
                            </tr>
                        `).join('')}
                    </tbody>
                </table>
            `;
        }
    } catch (error) {
        console.error('Error loading transactions:', error);
    }
}

async function markAsPaid(transactionId, amount) {
    try {
        await fetch(`${API_BASE}/transactions/${transactionId}`, {
            method: 'PUT',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ status: 'paid', amount_paid: amount })
        });
        loadTransactions();
        loadDashboard();
    } catch (error) {
        console.error('Error updating transaction:', error);
        alert('Error updating transaction');
    }
}

// Modal Functions
function showAddPartnerModal() {
    document.getElementById('add-partner-modal').classList.add('active');
}

function showAddLinkModal() {
    if (partners.length === 0) {
        alert('Please add a partner first!');
        return;
    }
    document.getElementById('add-link-modal').classList.add('active');
}

function showAddTransactionModal() {
    if (links.length === 0) {
        alert('Please add a link first!');
        return;
    }
    document.getElementById('add-transaction-modal').classList.add('active');
}

function closeModal(modalId) {
    document.getElementById(modalId).classList.remove('active');
}

// Form Submissions
async function submitPartner(event) {
    event.preventDefault();
    const form = event.target;
    const formData = new FormData(form);
    const data = Object.fromEntries(formData.entries());

    try {
        await fetch(`${API_BASE}/partners`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(data)
        });

        closeModal('add-partner-modal');
        form.reset();
        loadPartners();
    } catch (error) {
        console.error('Error creating partner:', error);
        alert('Error creating partner');
    }
}

async function submitLink(event) {
    event.preventDefault();
    const form = event.target;
    const formData = new FormData(form);
    const data = Object.fromEntries(formData.entries());

    // Convert partner_id to integer
    data.partner_id = parseInt(data.partner_id);
    data.commission_rate = parseFloat(data.commission_rate) || 0;

    try {
        await fetch(`${API_BASE}/links`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(data)
        });

        closeModal('add-link-modal');
        form.reset();
        loadLinks();
    } catch (error) {
        console.error('Error creating link:', error);
        alert('Error creating link');
    }
}

async function submitTransaction(event) {
    event.preventDefault();
    const form = event.target;
    const formData = new FormData(form);
    const data = Object.fromEntries(formData.entries());

    // Convert to proper types
    data.link_id = parseInt(data.link_id);
    data.amount_collected = parseFloat(data.amount_collected);
    data.amount_paid = parseFloat(data.amount_paid) || 0;

    try {
        await fetch(`${API_BASE}/transactions`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(data)
        });

        closeModal('add-transaction-modal');
        form.reset();
        loadTransactions();
        loadDashboard();
    } catch (error) {
        console.error('Error creating transaction:', error);
        alert('Error creating transaction');
    }
}

// Close modal on outside click
window.addEventListener('click', (e) => {
    if (e.target.classList.contains('modal')) {
        e.target.classList.remove('active');
    }
});
