export function formatForPrometheus(evt) {
  if (!evt || evt.ok !== true) throw new Error("Telemetry: invalid event");
  return {
    measurements: {
      stage: evt.stage,
      timestamp: Date.now()
    }
  };
}

export function logTelemetry(evt) {
  const payload = formatForPrometheus(evt);
  // send to your sink (Prom, OTLP, file, etc.)
  return payload;
}
