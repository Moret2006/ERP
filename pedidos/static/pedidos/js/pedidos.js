document.addEventListener('DOMContentLoaded', () => {
    initStatusChart();
    initActionMenus();
});

function initStatusChart() {
    const canvas = document.getElementById('status-chart');
    const dataEl = document.getElementById('status-chart-data');

    if (!canvas || !dataEl || typeof Chart === 'undefined') return;

    const chartData = JSON.parse(dataEl.textContent || '{}');
    const values = chartData.values || [0, 0, 0, 0];
    const hasData = values.some((value) => Number(value) > 0);

    const ctx = canvas.getContext('2d');
    new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels: chartData.labels || [],
            datasets: [{
                data: hasData ? values : [1],
                backgroundColor: hasData
                    ? (chartData.colors || ['#2e9e6a', '#0099d6', '#ff2f78', '#e67e22'])
                    : ['#ece8ec'],
                borderWidth: 0,
                hoverOffset: hasData ? 4 : 0,
            }],
        },
        options: {
            responsive: false,
            maintainAspectRatio: false,
            cutout: '72%',
            plugins: {
                legend: { display: false },
                tooltip: { enabled: hasData },
            },
        },
    });
}

function initActionMenus() {
    const menus = document.querySelectorAll('[data-action-menu]');
    if (!menus.length) return;

    menus.forEach((menu) => {
        const toggle = menu.querySelector('[data-action-toggle]');
        const dropdown = menu.querySelector('[data-action-dropdown]');
        if (!toggle || !dropdown) return;

        toggle.addEventListener('click', (event) => {
            event.stopPropagation();
            const isOpen = toggle.getAttribute('aria-expanded') === 'true';
            closeAllActionMenus();
            if (!isOpen) {
                toggle.setAttribute('aria-expanded', 'true');
                dropdown.hidden = false;
            }
        });
    });

    document.addEventListener('click', closeAllActionMenus);
}

function closeAllActionMenus() {
    document.querySelectorAll('[data-action-menu]').forEach((menu) => {
        const toggle = menu.querySelector('[data-action-toggle]');
        const dropdown = menu.querySelector('[data-action-dropdown]');
        if (toggle) toggle.setAttribute('aria-expanded', 'false');
        if (dropdown) dropdown.hidden = true;
    });
}
