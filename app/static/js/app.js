/**
 * OTL Reports - Shared utilities
 */

// Standard currency format: 1,234,567.89
function formatNum(value) {
    if (value == null || value === '') return '-';
    return Number(value).toLocaleString('en-US', {
        minimumFractionDigits: 2,
        maximumFractionDigits: 2,
    });
}

// Compact format for chart axes & KPI cards: 37,342M, 45.6K, 123.45
// Drops decimals when fractional part is 0 (e.g. 1,000M not 1,000.00M)
function formatCompact(value) {
    if (value == null) return '-';
    const num = Number(value);
    if (Math.abs(num) >= 1e6) return smartNum(num / 1e6, 2) + 'M';
    if (Math.abs(num) >= 1e3) return smartNum(num / 1e3, 1) + 'K';
    return smartNum(num, 2);
}

// Format number with up to maxDec decimals, but drop trailing .00
function smartNum(n, maxDec) {
    const fixed = Number(n.toFixed(maxDec));
    if (fixed === Math.floor(fixed)) {
        return Math.floor(fixed).toLocaleString('en-US');
    }
    return fixed.toLocaleString('en-US', { minimumFractionDigits: 1, maximumFractionDigits: maxDec });
}

// Integer format for counts: 1,234
function formatInt(value) {
    if (value == null || value === '') return '-';
    return Number(value).toLocaleString('en-US', { maximumFractionDigits: 0 });
}

// Shared Chart.js tooltip callback — shows currency symbol before the value
// Uses ctx.raw which is always the actual data value regardless of chart orientation
const currencyTooltip = {
    callbacks: {
        label: function(ctx) {
            const label = ctx.dataset.label || ctx.label || '';
            const ccy = typeof ccyLabel === 'function' ? ccyLabel() : (typeof localCurrency !== 'undefined' ? localCurrency : '');
            const val = ccy + ' ' + formatNum(ctx.raw);
            return label ? `${label}: ${val}` : val;
        }
    }
};

const CHART_COLORS = [
    '#3b82f6', '#10b981', '#f59e0b', '#ef4444', '#8b5cf6',
    '#06b6d4', '#ec4899', '#f97316', '#14b8a6', '#6366f1',
    '#84cc16', '#e11d48', '#0ea5e9', '#a855f7', '#22c55e',
];

function getColors(count) {
    const colors = [];
    for (let i = 0; i < count; i++) {
        colors.push(CHART_COLORS[i % CHART_COLORS.length]);
    }
    return colors;
}
