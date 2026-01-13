import React, { useCallback, useEffect, useMemo, useRef, useState } from 'react';
import './ParityDashboard.css';

const API_BASE = 'http://localhost:5050';

const toEpoch = (value) => {
  if (value === null || value === undefined) return null;
  if (typeof value === 'number') return value;
  if (typeof value === 'string') {
    const asFloat = Number(value);
    if (!Number.isNaN(asFloat)) return asFloat;
    const parsed = Date.parse(value);
    if (!Number.isNaN(parsed)) return parsed / 1000;
  }
  return null;
};

const formatTs = (value) => {
  const epoch = toEpoch(value);
  if (!epoch) return '—';
  return new Date(epoch * 1000).toISOString();
};

const ParityDashboard = () => {
  const [snapshot, setSnapshot] = useState(null);
  const [events, setEvents] = useState([]);
  const [refreshMs, setRefreshMs] = useState(2000);
  const [pollMs, setPollMs] = useState(2000);
  const [windowSec, setWindowSec] = useState(300);
  const [density, setDensity] = useState('compact');
  const [sortMode, setSortMode] = useState('iss');
  const [controlTarget, setControlTarget] = useState('GOAT');
  const [controlAction, setControlAction] = useState('pause_ingest');
  const [controlParams, setControlParams] = useState('{}');
  const [controlStatus, setControlStatus] = useState(null);

  const [surfaceFilter, setSurfaceFilter] = useState('all');
  const [targetFilter, setTargetFilter] = useState('all');
  const [typeFilter, setTypeFilter] = useState('all');
  const [routingFilter, setRoutingFilter] = useState('all');

  const lastEventTsRef = useRef(null);

  const fetchSnapshot = useCallback(async () => {
    try {
      const res = await fetch(`${API_BASE}/state/snapshot`);
      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      const data = await res.json();
      setSnapshot(data);
    } catch (err) {
      console.error('snapshot error', err);
    }
  }, []);

  useEffect(() => {
    fetchSnapshot();
    const id = setInterval(fetchSnapshot, Math.max(500, refreshMs));
    return () => clearInterval(id);
  }, [fetchSnapshot, refreshMs]);

  useEffect(() => {
    let stopped = false;

    const poll = async () => {
      const since = lastEventTsRef.current;
      const qs = since ? `?since=${since}` : '';
      try {
        const res = await fetch(`${API_BASE}/state/events${qs}`);
        if (!res.ok) throw new Error(`HTTP ${res.status}`);
        const data = await res.json();
        const incoming = data.events || [];
        if (incoming.length) {
          const maxTs = incoming.reduce((acc, ev) => {
            const ts = toEpoch(ev.timestamp);
            return ts && ts > acc ? ts : acc;
          }, since || 0);
          if (maxTs) lastEventTsRef.current = maxTs;
        }

        setEvents((prev) => {
          const merged = [...prev, ...incoming];
          const cutoff = Date.now() / 1000 - windowSec;
          return merged.filter((ev) => {
            const ts = toEpoch(ev.timestamp) || 0;
            return ts >= cutoff;
          });
        });
      } catch (err) {
        console.error('events error', err);
      }
      if (!stopped) {
        setTimeout(poll, Math.max(500, pollMs));
      }
    };

    poll();
    return () => {
      stopped = true;
    };
  }, [pollMs, windowSec]);

  const submitControl = async () => {
    let paramsObj = {};
    try {
      paramsObj = controlParams.trim() ? JSON.parse(controlParams) : {};
    } catch (err) {
      setControlStatus({ error: 'Invalid JSON for params' });
      return;
    }

    const packet = {
      actor: 'Dashboard',
      surface: 'Dashboard',
      target: controlTarget,
      action: controlAction,
      params: paramsObj,
      timestamp: new Date().toISOString(),
    };

    try {
      const res = await fetch(`${API_BASE}/control/submit`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(packet),
      });
      const data = await res.json();
      setControlStatus({ ok: true, outcome: data.outcome });
    } catch (err) {
      setControlStatus({ error: err.message });
    }
  };

  const coreEntries = useMemo(() => Object.entries(snapshot?.cores || {}), [snapshot]);
  const systemEntries = useMemo(() => Object.entries(snapshot?.systems || {}), [snapshot]);

  const filteredEvents = useMemo(() => {
    return events.filter((ev) => {
      const via = ev.via === 'dals' ? 'via_dals' : ev.via;
      if (surfaceFilter !== 'all' && ev.surface !== surfaceFilter) return false;
      if (targetFilter !== 'all' && ev.target !== targetFilter) return false;
      if (typeFilter !== 'all' && ev.type !== typeFilter) return false;
      if (routingFilter !== 'all' && via !== routingFilter) return false;
      return true;
    });
  }, [events, surfaceFilter, targetFilter, typeFilter, routingFilter]);

  const sortedEvents = useMemo(() => {
    const score = (ev) => {
      if (sortMode === 'iss') {
        if (ev.iss) return { key: ev.iss, has: true };
      }
      const ts = toEpoch(ev.timestamp) || 0;
      return { key: ts, has: false };
    };
    return filteredEvents
      .slice()
      .sort((a, b) => {
        const sa = score(a);
        const sb = score(b);
        // Prefer ISS ordering if both have ISS; fallback to timestamp
        if (sortMode === 'iss' && sa.has !== sb.has) {
          // those with ISS sort before those without
          return sa.has ? -1 : 1;
        }
        if (sa.has && sb.has) {
          return sa.key < sb.key ? 1 : sa.key > sb.key ? -1 : 0;
        }
        return sb.key - sa.key;
      });
  }, [filteredEvents, sortMode]);

  const eventsPerMinute = useMemo(() => {
    if (windowSec <= 0) return 0;
    return Math.round((filteredEvents.length / windowSec) * 60);
  }, [filteredEvents.length, windowSec]);

  const divergence = useMemo(() => {
    if (snapshot?.divergence) return true;
    const cores = snapshot?.cores || {};
    return Object.values(cores).some((c) => {
      const avail = (c?.availability || '').toUpperCase();
      return (avail === 'SILENT' || avail === 'UNAVAILABLE') && c?.last_assertion;
    });
  }, [snapshot]);

  const assertionDetails = useMemo(() => {
    const cores = snapshot?.cores || {};
    return Object.entries(cores)
      .filter(([, c]) => c?.last_assertion)
      .map(([name, c]) => ({ name, assertion: c.last_assertion }));
  }, [snapshot]);

  const targetLanes = useMemo(() => {
    const lanes = {};
    filteredEvents.forEach((ev) => {
      const lane = ev.target || 'unattributed';
      if (!lanes[lane]) lanes[lane] = [];
      lanes[lane].push(ev);
    });
    Object.values(lanes).forEach((lane) => lane.sort((a, b) => (toEpoch(a.timestamp) || 0) - (toEpoch(b.timestamp) || 0)));
    return lanes;
  }, [filteredEvents]);

  const integrity = snapshot?.integrity || {};

  return (
    <div className="parity-shell">
      <header className="parity-header">
        <div>
          <h1>Dashboard = Orb</h1>
          <p className="subtitle">Shared spine, two skins. Read-only state; packetized control.</p>
        </div>
        <div className="gauges">
          <label>
            Refresh (ms)
            <input type="number" value={refreshMs} onChange={(e) => setRefreshMs(Number(e.target.value) || 0)} />
          </label>
          <label>
            Poll (ms)
            <input type="number" value={pollMs} onChange={(e) => setPollMs(Number(e.target.value) || 0)} />
          </label>
          <label>
            Event window (sec)
            <input type="number" value={windowSec} onChange={(e) => setWindowSec(Number(e.target.value) || 0)} />
          </label>
          <label>
            Density
            <select value={density} onChange={(e) => setDensity(e.target.value)}>
              <option value="compact">compact</option>
              <option value="expanded">expanded</option>
            </select>
          </label>
          <label>
            Sort
            <select value={sortMode} onChange={(e) => setSortMode(e.target.value)}>
              <option value="iss">ISS</option>
              <option value="timestamp">timestamp</option>
            </select>
          </label>
        </div>
      </header>

      <section className="grid two">
        <div className="panel">
          <h3>Core availability</h3>
          <div className="list">
            {coreEntries.length === 0 && <div className="muted">No cores reported.</div>}
            {coreEntries.map(([name, state]) => (
              <div key={name} className="row">
                <div className="label">{name}</div>
                <div className={`pill ${state?.availability?.toLowerCase() || 'unknown'}`}>
                  {state?.availability || 'unknown'}
                </div>
                <div className="muted">last seen: {state?.last_seen ? formatTs(state.last_seen) : '—'}</div>
              </div>
            ))}
          </div>
        </div>

        <div className="panel">
          <h3>System connectivity</h3>
          <div className="list">
            {systemEntries.length === 0 && <div className="muted">No systems reported.</div>}
            {systemEntries.map(([name, state]) => (
              <div key={name} className="row">
                <div className="label">{name}</div>
                <div className={`pill ${state?.connected === true ? 'available' : state?.connected === false ? 'unavailable' : 'unknown'}`}>
                  {state?.connected === true ? 'connected' : state?.connected === false ? 'disconnected' : 'unknown'}
                </div>
                <div className="muted">last event: {formatTs(state?.last_event)}</div>
              </div>
            ))}
          </div>
        </div>
      </section>

      <section className="grid three">
        <div className="panel gauge-panel">
          <h3>Events per minute (windowed)</h3>
          <div className="gauge-value">{eventsPerMinute}</div>
          <div className="muted">Window: {windowSec}s</div>
        </div>
        <div className="panel gauge-panel">
          <h3>Control acceptance</h3>
          <div className={`pill ${snapshot?.controls?.accepting ? 'available' : 'unavailable'}`}>
            {snapshot?.controls?.accepting ? 'accepting' : 'not accepting'}
          </div>
          <div className="muted">routing mode: {JSON.stringify(snapshot?.controls?.routing_mode || {})}</div>
        </div>
        <div className="panel gauge-panel">
          <h3>Integrity signals</h3>
          <div className={`pill ${integrity?.integrity_status || 'unknown'}`}>{integrity?.integrity_status || 'unknown'}</div>
          <div className="muted">last snapshot: {formatTs(integrity?.last_snapshot_ts)}</div>
          <div className="muted">last event: {formatTs(integrity?.last_event_ts)}</div>
          <div className="muted">replay: {integrity?.replay_duration_ms ?? '—'} ms</div>
        </div>
        <div className="panel gauge-panel">
          <h3>ISS (reported)</h3>
          <div className="muted">iss_now: {snapshot?.iss_now || '—'}</div>
          <div className="muted">last_event_iss: {snapshot?.last_event_iss || '—'}</div>
        </div>
      </section>

      <section className="panel">
        <div className="filters">
          <label>Surface
            <select value={surfaceFilter} onChange={(e) => setSurfaceFilter(e.target.value)}>
              <option value="all">all</option>
              <option value="Orb">Orb</option>
              <option value="Dashboard">Dashboard</option>
            </select>
          </label>
          <label>Target
            <select value={targetFilter} onChange={(e) => setTargetFilter(e.target.value)}>
              <option value="all">all</option>
              <option value="GOAT">GOAT</option>
              <option value="DALS">DALS</option>
              <option value="TrueMark">TrueMark</option>
              <option value="CertSig">CertSig</option>
              <option value="CALI_ORCHESTRATOR">CALI_ORCHESTRATOR</option>
            </select>
          </label>
          <label>Event type
            <select value={typeFilter} onChange={(e) => setTypeFilter(e.target.value)}>
              <option value="all">all</option>
              <option value="intent_issued">intent_issued</option>
              <option value="outcome_observed">outcome_observed</option>
            </select>
          </label>
          <label>Routing
            <select value={routingFilter} onChange={(e) => setRoutingFilter(e.target.value)}>
              <option value="all">all</option>
              <option value="direct">direct</option>
              <option value="via_dals">via_dals</option>
            </select>
          </label>
        </div>
      </section>

      <section className="grid two">
        <div className="panel">
          <h3>Controls (packet only)</h3>
          <div className="form">
            <label>
              Target
              <select value={controlTarget} onChange={(e) => setControlTarget(e.target.value)}>
                <option>GOAT</option>
                <option>DALS</option>
                <option>TrueMark</option>
                <option>CertSig</option>
                <option>CALI_ORCHESTRATOR</option>
              </select>
            </label>
            <label>
              Action
              <input value={controlAction} onChange={(e) => setControlAction(e.target.value)} />
            </label>
            <label>
              Params (JSON)
              <textarea value={controlParams} onChange={(e) => setControlParams(e.target.value)} rows={4} />
            </label>
            <button onClick={submitControl}>Submit control packet</button>
            {controlStatus && (
              <div className="muted">
                {controlStatus.error && <span className="error">{controlStatus.error}</span>}
                {controlStatus.ok && <span>Outcome: {JSON.stringify(controlStatus.outcome)}</span>}
              </div>
            )}
          </div>
        </div>

        <div className={`panel events-panel ${density}`}>
          <div className="panel-head">
            <h3>Unified timeline</h3>
            <div className="muted">window: {windowSec}s · filtered: {filteredEvents.length} · sort: {sortMode}</div>
          </div>
          <div className="events">
            {sortedEvents.length === 0 && <div className="muted">No events in window.</div>}
            {sortedEvents.map((ev, idx) => (
              <div key={idx} className="event-row">
                <div className="event-head">
                  <span className="pill small">{ev.type || 'event'}</span>
                  <span className="muted" title={`iss: ${ev.iss || '—'} | ts: ${formatTs(ev.timestamp)}`}>
                    {ev.iss || formatTs(ev.timestamp)}
                  </span>
                </div>
                <div className="muted">actor: {ev.actor || '—'} · surface: {ev.surface || '—'} · target: {ev.target || '—'} · action: {ev.action || '—'} · via: {ev.via || '—'}</div>
                {ev.outcome && <pre className="codeblock">{JSON.stringify(ev.outcome, null, 2)}</pre>}
              </div>
            ))}
          </div>
        </div>
      </section>

      <section className="panel lanes">
        <div className="panel-head">
          <h3>Per-target lanes</h3>
          <div className="muted">visual only; no behavior</div>
        </div>
        <div className="lanes-grid">
          {coreEntries.length > 0 && (
            <div className="lane">
              <div className="lane-title">Core presence</div>
              <div className="lane-events">
                {coreEntries.map(([name, state]) => (
                  <span key={name} className={`pill small ${state?.availability?.toLowerCase() || 'unknown'}`}>{name}:{state?.availability || 'unknown'}</span>
                ))}
              </div>
            </div>
          )}
          {Object.entries(targetLanes).map(([lane, laneEvents]) => (
            <div key={lane} className="lane">
              <div className="lane-title">{lane}</div>
              <div className="lane-events">
                {laneEvents.map((ev, idx) => (
                  <span
                    key={idx}
                    className={`dot ${ev.type === 'intent_issued' ? 'intent' : 'outcome'}`}
                    title={`${ev.type || 'event'} | iss: ${ev.iss || '—'} | ts: ${formatTs(ev.timestamp)}`}
                  ></span>
                ))}
              </div>
            </div>
          ))}
          {Object.keys(targetLanes).length === 0 && <div className="muted">No events to show.</div>}
        </div>
      </section>

      <section className="panel divergence">
        <div className="panel-head">
          <h3>Divergence</h3>
          <div className={`pill ${divergence ? 'conflict' : 'available'}`}>{divergence ? 'divergence detected' : 'aligned'}</div>
        </div>
        {divergence && (
          <div className="divergence-body">
            <p className="muted">Parallel assertions (read-only):</p>
            {assertionDetails.length === 0 && <div className="muted">No assertions captured.</div>}
            {assertionDetails.map((entry) => (
              <div key={entry.name} className="event-row">
                <div className="event-head">
                  <span className="label">{entry.name}</span>
                </div>
                <pre className="codeblock">{JSON.stringify(entry.assertion, null, 2)}</pre>
              </div>
            ))}
          </div>
        )}
      </section>
    </div>
  );
};

export default ParityDashboard;