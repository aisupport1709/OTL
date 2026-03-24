/**
 * OTL Reports - Dashboard with filters
 */

const charts = {};
let localCurrency = 'VND';
let availableCurrencies = [];

function getFilters() {
    const month = document.getElementById('filter-month').value;
    const category = document.getElementById('filter-category').value;
    const params = new URLSearchParams();
    if (month) params.set('month', month);
    if (category) params.set('category', category);
    params.set('currency', getSelectedCurrency());
    return params;
}

function updateFilterBadges() {
    const month = document.getElementById('filter-month').value;
    const category = document.getElementById('filter-category').value;
    const container = document.getElementById('active-filters');
    const badges = document.getElementById('filter-badges');

    if (!month && !category) {
        container.classList.add('hidden');
        return;
    }
    container.classList.remove('hidden');
    let html = '';
    if (month) html += `<span class="px-2 py-0.5 bg-blue-100 text-blue-700 rounded-full text-xs font-medium">Month: ${month}</span>`;
    if (category) html += `<span class="px-2 py-0.5 bg-purple-100 text-purple-700 rounded-full text-xs font-medium">${category}</span>`;
    badges.innerHTML = html;
}

function resetFilters() {
    document.getElementById('filter-month').value = '';
    document.getElementById('filter-category').value = '';
    // Reset currency to local
    const ccySel = document.getElementById('filter-currency');
    if (ccySel) ccySel.value = localCurrency;
    loadDashboard();
}

async function loadFilterOptions() {
    try {
        const resp = await fetch('/api/filters/months');
        const months = await resp.json();
        const sel = document.getElementById('filter-month');
        const current = sel.value;
        sel.innerHTML = '<option value="">All Months</option>' +
            months.map(m => `<option value="${m}" ${m === current ? 'selected' : ''}>${m}</option>`).join('');
    } catch (err) {
        console.error('Failed to load months', err);
    }
}

async function loadCurrencyOptions() {
    try {
        const resp = await fetch('/api/kpi/currency-breakdown?' + getFilters());
        const data = await resp.json();
        availableCurrencies = data.map(d => d.currency).filter(Boolean);

        const sel = document.getElementById('filter-currency');
        const current = sel.value || localCurrency;

        // Build options: local currency first (default), then others
        let options = [`<option value="${localCurrency}">${localCurrency} (Local)</option>`];
        for (const ccy of availableCurrencies) {
            if (ccy !== localCurrency) {
                options.push(`<option value="${ccy}" ${ccy === current ? 'selected' : ''}>${ccy}</option>`);
            }
        }
        sel.innerHTML = options.join('');

        // Restore selection
        if (current && availableCurrencies.includes(current)) {
            sel.value = current;
        } else {
            sel.value = localCurrency;
        }
    } catch (err) {
        console.error('Failed to load currencies', err);
    }
}

function getSelectedCurrency() {
    const sel = document.getElementById('filter-currency');
    return sel ? sel.value : localCurrency;
}

function isLocalCurrency() {
    return getSelectedCurrency() === localCurrency;
}

function ccyLabel() {
    return getSelectedCurrency();
}

async function onCurrencyChange() {
    // Re-render with new currency — reload only data, not filter options
    updateFilterBadges();
    await Promise.all([
        loadKPIs(),
        loadFtlLtlComparison(),
        loadRevenueByMonth(),
        loadTopCustomers(),
        loadRevenueByCategory(),
        loadRoutes(),
        loadInvoiceStatus(),
    ]);
}

async function loadDashboard() {
    updateFilterBadges();
    // Load settings first so currency label is available
    try {
        const resp = await fetch('/api/settings');
        const settings = await resp.json();
        localCurrency = settings.local_currency || 'VND';
    } catch (err) {
        console.error('Failed to load settings', err);
    }
    await loadFilterOptions();
    await loadCurrencyOptions();
    await Promise.all([
        loadKPIs(),
        loadFtlLtlComparison(),
        loadRevenueByMonth(),
        loadTopCustomers(),
        loadRevenueByCategory(),
        loadRoutes(),
        loadInvoiceStatus(),
    ]);
}

