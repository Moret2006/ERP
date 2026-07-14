document.addEventListener('DOMContentLoaded', () => {
    initSidebar();
    initUserMenu();
    initSearch();
    initSalesChart();
});

function initSidebar() {
    const sidebar = document.getElementById('sidebar');
    const overlay = document.getElementById('sidebar-overlay');
    const openBtn = document.getElementById('sidebar-open');
    const closeBtn = document.getElementById('sidebar-close');

    if (!sidebar || !overlay) return;

    const open = () => {
        sidebar.classList.add('is-open');
        overlay.hidden = false;
        document.body.style.overflow = 'hidden';
    };

    const close = () => {
        sidebar.classList.remove('is-open');
        overlay.hidden = true;
        document.body.style.overflow = '';
    };

    openBtn?.addEventListener('click', open);
    closeBtn?.addEventListener('click', close);
    overlay.addEventListener('click', close);

    window.addEventListener('resize', () => {
        if (window.innerWidth > 900) close();
    });
}

function initUserMenu() {
    const toggle = document.getElementById('user-menu-toggle');
    const dropdown = document.getElementById('user-menu-dropdown');

    if (!toggle || !dropdown) return;

    toggle.addEventListener('click', (event) => {
        event.stopPropagation();
        const isOpen = toggle.getAttribute('aria-expanded') === 'true';
        toggle.setAttribute('aria-expanded', String(!isOpen));
        dropdown.hidden = isOpen;
    });

    document.addEventListener('click', () => {
        toggle.setAttribute('aria-expanded', 'false');
        dropdown.hidden = true;
    });
}

function initSearch() {
    const input = document.getElementById('global-search');
    if (!input) return;

    input.addEventListener('keydown', (event) => {
        if (event.key === 'Enter') {
            event.preventDefault();
            // Integração futura com endpoint de busca global
        }
    });
}

function initSalesChart() {
    const canvas = document.getElementById('sales-chart');
    const labelsEl = document.getElementById('sales-chart-labels');
    const valuesEl = document.getElementById('sales-chart-values');

    if (!canvas || !labelsEl || !valuesEl || typeof Chart === 'undefined') return;

    const labels = JSON.parse(labelsEl.textContent || '[]');
    const values = JSON.parse(valuesEl.textContent || '[]');

    if (!labels.length || !values.length) return;

    const ctx = canvas.getContext('2d');
    const gradient = ctx.createLinearGradient(0, 0, 0, 220);
    gradient.addColorStop(0, 'rgba(255, 47, 120, 0.28)');
    gradient.addColorStop(1, 'rgba(255, 47, 120, 0.02)');

    new Chart(ctx, {
        type: 'line',
        data: {
            labels,
            datasets: [{
                data: values,
                borderColor: '#ff2f78',
                backgroundColor: gradient,
                borderWidth: 2.5,
                pointBackgroundColor: '#ffffff',
                pointBorderColor: '#ff2f78',
                pointBorderWidth: 2,
                pointRadius: 4,
                pointHoverRadius: 6,
                fill: true,
                tension: 0.35,
            }],
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: { display: false },
                tooltip: {
                    backgroundColor: '#2d2d3a',
                    padding: 10,
                    cornerRadius: 8,
                },
            },
            scales: {
                x: {
                    grid: { display: false },
                    ticks: { color: '#8b8b9e', font: { family: 'Poppins', size: 11 } },
                },
                y: {
                    beginAtZero: true,
                    grid: { color: 'rgba(139, 139, 158, 0.12)' },
                    ticks: { color: '#8b8b9e', font: { family: 'Poppins', size: 11 } },
                },
            },
        },
    });
}
