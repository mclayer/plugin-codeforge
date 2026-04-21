const TICK_ICONS = { UP: '\u2191', DOWN: '\u2193', ZERO_UP: '\u2191', ZERO_DOWN: '\u2193' };
const BUCKET_CLASSES = {
  small: '',
  medium: 'fw-medium',
  large: 'fw-bold tape-large',
  whale: 'fw-bold tape-whale'
};

function loadTape() {
  const symbol = document.getElementById('tape-symbol').value;
  const startVal = document.getElementById('tape-start').value;
  const endVal = document.getElementById('tape-end').value;
  const startMs = startVal ? new Date(startVal).getTime() : 0;
  const endMs = endVal ? new Date(endVal).getTime() : Date.now();

  fetch(`/api/data/trades/tape?symbol=${encodeURIComponent(symbol)}&start_ts=${startMs}&end_ts=${endMs}&limit=500`)
    .then(r => r.json())
    .then(data => renderTape(data.entries || []))
    .catch(err => {
      document.getElementById('tape-body').innerHTML =
        `<tr><td colspan="7" class="text-danger text-center">${err}</td></tr>`;
    });
}

function renderTape(entries) {
  const rows = [...entries].reverse();
  const html = rows.map(e => {
    const sideClass = e.side === 'buy' ? 'text-success' : 'text-danger';
    const bucketClass = BUCKET_CLASSES[e.size_bucket] || '';
    const tickIcon = TICK_ICONS[e.tick_dir] || '\u00b7';
    const timeStr = new Date(e.ts).toLocaleTimeString('ko-KR', {
      hour12: false, hour: '2-digit', minute: '2-digit', second: '2-digit'
    });
    const notionalFmt = Number(e.notional).toLocaleString('ko-KR', { maximumFractionDigits: 0 });
    return `<tr class="${sideClass} ${bucketClass}">
      <td class="small">${timeStr}</td>
      <td>${tickIcon} ${Number(e.price).toLocaleString('ko-KR')}</td>
      <td>${e.qty}</td>
      <td class="small">${notionalFmt}</td>
      <td>${e.side.toUpperCase()}</td>
      <td class="small text-muted">${e.tick_dir}</td>
      <td class="small">${e.size_bucket}</td>
    </tr>`;
  }).join('');
  document.getElementById('tape-body').innerHTML = html || '<tr><td colspan="7" class="text-secondary text-center">No entries.</td></tr>';
}