// ─── KPIs ────────────────────────────────────────────────────────────

async function loadKPIs() {
    try {
        const resp = await fetch(`/api/kpi/summary?${getFilters()}`);
        const data = await resp.json();
        const ccy = getSelectedCurrency();

        document.getElementById('kpi-invoices').textContent = formatInt(data.total_invoices);
        document.getElementById('kpi-revenue').textContent = ccy + ' ' + formatCompact(data.total_revenue);
        document.getElementById('kpi-tax').textContent = ccy + ' ' + formatCompact(data.total_tax);
        document.getElementById('kpi-customers').textContent = formatInt(data.total_customers);
        document.getElementById('kpi-bookings').textContent = formatInt(data.total_bookings);
        document.getElementById('kpi-records').textContent = formatInt(data.total_records);

        document.getElementById('revenue-summary-body').innerHTML = `
            <div class="flex justify-between py-2.5 border-b border-gray-100 text-sm">
                <span class="text-gray-500">Revenue (excl. tax)</span>
                <span class="font-semibold">${ccy} ${formatNum(data.total_revenue)}</span></div>
            <div class="flex justify-between py-2.5 border-b border-gray-100 text-sm">
                <span class="text-gray-500">Tax</span>
                <span class="font-semibold">${ccy} ${formatNum(data.total_tax)}</span></div>
            <div class="flex justify-between py-2.5 border-b border-gray-100 text-sm">
                <span class="text-gray-500">Revenue (incl. tax)</span>
                <span class="font-semibold text-blue-600">${ccy} ${formatNum(data.total_revenue_with_tax)}</span></div>
            <div class="flex justify-between py-2.5 border-b border-gray-100 text-sm">
                <span class="text-gray-500">Avg Revenue / Invoice</span>
                <span class="font-semibold">${data.total_invoices > 0
                    ? ccy + ' ' + formatNum(data.total_revenue / data.total_invoices) : '-'}</span></div>
            <div class="flex justify-between py-2.5 text-sm">
                <span class="text-gray-500">Avg Revenue / Customer</span>
                <span class="font-semibold">${data.total_customers > 0
                    ? ccy + ' ' + formatNum(data.total_revenue / data.total_customers) : '-'}</span></div>
        `;
    } catch (err) {
        console.error('Failed to load KPIs', err);
    }
}

// ─── FTL vs LTL ─────────────────────────────────────────────────────

async function loadFtlLtlComparison() {
    try {
        const params = new URLSearchParams();
        const month = document.getElementById('filter-month').value;
        if (month) params.set('month', month);
        params.set('currency', getSelectedCurrency());

        const resp = await fetch(`/api/kpi/ftl-ltl-comparison?${params}`);
        const data = await resp.json();

        const ftlData = data.filter(d => d.category === 'FTL');
        const ltlData = data.filter(d => d.category === 'LTL');
        const allMonths = [...new Set(data.map(d => d.month))].sort();

        const ftlMap = Object.fromEntries(ftlData.map(d => [d.month, d.revenue]));
        const ltlMap = Object.fromEntries(ltlData.map(d => [d.month, d.revenue]));

        if (charts.ftlLtl) charts.ftlLtl.destroy();
        charts.ftlLtl = new Chart(document.getElementById('chart-ftl-ltl'), {
            type: 'bar',
            data: {
                labels: allMonths,
                datasets: [
                    {
                        label: 'FTL',
                        data: allMonths.map(m => ftlMap[m] || 0),
                        backgroundColor: '#3b82f6',
                        borderRadius: 4,
                    },
                    {
                        label: 'LTL',
                        data: allMonths.map(m => ltlMap[m] || 0),
                        backgroundColor: '#f59e0b',
                        borderRadius: 4,
                    },
                ],
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: { legend: { position: 'top' }, tooltip: currencyTooltip },
                scales: {
                    y: {
                        beginAtZero: true,
                        ticks: { callback: v => ccyLabel() + ' ' + formatCompact(v) },
                    },
                },
            },
        });
    } catch (err) {
        console.error('Failed to load FTL/LTL comparison', err);
    }
}

