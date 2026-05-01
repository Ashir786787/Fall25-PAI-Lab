let distributionChart, storeTypeChart, sizeAnalysisChart;

document.addEventListener('DOMContentLoaded', function() {
    loadAnalyticsData();
});

function loadAnalyticsData() {
    fetch('/api/analytics')
        .then(response => response.json())
        .then(data => {
            if (data.status === 'success') {
                displaySalesDistribution(data.sales_distribution);
                displayStatistics(data.sales_distribution);
                displayStoreTypeAnalysis(data.store_types);
            }
        });
}

function displaySalesDistribution(stats) {
    const ctx = document.getElementById('distributionChart');
    if (!ctx) return;
    
    if (distributionChart) {
        distributionChart.destroy();
    }
    
    distributionChart = new Chart(ctx.getContext('2d'), {
        type: 'bar',
        data: {
            labels: ['Min', 'Median', 'Mean', 'Max'],
            datasets: [{
                label: 'Sales ($)',
                data: [stats.min, stats.median, stats.mean, stats.max],
                backgroundColor: ['#667eea', '#f093fb', '#f5576c', '#ff9d00']
            }]
        },
        options: {
            responsive: true,
            scales: {
                y: {
                    beginAtZero: true,
                    ticks: { callback: v => '$' + v.toLocaleString() }
                }
            }
        }
    });
}

function displayStatistics(stats) {
    const tbody = document.getElementById('statsTable');
    if (!tbody) return;
    
    tbody.innerHTML = `
        <tr><td><strong>Count</strong></td><td>${stats.count.toLocaleString()}</td></tr>
        <tr><td><strong>Mean</strong></td><td>$${stats.mean.toLocaleString()}</td></tr>
        <tr><td><strong>Median</strong></td><td>$${stats.median.toLocaleString()}</td></tr>
        <tr><td><strong>Std Dev</strong></td><td>$${stats.std.toLocaleString()}</td></tr>
        <tr><td><strong>Min</strong></td><td>$${stats.min.toLocaleString()}</td></tr>
        <tr><td><strong>Max</strong></td><td>$${stats.max.toLocaleString()}</td></tr>
    `;
}

function displayStoreTypeAnalysis(storeTypes) {
    const ctx = document.getElementById('storeTypeChart');
    if (!ctx) return;
    
    if (storeTypeChart) {
        storeTypeChart.destroy();
    }
    
    const types = Object.keys(storeTypes);
    const means = types.map(t => storeTypes[t]);

    storeTypeChart = new Chart(ctx.getContext('2d'), {
        type: 'bar',
        data: {
            labels: types,
            datasets: [{
                label: 'Average Sales ($)',
                data: means,
                backgroundColor: ['#667eea', '#764ba2', '#f5576c']
            }]
        },
        options: {
            responsive: true,
            scales: {
                y: {
                    beginAtZero: true,
                    ticks: { callback: v => '$' + v.toLocaleString() }
                }
            }
        }
    });
}
