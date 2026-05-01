let holidayChart, monthlyChart;

document.addEventListener('DOMContentLoaded', function() {
    loadDashboardData();
});

function loadDashboardData() {
    fetch('/api/overview')
        .then(response => {
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            return response.json();
        })
        .then(data => {
            if (data.status === 'success') {
                displayHolidayImpact(data.holiday_impact);
                displayMonthlyTrend(data.monthly_trend);
                displayTopStores(data.stores.top);
                displayTopDepartments(data.departments.top);
            } else {
                showErrorMessage('Failed to load dashboard data');
            }
        })
        .catch(error => {
            showErrorMessage('Error loading data: ' + error.message);
        });
}

function displayHolidayImpact(holiday_impact) {
    const ctx = document.getElementById('holidayChart');
    if (!ctx) return;
    
    if (holidayChart) {
        holidayChart.destroy();
    }
    
    const gradientRegular = ctx.getContext('2d').createLinearGradient(0, 0, 0, 400);
    gradientRegular.addColorStop(0, '#4f46e5');
    gradientRegular.addColorStop(1, '#818cf8');
    
    const gradientHoliday = ctx.getContext('2d').createLinearGradient(0, 0, 0, 400);
    gradientHoliday.addColorStop(0, '#ec4899');
    gradientHoliday.addColorStop(1, '#f472b6');

    holidayChart = new Chart(ctx.getContext('2d'), {
        type: 'bar',
        data: {
            labels: ['Regular Weeks', 'Holiday Weeks'],
            datasets: [{
                label: 'Average Sales ($)',
                data: [holiday_impact.regular, holiday_impact.holiday],
                backgroundColor: [gradientRegular, gradientHoliday],
                borderRadius: 8,
                borderSkipped: false,
                barPercentage: 0.6
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: true,
            plugins: {
                legend: { display: false }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    ticks: { callback: v => '$' + v.toLocaleString() }
                }
            }
        }
    });

    const wrapper = ctx.parentElement;
    const liftDiv = document.createElement('div');
    liftDiv.className = 'alert alert-success mt-3';
    liftDiv.innerHTML = `
        <strong>Holiday Lift: +${holiday_impact.lift.toFixed(2)}%</strong><br/>
        Regular: $${holiday_impact.regular.toLocaleString()}<br/>
        Holiday: $${holiday_impact.holiday.toLocaleString()}
    `;
    wrapper.appendChild(liftDiv);
}

function displayMonthlyTrend(monthly_trend) {
    const ctx = document.getElementById('monthlyChart');
    if (!ctx) return;
    
    const months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'];
    const values = months.map((m, i) => monthly_trend[i + 1] || 0);

    if (monthlyChart) {
        monthlyChart.destroy();
    }
    
    monthlyChart = new Chart(ctx.getContext('2d'), {
        type: 'line',
        data: {
            labels: months,
            datasets: [{
                label: 'Average Sales ($)',
                data: values,
                borderColor: '#4f46e5',
                borderWidth: 4,
                fill: true,
                tension: 0.4
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: true,
            plugins: {
                legend: { display: false }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    ticks: { callback: v => '$' + v.toLocaleString() }
                }
            }
        }
    });
}

function displayTopStores(stores) {
    const container = document.getElementById('topStoresContainer');
    if (!container) return;
    container.innerHTML = '';

    const storesList = Object.entries(stores).slice(0, 10);
    storesList.forEach(([store, data], index) => {
        const row = document.createElement('div');
        row.className = 'mb-3 pb-3 border-bottom';
        row.innerHTML = `
            <div class="d-flex justify-content-between align-items-center">
                <div>
                    <h6 class="mb-1">Store ${store}</h6>
                    <small>Avg: $${parseFloat(data[0]).toLocaleString()}</small>
                </div>
                <span class="badge bg-primary">#${index + 1}</span>
            </div>
        `;
        container.appendChild(row);
    });
}

function displayTopDepartments(departments) {
    const container = document.getElementById('topDeptsContainer');
    if (!container) return;
    container.innerHTML = '';

    const deptsList = Object.entries(departments).slice(0, 10);
    deptsList.forEach(([dept, data], index) => {
        const row = document.createElement('div');
        row.className = 'mb-3 pb-3 border-bottom';
        row.innerHTML = `
            <div class="d-flex justify-content-between align-items-center">
                <div>
                    <h6 class="mb-1">Dept ${dept}</h6>
                    <small>Avg: $${parseFloat(data[0]).toLocaleString()}</small>
                </div>
                <span class="badge bg-success">#${index + 1}</span>
            </div>
        `;
        container.appendChild(row);
    });
}

function showErrorMessage(message) {
    const container = document.querySelector('.container-fluid');
    if (container) {
        const alert = document.createElement('div');
        alert.className = 'alert alert-danger';
        alert.innerHTML = message;
        container.prepend(alert);
    }
}