// ─── Revenue by Month ────────────────────────────────────────────────

async function loadRevenueByMonth() {
    try {
        const params = new URLSearchParams();
        const category = document.getElementById('filter-category').value;
        if (category) params.set('category', category);
        params.set('currency', getSelectedCurrency());

        const resp = await fetch(`/api/kpi/revenue-by-month?${params}`);
        const data = await resp.json();

        if (charts.revenueMonth) charts.revenueMonth.destroy();
        charts.revenueMonth = new Chart(document.getElementById('chart-revenue-month'), {
            type: 'bar',
            data: {
                labels: data.map(d => d.month),
                datasets: [
                    {
                        label: 'Revenue',
                        data: data.map(d => d.revenue),
                        backgroundColor: '#3b82f6',
                        borderRadius: 4,
                    },
                    {
                        label: 'Tax',
                        data: data.map(d => d.tax),
                        backgroundColor: '#f59e0b',
                        borderRadius: 4,
                    },
                ],
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: { legend: { position: 'top' }, tooltip: currencyTooltip },
                scales: {
                    y: {
                        beginAtZero: true,
                        ticks: { callback: v => ccyLabel() + ' ' + formatCompact(v) },
                    },
                },
            },
        });
    } catch (err) {
        console.error('Failed to load revenue by month', err);
    }
}

// ─── Top Customers ───────────────────────────────────────────────────

async function loadTopCustomers() {
    try {
        const resp = await fetch(`/api/kpi/top-customers?${getFilters()}`);
        const data = await resp.json();

        if (charts.topCustomers) charts.topCustomers.destroy();
        charts.topCustomers = new Chart(document.getElementById('chart-top-customers'), {
            type: 'bar',
            data: {
                labels: data.map(d => d.customer_name ? d.customer_name.substring(0, 25) : ''),
                datasets: [{
                    label: 'Revenue',
                    data: data.map(d => d.revenue),
                    backgroundColor: getColors(data.length),
                    borderRadius: 4,
                }],
            },
            options: {
                indexAxis: 'y',
                responsive: true,
                maintainAspectRatio: false,
                plugins: { legend: { display: false }, tooltip: currencyTooltip },
                scales: {
                    x: {
                        beginAtZero: true,
                        ticks: { callback: v => ccyLabel() + ' ' + formatCompact(v) },
                    },
                },
            },
        });
    } catch (err) {
        console.error('Failed to load top customers', err);
    }
}

// ─── Revenue by Category ────────────────────────────────────────────

async function loadRevenueByCategory() {
    try {
        const params = new URLSearchParams();
        const month = document.getElementById('filter-month').value;
        if (month) params.set('month', month);
        params.set('currency', getSelectedCurrency());

        const resp = await fetch(`/api/kpi/revenue-by-category?${params}`);
        const data = await resp.json();

        if (charts.category) charts.category.destroy();
        charts.category = new Chart(document.getElementById('chart-category'), {
            type: 'doughnut',
            data: {
                labels: data.map(d => d.category),
                datasets: [{
                    data: data.map(d => d.revenue),
                    backgroundColor: getColors(data.length),
                }],
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: { position: 'bottom', labels: { boxWidth: 12, font: { size: 11 } } },
                    tooltip: currencyTooltip,
                },
            },
        });
    } catch (err) {
        console.error('Failed to load category data', err);
    }
}

// ─── Top 10 Routes ──────────────────────────────────────────────────

async function loadRoutes() {
    try {
        const resp = await fetch(`/api/kpi/revenue-by-location?${getFilters()}`);
        const data = await resp.json();

        if (charts.routes) charts.routes.destroy();
        charts.routes = new Chart(document.getElementById('chart-routes'), {
            type: 'bar',
            data: {
                labels: data.map(d => d.route),
                datasets: [{
                    label: 'Revenue',
                    data: data.map(d => d.revenue),
                    backgroundColor: getColors(data.length),
                    borderRadius: 4,
                }],
            },
            options: {
                indexAxis: 'y',
                responsive: true,
                maintainAspectRatio: false,
                plugins: { legend: { display: false }, tooltip: currencyTooltip },
                scales: {
                    x: {
                        beginAtZero: true,
                        ticks: { callback: v => ccyLabel() + ' ' + formatCompact(v) },
                    },
                },
            },
        });
    } catch (err) {
        console.error('Failed to load routes', err);
    }
}

