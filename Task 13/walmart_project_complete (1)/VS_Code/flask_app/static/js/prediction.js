document.addEventListener('DOMContentLoaded', function() {
    const predictionForm = document.getElementById('predictionForm');
    const storeSelect = document.getElementById('storeSelect');
    
    if (predictionForm) {
        predictionForm.addEventListener('submit', handlePrediction);
    }
    
    if (storeSelect) {
        storeSelect.addEventListener('change', function() {
            const storeId = this.value;
            if (storeId) {
                loadValidDepartments(storeId);
            }
        });
    }
});

function loadValidDepartments(storeId) {
    const deptSelect = document.getElementById('deptSelect');
    if (!deptSelect) return;
    
    deptSelect.disabled = true;
    deptSelect.innerHTML = '<option value="">Loading...</option>';
    
    fetch(`/api/combinations/${storeId}`)
        .then(response => response.json())
        .then(data => {
            deptSelect.innerHTML = '<option value="">Choose a department...</option>';
            data.departments.forEach(dept => {
                const option = document.createElement('option');
                option.value = dept;
                option.textContent = `Department ${dept}`;
                deptSelect.appendChild(option);
            });
            deptSelect.disabled = false;
        });
}

function handlePrediction(e) {
    e.preventDefault();
    
    const store = document.getElementById('storeSelect').value;
    const dept = document.getElementById('deptSelect').value;

    if (!store || !dept) {
        alert('Please select both store and department');
        return;
    }

    fetch('/api/predict', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ store: parseInt(store), department: parseInt(dept) })
    })
    .then(response => response.json())
    .then(data => {
        if (data.status === 'success') {
            displayPrediction(data.prediction);
        } else {
            alert(data.message);
        }
    });
}

function displayPrediction(prediction) {
    const resultCard = document.getElementById('resultCard');
    const noResultCard = document.getElementById('noResultCard');

    if (!resultCard || !noResultCard) return;

    document.getElementById('predictedSales').textContent = '$' + prediction.predicted_sales.toLocaleString();
    document.getElementById('confidence').textContent = prediction.confidence + '%';
    
    document.getElementById('resultStore').textContent = `Store #${prediction.store}`;
    document.getElementById('resultDept').textContent = `Department #${prediction.department}`;
    document.getElementById('histAvg').textContent = '$' + prediction.historical_avg.toLocaleString();

    resultCard.style.display = 'block';
    noResultCard.style.display = 'none';
}
