const KEY = 'autosolari_measurements_v1';

function read() {
  try { return JSON.parse(localStorage.getItem(KEY) || '[]'); } catch { return []; }
}
function write(data) { localStorage.setItem(KEY, JSON.stringify(data)); }
function fmt(n) { return Number(n || 0).toFixed(2); }

function render() {
  const data = read().sort((a,b)=> b.day.localeCompare(a.day));
  const tbody = document.getElementById('rows');
  tbody.innerHTML = '';

  let totalProd = 0, totalCons = 0, totalKm = 0;
  for (const row of data) {
    totalProd += Number(row.production_kwh);
    totalCons += Number(row.consumption_kwh);
    totalKm += Number(row.km_travelled);

    const tr = document.createElement('tr');
    tr.innerHTML = `<td>${row.day}</td><td>${fmt(row.production_kwh)}</td><td>${fmt(row.consumption_kwh)}</td><td>${fmt(row.km_travelled)}</td><td><button class="btn btn-sm btn-outline-danger">Elimina</button></td>`;
    tr.querySelector('button').onclick = () => {
      write(read().filter((x) => x.id !== row.id));
      render();
    };
    tbody.appendChild(tr);
  }

  if (!data.length) {
    tbody.innerHTML = '<tr><td colspan="5" class="text-center text-muted">Nessuna misurazione.</td></tr>';
  }

  document.getElementById('kpi-prod').textContent = `${fmt(totalProd)} kWh`;
  document.getElementById('kpi-cons').textContent = `${fmt(totalCons)} kWh`;
  document.getElementById('kpi-km').textContent = `${fmt(totalKm)} km`;
}

document.getElementById('measurement-form').addEventListener('submit', (e) => {
  e.preventDefault();
  const day = document.getElementById('day').value;
  const production = document.getElementById('production').value;
  const consumption = document.getElementById('consumption').value;
  const km = document.getElementById('km').value;

  const data = read();
  data.push({ id: crypto.randomUUID(), day, production_kwh: Number(production), consumption_kwh: Number(consumption), km_travelled: Number(km) });
  write(data);
  e.target.reset();
  render();
});

document.getElementById('clear-all').addEventListener('click', () => {
  localStorage.removeItem(KEY);
  render();
});

render();