// ─── Invoice Status ──────────────────────────────────────────────────

async function loadInvoiceStatus() {
    try {
        const resp = await fetch(`/api/kpi/invoice-status?${getFilters()}`);
        const data = await resp.json();

        if (charts.status) charts.status.destroy();
        charts.status = new Chart(document.getElementById('chart-status'), {
            type: 'pie',
            data: {
                labels: data.map(d => `${d.status} (${formatInt(d.count)})`),
                datasets: [{
                    data: data.map(d => d.count),
                    backgroundColor: getColors(data.length),
                }],
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: { position: 'bottom', labels: { boxWidth: 12, font: { size: 11 } } },
                    tooltip: {
                        callbacks: {
                            label: function(ctx) {
                                return `${ctx.label}: ${formatInt(ctx.parsed)}`;
                            }
                        }
                    },
                },
            },
        });
    } catch (err) {
        console.error('Failed to load invoice status', err);
    }
}

// ─── Export PDF ──────────────────────────────────────────────────────

async function exportToPDF() {
    const btn = document.getElementById('btn-export-pdf');
    const originalHTML = btn.innerHTML;
    btn.disabled = true;
    btn.innerHTML = '<i class="bi bi-hourglass-split"></i> Generating...';

    try {
        const { jsPDF } = window.jspdf;
        const content = document.querySelector('main');

        const canvas = await html2canvas(content, {
            scale: 2,
            useCORS: true,
            backgroundColor: '#f3f4f6',
            logging: false,
        });

        const imgData = canvas.toDataURL('image/png');
        const pdf = new jsPDF({ orientation: 'portrait', unit: 'mm', format: 'a4' });

        const pageW = pdf.internal.pageSize.getWidth();
        const pageH = pdf.internal.pageSize.getHeight();
        const margin = 10;
        const usableW = pageW - margin * 2;
        const imgW = canvas.width;
        const imgH = canvas.height;
        const ratio = usableW / (imgW / (96 / 25.4)); // px to mm
        const scaledH = (imgH / (96 / 25.4)) * (usableW / (imgW / (96 / 25.4)));

        // Split across pages if content is taller than one page
        const usableH = pageH - margin * 2;
        const totalPages = Math.ceil(scaledH / usableH);
        const sliceH = Math.floor(imgH / totalPages);

        for (let i = 0; i < totalPages; i++) {
            if (i > 0) pdf.addPage();
            const sliceCanvas = document.createElement('canvas');
            sliceCanvas.width = imgW;
            const remainH = imgH - i * sliceH;
            sliceCanvas.height = i === totalPages - 1 ? remainH : sliceH;
            const ctx = sliceCanvas.getContext('2d');
            ctx.drawImage(canvas, 0, -i * sliceH);
            const sliceData = sliceCanvas.toDataURL('image/png');
            const sliceScaledH = (sliceCanvas.height / (96 / 25.4)) * (usableW / (imgW / (96 / 25.4)));
            pdf.addImage(sliceData, 'PNG', margin, margin, usableW, sliceScaledH);
        }

        const filters = [];
        const month = document.getElementById('filter-month').value;
        const category = document.getElementById('filter-category').value;
        if (month) filters.push(month);
        if (category) filters.push(category);
        const suffix = filters.length ? '_' + filters.join('_') : '';
        pdf.save(`dashboard${suffix}.pdf`);
    } catch (err) {
        console.error('PDF export failed', err);
        alert('Failed to export PDF. Please try again.');
    } finally {
        btn.disabled = false;
        btn.innerHTML = originalHTML;
    }
}

// ─── Init ────────────────────────────────────────────────────────────
loadDashboard();
