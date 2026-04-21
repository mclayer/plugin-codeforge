let imbalanceChartInstance = null;

function loadImbalance() {
  const symbol = document.getElementById('imb-symbol').value;
  const startVal = document.getElementById('imb-start').value;
  const endVal = document.getElementById('imb-end').value;
  const startMs = startVal ? new Date(startVal).getTime() : 0;
  const endMs = endVal ? new Date(endVal).getTime() : Date.now();
  const bucketMs = parseInt(document.getElementById('imb-bucket').value) || 250;

  fetch(`/api/data/orderbook/imbalance-series?symbol=${encodeURIComponent(symbol)}&start_ts=${startMs}&end_ts=${endMs}&bucket_ms=${bucketMs}`)
    .then(r => r.json())
    .then(data => renderImbalanceChart(data.points || []))
    .catch(err => console.error('imbalance-series error:', err));
}

function renderImbalanceChart(points) {
  const ctx = document.getElementById('imbalance-chart').getContext('2d');
  if (imbalanceChartInstance) {
    imbalanceChartInstance.destroy();
    imbalanceChartInstance = null;
  }

  imbalanceChartInstance = new Chart(ctx, {
    type: 'line',
    data: {
      labels: points.map(p => new Date(p.ts).toLocaleTimeString('ko-KR', { hour12: false })),
      datasets: [{
        label: 'Imbalance',
        data: points.map(p => p.imbalance),
        borderColor: '#0d6efd',
        borderWidth: 1.5,
        pointRadius: 0,
        tension: 0.1
      }]
    },
    options: {
      scales: {
        y: {
          min: -1,
          max: 1,
          grid: { color: 'rgba(255,255,255,0.1)' }
        },
        x: { ticks: { maxTicksLimit: 10 } }
      },
      plugins: {
        annotation: {
          annotations: {
            zeroline: { type: 'line', yMin: 0, yMax: 0, borderColor: '#adb5bd', borderWidth: 1 },
            posThreshold: { type: 'line', yMin: 0.3, yMax: 0.3, borderColor: '#198754', borderWidth: 1, borderDash: [5, 3] },
            negThreshold: { type: 'line', yMin: -0.3, yMax: -0.3, borderColor: '#dc3545', borderWidth: 1, borderDash: [5, 3] }
          }
        },
        legend: { display: false }
      }
    }
  });
}
