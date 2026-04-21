function loadLadder() {
  const symbol = document.getElementById('ladder-symbol').value;
  const tsInput = document.getElementById('ladder-ts').value;
  const tsMs = tsInput ? new Date(tsInput).getTime() : 0;

  fetch(`/api/data/orderbook/snapshot?symbol=${encodeURIComponent(symbol)}&ts=${tsMs}&depth=20`)
    .then(r => r.json())
    .then(data => renderLadder(data))
    .catch(err => {
      document.getElementById('ladder-body').innerHTML =
        `<tr><td colspan="3" class="text-danger text-center">${err}</td></tr>`;
    });
}

function renderLadder(data) {
  const metrics = document.getElementById('ladder-metrics');
  metrics.textContent = `Mid: ${fmtPrice(data.mid_price)}  Spread: ${data.spread_bps != null ? data.spread_bps.toFixed(2) : '—'} bps  Imbalance: ${data.imbalance != null ? data.imbalance.toFixed(3) : '—'}`;

  renderImbalanceGauge(data.imbalance);

  const asks = [...(data.asks || [])].reverse();
  const bids = data.bids || [];

  let html = '';
  for (const lvl of asks) {
    const pct = lvl.depth_pct || 0;
    const barStyle = `background: linear-gradient(to left, rgba(220,53,69,0.3) ${pct}%, transparent ${pct}%)`;
    html += `<tr class="ask-row" style="${barStyle}">
      <td class="text-end text-muted">\u2014</td>
      <td class="text-center fw-bold">${fmtPrice(lvl.price)}</td>
      <td class="text-danger">${lvl.qty}</td>
    </tr>`;
  }
  html += `<tr class="table-secondary"><td colspan="3" class="text-center small">\u2500\u2500\u2500 mid: ${fmtPrice(data.mid_price)} \u2500\u2500\u2500</td></tr>`;
  for (const lvl of bids) {
    const pct = lvl.depth_pct || 0;
    const barStyle = `background: linear-gradient(to right, rgba(25,135,84,0.3) ${pct}%, transparent ${pct}%)`;
    html += `<tr class="bid-row" style="${barStyle}">
      <td class="text-success text-end">${lvl.qty}</td>
      <td class="text-center fw-bold">${fmtPrice(lvl.price)}</td>
      <td class="text-muted">\u2014</td>
    </tr>`;
  }

  document.getElementById('ladder-body').innerHTML = html;
}

function renderImbalanceGauge(imbalance) {
  if (imbalance == null) {
    document.getElementById('imbalance-gauge').innerHTML = '';
    return;
  }
  const pct = Math.round((imbalance + 1) / 2 * 100);
  const color = imbalance > 0.3 ? '#198754' : imbalance < -0.3 ? '#dc3545' : '#6c757d';
  document.getElementById('imbalance-gauge').innerHTML = `
    <div class="d-flex align-items-center gap-2">
      <span class="small">Imbalance</span>
      <div style="flex:1;height:12px;background:#e9ecef;border-radius:4px;position:relative">
        <div style="position:absolute;left:${pct}%;width:4px;height:12px;background:${color};transform:translateX(-50%);border-radius:2px"></div>
        <div style="position:absolute;left:50%;width:1px;height:12px;background:#adb5bd"></div>
      </div>
      <span class="small" style="color:${color}">${imbalance.toFixed(3)}</span>
    </div>`;
}

function fmtPrice(p) {
  if (p == null) return '\u2014';
  return Number(p).toLocaleString('ko-KR');
}
