document.addEventListener('DOMContentLoaded', function() {
    const tableBody = document.querySelector('#metrics-table tbody');
    const searchInput = document.getElementById('search');
    let metrics = {};

    function renderTable(data) {
        tableBody.innerHTML = '';
        Object.entries(data).forEach(([agency, vals]) => {
            const row = document.createElement('tr');
            row.innerHTML = `<td>${agency}</td><td>${vals.word_count}</td><td>${vals.checksum}</td><td>${vals.readability.toFixed(2)}</td>`;
            tableBody.appendChild(row);
        });
    }

    function filterTable() {
        const q = searchInput.value.toLowerCase();
        const filtered = Object.fromEntries(Object.entries(metrics).filter(([k]) => k.toLowerCase().includes(q)));
        renderTable(filtered);
    }

    fetch('/api/metrics')
        .then(r => r.json())
        .then(data => {
            metrics = data;
            renderTable(metrics);
            renderChart(metrics);
        });

    searchInput.addEventListener('input', filterTable);

    function renderChart(metrics) {
        // Placeholder: If historical data is available, plot it here
        const ctx = document.getElementById('historyChart').getContext('2d');
        const labels = Object.keys(metrics);
        const data = Object.values(metrics).map(m => m.word_count);
        new Chart(ctx, {
            type: 'line',
            data: {
                labels: labels,
                datasets: [{
                    label: 'Word Count',
                    data: data,
                    borderColor: '#2980b9',
                    fill: false
                }]
            },
            options: {
                responsive: true,
                plugins: { legend: { display: false } },
                scales: { x: { display: false } }
            }
        });
    }
});
