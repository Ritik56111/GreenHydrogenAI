
import React, { useEffect, useState } from 'react';
import { createRoot } from 'react-dom/client';
import axios from 'axios';
import {
  LineChart, Line, XAxis, YAxis, CartesianGrid,
  Tooltip, ResponsiveContainer, BarChart, Bar
} from 'recharts';
import {
  Leaf, Sun, Wind, Droplets, Factory, BrainCircuit,
  RefreshCw, AlertTriangle, Target, Zap, FlaskConical,
  TrendingUp, Activity, LayoutDashboard
} from 'lucide-react';
import './style.css';

const api = axios.create({ baseURL: '' });

const base = {
  solar: 100,
  wind: 50,
  hydro: 25,
  temperature: 28,
  humidity: 50,
  electrolyzer_efficiency: 0.78
};

const nav = [
  ['Dashboard', LayoutDashboard],
  ['AI Intelligence', BrainCircuit],
  ['Energy Monitor', Activity],
  ['Hydrogen Prediction', Target],
  ['Optimization', Zap],
  ['What-If Simulator', FlaskConical],
  ['Forecast', TrendingUp],
  ['Anomaly Detection', AlertTriangle]
];

function Card({ icon, title, value, unit = '' }) {
  return (
    <div className="card stat">
      <div className="icon">{icon}</div>
      <div>
        <small>{title}</small>
        <h2>{value ?? '—'} <em>{unit}</em></h2>
      </div>
    </div>
  );
}

