// To Prometheus/Grafana
const fs = require('fs');

function formatForPrometheus(metrics) {
  if (!metrics || metrics.ok !== true) throw new Error('Telemetry: invalid event');
  return {
    measurements: {
      stage: metrics.stage,
      timestamp: Date.now()
    }
  };
}

function exportTelemetry(data) {
  const payload = formatForPrometheus(data);
  fs.writeFileSync('telemetry_export.json', JSON.stringify(payload));
  console.log('Telemetry exported');
  return payload;
}

module.exports = { exportTelemetry, formatForPrometheus };