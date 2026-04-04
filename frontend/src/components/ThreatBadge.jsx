const threatStyles = {
  LOW: {
    label: 'LOW',
    wrap: 'from-emerald-400/20 via-emerald-500/10 to-transparent text-emerald-200',
    accent: 'bg-emerald-400',
    border: 'border-emerald-400/30',
  },
  MEDIUM: {
    label: 'MEDIUM',
    wrap: 'from-amber-400/20 via-amber-500/10 to-transparent text-amber-100',
    accent: 'bg-amber-400',
    border: 'border-amber-400/30',
  },
  HIGH: {
    label: 'HIGH',
    wrap: 'from-orange-400/20 via-orange-500/10 to-transparent text-orange-100',
    accent: 'bg-orange-400',
    border: 'border-orange-400/30',
  },
  CRITICAL: {
    label: 'CRITICAL',
    wrap: 'from-rose-500/30 via-red-500/15 to-transparent text-rose-100',
    accent: 'bg-rose-500',
    border: 'border-rose-500/40 alert-pulse',
  },
};

function ThreatBadge({ threatLevel, confidence, behaviors = [] }) {
  const token = threatStyles[threatLevel] || threatStyles.LOW;

  return (
    <section className={`rounded-[28px] border ${token.border} bg-[var(--panel)] p-5 shadow-glow backdrop-blur-xl`}>
      <div className={`rounded-[24px] bg-gradient-to-br ${token.wrap} p-5`}>
        <div className="flex items-start justify-between gap-4">
          <div>
            <p className="text-xs font-semibold uppercase tracking-[0.35em] text-slate-400">Threat Level</p>
            <h2 className="mt-2 text-4xl font-black tracking-[0.15em] text-white">{token.label}</h2>
          </div>
          <div className={`h-4 w-4 rounded-full ${token.accent} ${threatLevel === 'CRITICAL' ? 'alert-pulse' : ''}`} />
        </div>

        <div className="mt-5 flex items-end justify-between gap-4">
          <div>
            <div className="text-sm uppercase tracking-[0.3em] text-slate-400">Confidence</div>
            <div className="mt-1 text-3xl font-semibold text-white">{Math.round((confidence || 0) * 100)}%</div>
          </div>
          <div className="rounded-2xl border border-white/10 bg-slate-950/60 px-4 py-2 text-sm text-slate-300">
            {behaviors.length ? behaviors.slice(0, 3).join(' · ') : 'No critical behavior detected'}
          </div>
        </div>
      </div>
    </section>
  );
}

export default ThreatBadge;
