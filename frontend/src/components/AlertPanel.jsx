function formatTime(timestamp) {
  if (!timestamp) {
    return '--:--:--';
  }
  return new Date(timestamp).toLocaleTimeString([], {
    hour: '2-digit',
    minute: '2-digit',
    second: '2-digit',
  });
}

function AlertPanel({ alerts, onAcknowledge }) {
  return (
    <section className="flex min-h-[320px] flex-1 flex-col overflow-hidden rounded-[28px] border border-white/10 bg-[var(--panel)] shadow-glow backdrop-blur-xl">
      <div className="border-b border-white/10 px-5 py-4">
        <p className="text-xs font-semibold uppercase tracking-[0.35em] text-orange-300/90">Alert Feed</p>
        <h2 className="mt-1 text-xl font-semibold text-white">Recent dispatch history</h2>
      </div>

      <div className="flex-1 space-y-3 overflow-y-auto px-4 py-4">
        {alerts.length === 0 ? (
          <div className="rounded-2xl border border-dashed border-white/10 bg-white/5 px-4 py-10 text-center text-sm text-slate-400">
            No alerts yet. The feed will populate automatically when the threat level crosses HIGH.
          </div>
        ) : (
          alerts.map((alert) => (
            <article
              key={alert.id}
              className={`rounded-2xl border px-4 py-3 transition ${alert.acknowledged ? 'border-emerald-400/20 bg-emerald-400/5' : 'border-white/10 bg-slate-950/60 hover:border-orange-300/30'}`}
            >
              <div className="flex items-start justify-between gap-3">
                <div>
                  <div className="flex flex-wrap items-center gap-2 text-sm text-slate-300">
                    <span className="font-semibold text-white">{formatTime(alert.timestamp)}</span>
                    <span className="rounded-full border border-white/10 px-2 py-0.5 text-xs">{alert.zone}</span>
                    <span className={`rounded-full px-2 py-0.5 text-xs font-semibold ${alert.threat_level === 'CRITICAL' ? 'bg-rose-500/20 text-rose-200' : 'bg-orange-500/20 text-orange-200'}`}>
                      {alert.threat_level}
                    </span>
                  </div>
                  <div className="mt-2 text-sm text-slate-300">
                    <span className="font-semibold text-white">{alert.person_count}</span> people, density {Number(alert.density).toFixed(2)} / m²
                  </div>
                  <div className="mt-2 text-xs uppercase tracking-[0.22em] text-slate-400">
                    {Array.isArray(alert.behaviors) && alert.behaviors.length ? alert.behaviors.join(' · ') : 'No flagged behavior'}
                  </div>
                </div>

                <div className="flex shrink-0 flex-col items-end gap-2">
                  <span className={`rounded-full px-2 py-1 text-[11px] font-semibold ${alert.acknowledged ? 'bg-emerald-400/20 text-emerald-200' : 'bg-amber-400/20 text-amber-100'}`}>
                    {alert.acknowledged ? 'ACKED' : 'NEW'}
                  </span>
                  <button
                    type="button"
                    onClick={() => onAcknowledge(alert.id)}
                    disabled={alert.acknowledged}
                    className="rounded-full border border-white/10 bg-white/5 px-3 py-1 text-xs font-semibold text-white transition hover:bg-white/10 disabled:cursor-not-allowed disabled:opacity-40"
                  >
                    Acknowledge
                  </button>
                </div>
              </div>
            </article>
          ))
        )}
      </div>
    </section>
  );
}

export default AlertPanel;
