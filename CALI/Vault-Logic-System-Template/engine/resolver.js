import { applyVaults } from "./vaults.js";
import { queryMatrix } from "./matrix.js";
import { logTelemetry } from "./telemetry.js";
import { generateTrace } from "./trace.js";

export async function resolve(input) {
  if (!input || !input.context || !input.embedding) {
    throw new Error("Resolver: invalid input");
  }
  const applied = await applyVaults(input);
  const results = await queryMatrix(input.embedding);
  logTelemetry({ stage: "resolver", ok: true });
  return generateTrace(applied, results);
}