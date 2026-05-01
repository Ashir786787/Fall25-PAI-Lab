let topStoresChartInstance, seasonalChartInstance;

document.addEventListener('DOMContentLoaded', function() {
    loadInsightsData();
});

function loadInsightsData() {
    fetch('/api/insights')
        .then(response => response.json())
        .then(data => {
            if (data.status === 'success') {
                displaySummary(data.summary);
                displayTopStoresChart(data.top_stores);
                displaySeasonalPattern(data.seasonal_pattern);
            }
        });
}

function displaySummary(summary) {
    const totalSalesElem = document.getElementById('totalSales');
    const holidayImpactElem = document.getElementById('holidayImpact');
    
    if (totalSalesElem) {
        totalSalesElem.textContent = '$' + (summary.total_sales / 1000000).toFixed(1) + 'M';
    }
    
    if (holidayImpactElem) {
        holidayImpactElem.textContent = `+${summary.holiday_impact_percent.toFixed(1)}%`;
    }

    const card = document.querySelector('#holidayImpact')?.closest('.card');
    const details = card?.querySelector('p');
    if (details) {
        details.innerHTML = `
            <strong>Regular:</strong> $${summary.regular_week_avg.toLocaleString()}<br/>
            <strong>Holiday:</strong> $${summary.holiday_week_avg.toLocaleString()}
        `;
    }
}

function displayTopStoresChart(topStores) {
    const ctx = document.getElementById('topStoresChart');
    if (!ctx) return;
    
    if (topStoresChartInstance) {
        topStoresChartInstance.destroy();
    }
    
    const stores = Object.keys(topStores);
    const values = Object.values(topStores);

    topStoresChartInstance = new Chart(ctx.getContext('2d'), {
        type: 'bar',
        data: {
            labels: stores.map(s => `Store ${s}`),
            datasets: [{
                label: 'Avg Sales ($)',
                data: values,
                backgroundColor: ['#667eea', '#764ba2', '#f093fb', '#f5576c', '#fa7921']
            }]
        },
        options: {
            indexAxis: 'y',
            responsive: true,
            scales: {
                x: { ticks: { callback: v => '$' + v.toLocaleString() } }
            }
        }
    });
}

function displaySeasonalPattern(seasonal) {
    const ctx = document.getElementById('seasonalChart');
    if (!ctx) return;
    
    if (seasonalChartInstance) {
        seasonalChartInstance.destroy();
    }
    
    const months = Object.keys(seasonal);
    const values = Object.values(seasonal);

    seasonalChartInstance = new Chart(ctx.getContext('2d'), {
        type: 'line',
        data: {
            labels: months,
            datasets: [{
                label: 'Monthly Avg ($)',
                data: values,
                borderColor: '#667eea',
                fill: false,
                tension: 0.4
            }]
        },
        options: {
            responsive: true,
            scales: {
                y: { ticks: { callback: v => '$' + v.toLocaleString() } }
            }
        }
    });
}
