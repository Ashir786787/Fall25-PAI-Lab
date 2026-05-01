document.addEventListener('DOMContentLoaded', function() {
    loadProjectInfo();
});

function loadProjectInfo() {
    fetch('/api/project-info')
        .then(response => response.json())
        .then(data => {
            displayProjectOverview(data);
            if (data.data_stats) displayDatasetInfo(data.data_stats);
            if (data.performance) displayPerformance(data.performance);
            if (data.features) displayFeatures(data.features);
            if (data.models) displayModels(data.models);
        });
}

function displayProjectOverview(data) {
    const titleElem = document.getElementById('projectTitle');
    const descElem = document.getElementById('projectDesc');
    if (titleElem) titleElem.textContent = data.title;
    if (descElem) descElem.textContent = data.description;
}

function displayDatasetInfo(stats) {
    const container = document.getElementById('datasetInfo');
    if (!container) return;
    
    container.innerHTML = `
        <table class="table">
            <tr><td><strong>Stores:</strong></td><td>${stats.stores}</td></tr>
            <tr><td><strong>Departments:</strong></td><td>${stats.departments}</td></tr>
            <tr><td><strong>Total Records:</strong></td><td>${stats.records.toLocaleString()}</td></tr>
            <tr><td><strong>Date Range:</strong></td><td>${stats.date_range}</td></tr>
        </table>
    `;
}

function displayPerformance(performance) {
    const container = document.getElementById('performanceInfo');
    if (!container) return;
    
    container.innerHTML = `
        <table class="table">
            <tr><td><strong>RMSE:</strong></td><td><span class="badge bg-success">${performance.RMSE}</span></td></tr>
            <tr><td><strong>MAE:</strong></td><td><span class="badge bg-success">${performance.MAE}</span></td></tr>
            <tr><td><strong>R² Score:</strong></td><td><span class="badge bg-success">${performance['R Score']}</span></td></tr>
        </table>
    `;
}

function displayFeatures(features) {
    const container = document.getElementById('featuresContainer');
    if (!container) return;
    container.innerHTML = '';

    features.forEach(feature => {
        const col = document.createElement('div');
        col.className = 'col-md-6 mb-2';
        col.innerHTML = `<div class="card p-2"><span><i class="bi bi-check"></i> ${feature}</span></div>`;
        container.appendChild(col);
    });
}

function displayModels(models) {
    const container = document.getElementById('modelsContainer');
    if (!container) return;
    container.innerHTML = '';

    models.forEach(model => {
        const col = document.createElement('div');
        col.className = 'col-md-4 mb-2';
        col.innerHTML = `<div class="card p-3 text-center"><h6>${model}</h6></div>`;
        container.appendChild(col);
    });
}
