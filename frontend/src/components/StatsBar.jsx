const statCard = (label, value, tone = 'text-white') => (
  <div className="rounded-2xl border border-white/10 bg-white/5 p-4 shadow-lg shadow-black/10">
    <div className="text-xs uppercase tracking-[0.3em] text-slate-400">{label}</div>
    <div className={`mt-2 text-2xl font-semibold ${tone}`}>{value}</div>
  </div>
);

function StatsBar({ people, density, activeAlerts, uptime, fps, zone }) {
  return (
    <section className="rounded-[28px] border border-white/10 bg-[var(--panel)] p-5 shadow-glow backdrop-blur-xl">
      <div className="mb-4 flex items-center justify-between">
        <div>
          <p className="text-xs font-semibold uppercase tracking-[0.35em] text-cyan-300/80">System Stats</p>
          <h2 className="mt-1 text-xl font-semibold text-white">Live operational metrics</h2>
        </div>
        <div className="rounded-full border border-white/10 bg-slate-950/70 px-3 py-1 text-xs text-slate-300">{zone || 'Zone A'}</div>
      </div>

      <div className="grid gap-3 sm:grid-cols-2 xl:grid-cols-4">
        {statCard('People', people, 'text-cyan-200')}
        {statCard('Density', `${density?.toFixed?.(2) || density || 0} / m²`, 'text-amber-200')}
        {statCard('Active Alerts', activeAlerts, 'text-rose-200')}
        {statCard('Uptime', uptime, 'text-emerald-200')}
      </div>

      <div className="mt-4 rounded-2xl border border-white/10 bg-slate-950/60 px-4 py-3 text-sm text-slate-300">
        Stream FPS: <span className="font-semibold text-white">{fps?.toFixed?.(1) || fps || 0}</span>
      </div>
    </section>
  );
}

export default StatsBar;