function App() {
  const [page, setPage] = useState('Dashboard');
  const [d, setD] = useState(null);
  const [hist, setHist] = useState([]);
  const [err, setErr] = useState('');
  const [loading, setLoading] = useState(true);

  async function load() {
    setLoading(true);
    try {
      const [a, b] = await Promise.all([
        api.get('/api/dashboard'),
        api.get('/api/history')
      ]);
      setD(a.data);
      setHist(Array.isArray(b.data) ? b.data : []);
      setErr('');
    } catch (e) {
      setErr('Backend connect nahi ho raha. Check karo ki FastAPI port 8000 par running hai.');
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => { load(); }, []);

  return (
    <div className="shell">
      <aside>
        <div className="brand">
          <Leaf />
          <b>Green Hydrogen<br /><span>AI Platform</span></b>
        </div>
        {nav.map(([name, Icon]) => (
          <button
            key={name}
            className={page === name ? 'active' : ''}
            onClick={() => setPage(name)}
          >
            <Icon size={18} /> {name}
          </button>
        ))}
        <div className="note">
          NEXAI<br />
          <small>Renewable intelligence & simulation</small>
        </div>
      </aside>

      <main>
        <header>
          <div>
            <small>AI-POWERED RENEWABLE INTELLIGENCE</small>
            <h1>{page}</h1>
          </div>
          <button className="refresh" onClick={load}>
            <RefreshCw size={16} /> Refresh
          </button>
        </header>

        {err && <div className="error">{err}</div>}
        {loading && !d ? <p>Loading dashboard...</p> : null}

        {d && page === 'Dashboard' && (
          <Dashboard d={d} hist={hist} go={setPage} />
        )}
        {page === 'AI Intelligence' && <AnalysisPage />}
        {page === 'Hydrogen Prediction' && (
          <AnalysisPage title="Hydrogen Prediction" endpoint="/api/predict" />
        )}
        {page === 'Optimization' && (
          <AnalysisPage title="Smart Optimization" endpoint="/api/optimize" efficiency />
        )}
        {page === 'What-If Simulator' && (
          <AnalysisPage title="What-If Simulator" endpoint="/api/what-if" />
        )}
        {page === 'Anomaly Detection' && (
          <AnalysisPage title="Anomaly Detection" endpoint="/api/anomaly" />
        )}
        {page === 'Forecast' && <ForecastPage />}
        {d && page === 'Energy Monitor' && <Energy d={d} hist={hist} />}
      </main>
    </div>
  );
}

function Dashboard({ d, hist, go }) {
  const data = hist.slice(-24).map((x, i) => ({
    ...x,
    time: x.timestamp
      ? new Date(x.timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
      : `T${i + 1}`
  }));

  return (
    <>
      <section className="hero">
        <div>
          <small>● SYSTEM MONITORING</small>
          <h2>AI-driven green hydrogen optimization</h2>
          <p>Monitor renewable inputs, estimate hydrogen yield and explore system insights.</p>
        </div>
        <div className="score">
          <small>AI CONFIDENCE</small>
          <strong>{d.ai_confidence ?? d.confidence ?? '—'}{(d.ai_confidence ?? d.confidence) != null ? '%' : ''}</strong>
        </div>
      </section>

      <div className="grid">
        <Card icon={<Sun />} title="Solar Energy" value={d.solar} unit="kW" />
        <Card icon={<Wind />} title="Wind Energy" value={d.wind} unit="kW" />
        <Card icon={<Droplets />} title="Hydro Energy" value={d.hydro} unit="kW" />
        <Card icon={<Factory />} title="Estimated Hydrogen" value={d.hydrogen} unit="kg/day" />
      </div>

      <div className="grid three">
        <Card icon={<Zap />} title="Efficiency" value={d.efficiency} unit="%" />
        <Card icon={<Leaf />} title="Carbon Saving" value={d.carbon_saving} unit="kg CO₂" />
        <Card icon={<Activity />} title="Renewable Total" value={d.total_renewable} unit="kW" />
      </div>

      <div className="charts">
        <Chart title="Hydrogen Production Trend">
          <ResponsiveContainer width="100%" height={260}>
            <LineChart data={data}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="time" />
              <YAxis />
              <Tooltip />
              <Line type="monotone" dataKey="hydrogen" stroke="#26b981" strokeWidth={3} />
            </LineChart>
          </ResponsiveContainer>
        </Chart>

        <Chart title="Renewable Energy Mix">
          <ResponsiveContainer width="100%" height={260}>
            <BarChart data={[
              { name: 'Solar', value: Number(d.solar) || 0 },
              { name: 'Wind', value: Number(d.wind) || 0 },
              { name: 'Hydro', value: Number(d.hydro) || 0 }
            ]}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="name" />
              <YAxis />
              <Tooltip />
              <Bar dataKey="value" fill="#26b981" radius={[5, 5, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </Chart>
      </div>

      <section className="panel insight">
        <BrainCircuit size={28} />
        <div>
          <h3>AI Executive Insight</h3>
          <p>{d.dominant_source || 'Renewables'} is the dominant source in the current simulated scenario.</p>
        </div>
        <button className="primary" onClick={() => go('AI Intelligence')}>
          Analyze System
        </button>
      </section>
      <p className="disclaimer">Simulation and decision support only. Hydrogen values are estimates, not physical plant measurements.</p>
    </>
  );
}

function Chart({ title, children }) {
  return <section className="panel"><h3>{title}</h3>{children}</section>;
}

function Energy({ d, hist }) {
  return (
    <>
      <div className="grid three">
        <Card icon={<Sun />} title="Solar" value={d.solar} unit="kW" />
        <Card icon={<Wind />} title="Wind" value={d.wind} unit="kW" />
        <Card icon={<Droplets />} title="Hydro" value={d.hydro} unit="kW" />
      </div>
      <Chart title="Renewable Energy History">
        <ResponsiveContainer width="100%" height={350}>
          <LineChart data={hist}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="timestamp" hide />
            <YAxis />
            <Tooltip />
            <Line type="monotone" dataKey="solar" stroke="#eab308" dot={false} />
            <Line type="monotone" dataKey="wind" stroke="#38bdf8" dot={false} />
            <Line type="monotone" dataKey="hydro" stroke="#26b981" dot={false} />
          </LineChart>
        </ResponsiveContainer>
      </Chart>
    </>
  );
}

function AnalysisPage({
  title = 'AI Intelligence & Analysis',
  endpoint = '/api/ai/analyze',
  efficiency = false
}) {
  const [f, setF] = useState({ ...base });
  const [r, setR] = useState(null);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState('');

  function update(key, value) {
    setF(old => ({ ...old, [key]: value }));
  }

  async function run() {
    setBusy(true);
    setError('');
    setR(null);
    try {
      const response = await api.post(endpoint, f);
      setR(response.data);
    } catch (e) {
      setError(e.response?.data?.detail || 'Analysis failed. Backend endpoint aur server status check karein.');
    } finally {
      setBusy(false);
    }
  }

  return (
    <>
      <section className="panel form">
        <h2>{title}</h2>
        <p>Inputs change karke simulated system analysis run karein.</p>
        <div className="fields">
          {[
            ['solar', 'Solar Energy (kW)', 0],
            ['wind', 'Wind Energy (kW)', 0],
            ['hydro', 'Hydro Energy (kW)', 0],
            ['temperature', 'Temperature (°C)', -50],
            ['humidity', 'Humidity (%)', 0]
          ].map(([key, label, min]) => (
            <label key={key}>
              {label}
              <input
                type="number"
                min={min}
                value={f[key]}
                onChange={e => update(key, Number(e.target.value))}
              />
            </label>
          ))}
          {efficiency && (
            <label>
              Electrolyzer Efficiency (0–1)
              <input
                type="number"
                min="0"
                max="1"
                step="0.01"
                value={f.electrolyzer_efficiency}
                onChange={e => update('electrolyzer_efficiency', Number(e.target.value))}
              />
            </label>
          )}
        </div>
        <button className="primary" disabled={busy} onClick={run}>
          {busy ? 'Analyzing...' : 'Run Analysis'}
        </button>
        {error && <p className="error">{error}</p>}
      </section>
      <Result r={r} />
    </>
  );
}

function Result({ r }) {
  if (!r) {
    return (
      <section className="panel result empty-result">
        <BrainCircuit size={42} />
        <h2>AI Decision Center</h2>
        <p>Run analysis to view metrics, insights and recommendations.</p>
      </section>
    );
  }

  const status = r.status || r.overall_status || 'Analysis Complete';
  const confidence = r.confidence ?? r.ai_confidence;
  const hydrogen = r.hydrogen ?? r.hydrogen_kg_day ?? r.predicted_hydrogen;
  const efficiency = r.efficiency ?? r.efficiency_score;
  const carbon = r.carbon_saving ?? r.carbon_saving_kgco2;
  const dominant = r.dominant_source || r.recommended_source || 'Renewable mix';
  const insights = Array.isArray(r.insights) ? r.insights : [];
  const recommendations = Array.isArray(r.recommendations) ? r.recommendations : [];
  const otherMetrics = Object.entries(r).filter(([k, v]) =>
    !['status', 'overall_status', 'confidence', 'ai_confidence', 'hydrogen',
      'hydrogen_kg_day', 'predicted_hydrogen', 'efficiency', 'efficiency_score',
      'carbon_saving', 'carbon_saving_kgco2', 'dominant_source', 'insights',
      'recommendations'].includes(k) && typeof v !== 'object'
  );

  return (
    <section className="panel result">
      <div className="result-header">
        <div>
          <small>ANALYSIS REPORT</small>
          <h2>System Intelligence</h2>
        </div>
        <span className="status-badge">{String(status).replaceAll('_', ' ')}</span>
      </div>

      <div className="grid">
        {confidence != null && <Card icon={<BrainCircuit />} title="AI Confidence" value={confidence} unit="%" />}
        {hydrogen != null && <Card icon={<Factory />} title="Hydrogen Yield" value={hydrogen} unit="kg/day" />}
        {efficiency != null && <Card icon={<Zap />} title="Efficiency" value={efficiency} unit="%" />}
        {carbon != null && <Card icon={<Leaf />} title="Carbon Saving" value={carbon} unit="kg CO₂" />}
        <Card icon={<Sun />} title="Dominant Source" value={dominant} />
      </div>

      {otherMetrics.length > 0 && (
        <div className="grid">
          {otherMetrics.map(([key, value]) => (
            <Card
              key={key}
              icon={<Activity />}
              title={key.replaceAll('_', ' ')}
              value={String(value)}
            />
          ))}
        </div>
      )}

      {insights.length > 0 && (
        <div className="result-section">
          <h3>💡 AI Insights</h3>
          {insights.map((item, i) => (
            <div className="insight-item" key={i}><span>✓</span><p>{String(item)}</p></div>
          ))}
        </div>
      )}

      {recommendations.length > 0 && (
        <div className="result-section">
          <h3>🎯 Recommendations</h3>
          {recommendations.map((item, i) => (
            <div className="recommendation-item" key={i}><span>→</span><p>{String(item)}</p></div>
          ))}
        </div>
      )}
    </section>
  );
}

function ForecastPage() {
  const [f, setF] = useState({ ...base });
  const [data, setData] = useState([]);
  const [error, setError] = useState('');
  const [busy, setBusy] = useState(false);

  async function generate() {
    setBusy(true);
    setError('');
    try {
      const response = await api.post('/api/forecast', f);
      const rows = response.data.forecast ?? response.data;
      setData(Array.isArray(rows) ? rows : []);
    } catch (e) {
      setError('Forecast generate nahi hua. Backend endpoint check karein.');
    } finally {
      setBusy(false);
    }
  }

  return (
    <>
      <section className="panel">
        <h2>24-Hour Hydrogen Forecast</h2>
        <p>Forecast is an estimate based on the current simulated inputs.</p>
        <button className="primary" onClick={generate} disabled={busy}>
          {busy ? 'Generating...' : 'Generate Forecast'}
        </button>
        {error && <p className="error">{error}</p>}
      </section>
      {data.length > 0 && (
        <Chart title="Renewable Availability & Hydrogen Yield">
          <ResponsiveContainer width="100%" height={350}>
            <LineChart data={data}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="hour" />
              <YAxis />
              <Tooltip />
              <Line type="monotone" dataKey="renewable" stroke="#38bdf8" strokeWidth={2} />
              <Line type="monotone" dataKey="hydrogen" stroke="#26b981" strokeWidth={3} />
            </LineChart>
          </ResponsiveContainer>
        </Chart>
      )}
    </>
  );
}

createRoot(document.getElementById('root')).render(<App />);
