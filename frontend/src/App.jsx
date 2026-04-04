import { useEffect, useMemo, useRef, useState } from 'react';
import LiveFeed from './components/LiveFeed';
import ThreatBadge from './components/ThreatBadge';
import AlertPanel from './components/AlertPanel';
import MapView from './components/MapView';
import StatsBar from './components/StatsBar';

const BACKEND_BASE = (import.meta.env.VITE_BACKEND_URL || '').trim().replace(/\/$/, '');
const API_PREFIX = BACKEND_BASE ? `${BACKEND_BASE}/api` : '/api';
const WS_URL = BACKEND_BASE
  ? `${BACKEND_BASE.replace(/^http/, 'ws')}/ws/feed`
  : `${window.location.protocol === 'https:' ? 'wss' : 'ws'}://${window.location.host}/ws/feed`;
const THREAT_ORDER = ['LOW', 'MEDIUM', 'HIGH', 'CRITICAL'];
const ZONES = ['Zone A', 'Zone B', 'Zone C', 'Zone D'];

const defaultFeed = {
  timestamp: null,
  person_count: 0,
  density: 0,
  threat_level: 'LOW',
  confidence: 0,
  behaviors: [],
  frame_base64: '',
  zone: 'Zone A',
  camera_id: '0',
  fps: 0,
  active_alerts: 0,
};

const initialZoneThreats = ZONES.reduce((accumulator, zone) => {
  accumulator[zone] = 'LOW';
  return accumulator;
}, {});

function shiftThreat(threat, offset) {
  const index = Math.max(0, THREAT_ORDER.indexOf(threat));
  return THREAT_ORDER[Math.min(THREAT_ORDER.length - 1, Math.max(0, index - offset))];
}

