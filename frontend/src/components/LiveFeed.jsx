const cameraLabel = (cameraId) => `Camera ${cameraId || '0'}`;

function LiveFeed({ feed }) {
  const hasFrame = Boolean(feed.frame_base64);
  const frameSrc = hasFrame ? `data:image/jpeg;base64,${feed.frame_base64}` : '';

  return (
    <section className="group relative h-full overflow-hidden rounded-[28px] border border-white/10 bg-[var(--panel)] shadow-glow backdrop-blur-xl">
      <div className="flex items-center justify-between border-b border-white/10 px-5 py-4">
        <div>
          <p className="text-xs font-semibold uppercase tracking-[0.35em] text-cyan-300/80">Live Feed</p>
          <h2 className="mt-1 text-xl font-semibold text-white">Annotated crowd stream</h2>
        </div>
        <div className="rounded-full border border-white/10 bg-slate-950/60 px-3 py-1 text-xs text-slate-300">
          {cameraLabel(feed.camera_id)}
        </div>
      </div>

      <div className="relative aspect-[16/10] min-h-[420px] overflow-hidden bg-slate-950">
        {hasFrame ? (
          <img src={frameSrc} alt="Live crowd feed" className="h-full w-full object-cover" />
        ) : (
          <div className="flex h-full items-center justify-center">
            <div className="max-w-md rounded-3xl border border-white/10 bg-white/5 px-8 py-10 text-center backdrop-blur-xl">
              <div className="mx-auto mb-4 h-14 w-14 rounded-2xl border border-cyan-300/30 bg-cyan-300/10" />
              <h3 className="text-lg font-semibold text-white">Waiting for stream</h3>
              <p className="mt-2 text-sm text-slate-400">The backend will switch to simulation mode automatically if a webcam is not available.</p>
            </div>
          </div>
        )}

        <div className="pointer-events-none absolute inset-0 bg-gradient-to-t from-slate-950/55 via-transparent to-transparent" />
        <div className="absolute left-4 top-4 rounded-2xl border border-white/10 bg-slate-950/70 px-4 py-3 backdrop-blur-xl">
          <div className="text-xs uppercase tracking-[0.3em] text-slate-400">People detected</div>
          <div className="mt-1 text-2xl font-semibold text-white">{feed.person_count}</div>
        </div>
        <div className="absolute right-4 top-4 grid gap-2 rounded-2xl border border-white/10 bg-slate-950/70 px-4 py-3 text-right backdrop-blur-xl">
          <div>
            <span className="text-xs uppercase tracking-[0.3em] text-slate-400">FPS</span>
            <span className="ml-3 text-lg font-semibold text-white">{feed.fps?.toFixed?.(1) || feed.fps || 0}</span>
          </div>
          <div>
            <span className="text-xs uppercase tracking-[0.3em] text-slate-400">Zone</span>
            <span className="ml-3 text-lg font-semibold text-cyan-300">{feed.zone || 'Zone A'}</span>
          </div>
        </div>
      </div>
    </section>
  );
}

export default LiveFeed;
