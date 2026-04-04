import { useEffect, useRef } from 'react';
import L from 'leaflet';

const ZONE_POINTS = [
  { name: 'Zone A', latlng: [17.3902, 78.503] },
  { name: 'Zone B', latlng: [17.397, 78.477] },
  { name: 'Zone C', latlng: [17.3789, 78.4878] },
  { name: 'Zone D', latlng: [17.4052, 78.4941] },
];

const THREAT_COLORS = {
  LOW: '#38d39f',
  MEDIUM: '#f5c451',
  HIGH: '#ff9a43',
  CRITICAL: '#ff5d73',
};

function MapView({ zoneThreats, activeZone, lastAlert }) {
  const mapElementRef = useRef(null);
  const mapRef = useRef(null);
  const markerRef = useRef({});

  useEffect(() => {
    if (mapRef.current || !mapElementRef.current) {
      return;
    }

    const map = L.map(mapElementRef.current, {
      center: [17.385, 78.4867],
      zoom: 13,
      zoomControl: false,
      attributionControl: false,
      scrollWheelZoom: false,
      dragging: false,
      doubleClickZoom: false,
      boxZoom: false,
      keyboard: false,
      tap: false,
    });

    mapRef.current = map;

    ZONE_POINTS.forEach((zone, index) => {
      const threat = zoneThreats[zone.name] || 'LOW';
      const marker = L.circleMarker(zone.latlng, {
        radius: 12 + index,
        color: THREAT_COLORS[threat],
        fillColor: THREAT_COLORS[threat],
        fillOpacity: 0.82,
        weight: 2,
      }).addTo(map);
      marker.bindTooltip(zone.name, { permanent: true, direction: 'top', className: 'zone-tooltip', offset: [0, -12] });
      markerRef.current[zone.name] = marker;
    });

    map.invalidateSize();
  }, [zoneThreats]);

  useEffect(() => {
    if (!mapRef.current) {
      return;
    }

    ZONE_POINTS.forEach((zone, index) => {
      const marker = markerRef.current[zone.name];
      if (!marker) {
        return;
      }

      const threat = zoneThreats[zone.name] || 'LOW';
      marker.setStyle({
        color: THREAT_COLORS[threat],
        fillColor: THREAT_COLORS[threat],
        fillOpacity: activeZone === zone.name ? 0.95 : 0.78,
        radius: activeZone === zone.name ? 16 + index : 12 + index,
      });
    });
  }, [activeZone, zoneThreats]);

  return (
    <div className="grid gap-4 xl:grid-cols-[1.35fr_0.65fr]">
      <div className="relative overflow-hidden rounded-[24px] border border-white/10 bg-slate-950/80">
        <div className="absolute left-4 top-4 z-[500] rounded-2xl border border-white/10 bg-slate-950/75 px-4 py-3 backdrop-blur-xl">
          <p className="text-xs uppercase tracking-[0.35em] text-cyan-300/80">Zone Map</p>
          <h3 className="mt-1 text-lg font-semibold text-white">Hyderabad, India</h3>
          <p className="mt-1 text-sm text-slate-400">Leaflet-driven zone visualization with offline-safe markers</p>
        </div>
        <div ref={mapElementRef} className="h-[420px] w-full" />
      </div>

      <div className="grid gap-3 rounded-[24px] border border-white/10 bg-slate-950/65 p-4">
        <div className="rounded-2xl border border-white/10 bg-white/5 p-4">
          <div className="text-xs uppercase tracking-[0.35em] text-slate-400">Active Zone</div>
          <div className="mt-2 text-2xl font-semibold text-white">{activeZone || 'Zone A'}</div>
          <div className="mt-2 text-sm text-slate-400">Current confidence flow is being mapped from the live websocket feed.</div>
        </div>

        <div className="grid gap-3 sm:grid-cols-2 xl:grid-cols-1">
          {ZONE_POINTS.map((zone) => (
            <div key={zone.name} className="rounded-2xl border border-white/10 bg-white/5 p-4">
              <div className="flex items-center justify-between gap-3">
                <div>
                  <div className="text-sm font-semibold text-white">{zone.name}</div>
                  <div className="text-xs uppercase tracking-[0.3em] text-slate-400">Threat</div>
                </div>
                <div
                  className="h-4 w-4 rounded-full"
                  style={{ backgroundColor: THREAT_COLORS[zoneThreats[zone.name] || 'LOW'] }}
                />
              </div>
              <div className="mt-3 text-2xl font-black tracking-[0.2em] text-slate-100">{zoneThreats[zone.name] || 'LOW'}</div>
            </div>
          ))}
        </div>

        <div className="rounded-2xl border border-white/10 bg-white/5 p-4 text-sm text-slate-300">
          <div className="text-xs uppercase tracking-[0.3em] text-slate-400">Latest alert</div>
          <div className="mt-2 text-white">{lastAlert ? `${lastAlert.zone} - ${lastAlert.threat_level}` : 'No dispatch yet'}</div>
          <div className="mt-1 text-slate-400">
            {lastAlert ? lastAlert.message : 'Once threat crosses HIGH, the alert engine logs and dispatches automatically.'}
          </div>
        </div>
      </div>
    </div>
  );
}

export default MapView;