function App() {
  const [feed, setFeed] = useState(defaultFeed);
  const [alerts, setAlerts] = useState([]);
  const [status, setStatus] = useState({ healthy: false, uptime_seconds: 0, active_alerts: 0 });
  const [lastAlert, setLastAlert] = useState(null);
  const [zoneThreats, setZoneThreats] = useState(initialZoneThreats);
  const [connected, setConnected] = useState(false);
  const reconnectTimer = useRef(null);
  const alertPollTimer = useRef(null);

  const uptimeLabel = useMemo(() => {
    const totalSeconds = status.uptime_seconds || 0;
    const hours = Math.floor(totalSeconds / 3600);
    const minutes = Math.floor((totalSeconds % 3600) / 60);
    const seconds = totalSeconds % 60;
    return `${String(hours).padStart(2, '0')}:${String(minutes).padStart(2, '0')}:${String(seconds).padStart(2, '0')}`;
  }, [status.uptime_seconds]);

  useEffect(() => {
    let cancelled = false;

    const fetchStatus = async () => {
      try {
        const response = await fetch(`${API_PREFIX}/status`);
        const data = await response.json();
        if (!cancelled) {
          setStatus(data);
        }
      } catch {
        if (!cancelled) {
          setStatus((current) => ({ ...current, healthy: false }));
        }
      }
    };

    const fetchAlerts = async () => {
      try {
        const response = await fetch(`${API_PREFIX}/alerts?limit=20`);
        const data = await response.json();
        if (!cancelled) {
          setAlerts(data);
          setStatus((current) => ({ ...current, active_alerts: data.filter((alert) => !alert.acknowledged).length }));
        }
      } catch {
        if (!cancelled) {
          setAlerts([]);
        }
      }
    };

    const fetchLastAlert = async () => {
      try {
        const response = await fetch(`${API_PREFIX}/last-alert`);
        const data = await response.json();
        if (!cancelled) {
          setLastAlert(data.alert);
        }
      } catch {
        if (!cancelled) {
          setLastAlert(null);
        }
      }
    };

    const connectWebSocket = () => {
      const socket = new WebSocket(WS_URL);

      socket.onopen = () => {
        if (!cancelled) {
          setConnected(true);
        }
      };

      socket.onmessage = (event) => {
        const data = JSON.parse(event.data);
        if (cancelled) {
          return;
        }

        setFeed(data);
        setLastAlert(data.last_alert || null);
        setStatus((current) => ({
          ...current,
          active_alerts: typeof data.active_alerts === 'number' ? data.active_alerts : current.active_alerts,
          healthy: true,
        }));

        const activeZoneIndex = Math.max(0, ZONES.indexOf(data.zone));
        const nextZoneThreats = ZONES.reduce((accumulator, zone, index) => {
          const distance = Math.abs(index - activeZoneIndex);
          accumulator[zone] = index === activeZoneIndex ? data.threat_level : shiftThreat(data.threat_level, distance + 1);
          return accumulator;
        }, {});
        setZoneThreats(nextZoneThreats);
      };

      socket.onerror = () => {
        if (!cancelled) {
          setConnected(false);
        }
      };

      socket.onclose = () => {
        if (!cancelled) {
          setConnected(false);
          reconnectTimer.current = window.setTimeout(connectWebSocket, 1500);
        }
      };

      return socket;
    };

    fetchStatus();
    fetchAlerts();
    fetchLastAlert();
    const socket = connectWebSocket();
    alertPollTimer.current = window.setInterval(fetchAlerts, 5000);
    const statusTimer = window.setInterval(fetchStatus, 5000);

    return () => {
      cancelled = true;
      socket.close();
      window.clearInterval(alertPollTimer.current);
      window.clearInterval(statusTimer);
      window.clearTimeout(reconnectTimer.current);
    };
  }, []);

  const handleAcknowledge = async (alertId) => {
    await fetch(`${API_PREFIX}/alerts/acknowledge/${alertId}`, { method: 'POST' });
    const response = await fetch(`${API_PREFIX}/alerts?limit=20`);
    const data = await response.json();
    setAlerts(data);
    setStatus((current) => ({ ...current, active_alerts: data.filter((alert) => !alert.acknowledged).length }));
  };

  return (
    <main className="relative min-h-screen overflow-hidden px-4 py-4 text-slate-100 sm:px-6 lg:px-8">
      <div className="pointer-events-none absolute inset-0 opacity-60">
        <div className="absolute left-0 top-0 h-72 w-72 rounded-full bg-cyan-400/10 blur-3xl animate-drift" />
        <div className="absolute right-10 top-16 h-96 w-96 rounded-full bg-orange-500/10 blur-3xl animate-drift" />
        <div className="absolute bottom-0 left-1/2 h-80 w-80 -translate-x-1/2 rounded-full bg-sky-500/10 blur-3xl" />
      </div>

      <div className="relative mx-auto flex min-h-[calc(100vh-2rem)] max-w-[1600px] flex-col gap-4">
        <header className="flex items-center justify-between rounded-3xl border border-white/10 bg-white/5 px-5 py-4 shadow-glow backdrop-blur-xl">
          <div>
            <div className="flex items-center gap-3">
              <div className="flex h-11 w-11 items-center justify-center rounded-2xl bg-gradient-to-br from-cyan-300 to-emerald-500 text-slate-950 shadow-lg shadow-cyan-500/25">
                <span className="text-sm font-black tracking-widest">CS</span>
              </div>
              <div>
                <h1 className="text-2xl font-semibold tracking-tight text-white sm:text-3xl">CrowdShield AI</h1>
                <p className="text-sm text-slate-400">Real-time panic detection and emergency dispatch console</p>
              </div>
            </div>
          </div>
          <div className="flex items-center gap-3 rounded-full border border-white/10 bg-slate-950/60 px-4 py-2 text-sm text-slate-200">
            <span className={`h-3 w-3 rounded-full ${connected && status.healthy ? 'bg-emerald-400 shadow-[0_0_18px_rgba(52,211,153,0.8)]' : 'bg-rose-500 shadow-[0_0_18px_rgba(248,113,113,0.6)]'}`} />
            <span>{connected && status.healthy ? 'System Online' : 'Reconnecting'}</span>
          </div>
        </header>

        <section className="grid flex-1 gap-4 xl:grid-cols-12">
          <div className="xl:col-span-7">
            <LiveFeed feed={feed} />
          </div>
          <div className="flex flex-col gap-4 xl:col-span-5">
            <ThreatBadge threatLevel={feed.threat_level} confidence={feed.confidence} behaviors={feed.behaviors} />
            <StatsBar
              people={feed.person_count}
              density={feed.density}
              activeAlerts={status.active_alerts || feed.active_alerts || 0}
              uptime={uptimeLabel}
              fps={feed.fps}
              zone={feed.zone}
            />
            <AlertPanel alerts={alerts} onAcknowledge={handleAcknowledge} />
          </div>
        </section>

        <section className="rounded-[28px] border border-white/10 bg-[var(--panel)] p-4 shadow-glow backdrop-blur-xl">
          <MapView zoneThreats={zoneThreats} activeZone={feed.zone} lastAlert={lastAlert} />
        </section>
      </div>
    </main>
  );
}

export default App;
