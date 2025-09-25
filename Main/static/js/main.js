document.getElementById('queryForm').addEventListener('submit', async function(e) {
    e.preventDefault();
    
    document.querySelector('.loading').style.display = 'block';
    document.querySelector('.results-container').style.display = 'none';
    document.getElementById('errorAlert').style.display = 'none';
    
    try {
        const formData = new FormData(this);
        const params = new URLSearchParams(formData).toString();

        const response = await fetch(`/api/municipality-data?${params}`, {
            method: 'GET'
        });

        const data = await response.json();

        if (!response.ok) {
            throw new Error(data.error || 'Failed to fetch data');
        }

        displayResults(data, formData);

    } catch (error) {
        showError(error.message);
    } finally {
        document.querySelector('.loading').style.display = 'none';
    }
});

function displayResults(data, formData) {
    if (!data.cells || data.cells.length === 0) {
        showError('No data found for the selected criteria');
        return;
    }
    
    const totalAmount = data.cells.reduce((sum, cell) => sum + (cell['amount.sum'] || 0), 0);
    const municipalityName = data.cells[0].municipality_name || formData.get('municipality');
    
    document.getElementById('totalAmount').textContent = formatCurrency(totalAmount);
    document.getElementById('itemCount').textContent = data.cells.length;
    document.getElementById('queryInfo').textContent = `${municipalityName} ${formData.get('year')}`;
    
    const tbody = document.getElementById('resultsBody');
    tbody.innerHTML = '';
    
    data.cells.forEach(cell => {
        const row = document.createElement('tr');
        const amount = cell['amount.sum'] || 0;
        const amountClass = amount >= 0 ? 'amount-positive' : 'amount-negative';
        
        row.innerHTML = `
            <td><code>${cell['item.code'] || '-'}</code></td>
            <td>${cell['item.label'] || '-'}</td>
            <td><small class="text-muted">${cell['function.label'] || '-'}</small></td>
            <td class="text-end ${amountClass}"><strong>${formatCurrency(amount)}</strong></td>
        `;
        tbody.appendChild(row);
    });
    
    document.querySelector('.results-container').style.display = 'block';
}

function showError(message) {
    document.getElementById('errorMessage').textContent = message;
    document.getElementById('errorAlert').style.display = 'block';
    document.getElementById('errorAlert').classList.add('show');
}

function formatCurrency(amount) {
    return new Intl.NumberFormat('en-ZA', {
        style: 'currency',
        currency: 'ZAR',
        minimumFractionDigits: 2
    }).format(amount);
}
