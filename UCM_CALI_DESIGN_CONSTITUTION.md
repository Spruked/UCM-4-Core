# UCM + CALI — Unified Decision Flow Design Constitution
## Contract: UCM_CALI_UNIFIED_v1.0
## Status: FROZEN_IMMUTABLE
## Effective Date: January 9, 2026

---

## I. Foundational Principle (Locked)

All four cores are **peers**. They receive the same input, apply the same philosophical seed vault, and independently arrive at a conclusion using architecturally different reasoning paths.

**No core:**
- specializes in a "task"
- outranks another
- serves as a validator or judge of the others

**CALI does not decide.**  
**The +1 does not decide.**  
**Decision emerges from structured convergence.**

---

## II. Input Distribution (Single Source of Truth)

### 1️⃣ Input Processor
Raw input enters the system **once**  
Normalized, schema-validated, time-stamped  
Broadcast **unchanged** to all four cores  

**Input → Canonical Form → Fan-out to 4 cores**

**Guarantees:**
- identical evidence
- no contextual bias
- no sequencing advantage

---

## III. Independent Core Reasoning (Parallel Sovereignty)

Each core executes the **full reasoning problem end-to-end**.

### 🔹 Core Characteristics (All Four)
- Same philosopher set
- Same master seed vault
- Same invariants
- Same ethical constraints

### 🔹 What differs
- Internal architecture
- Traversal geometry
- Memory handling
- Synthesis mechanics

### 🔹 Output from each core
Each core returns a **complete verdict**, not a partial one:
```json
{
  "status": "ACCEPT | REJECT | CONDITIONAL | REINTERPRETED | SUSPEND",
  "confidence": 0.0–1.0,
  "internal_consistency": 0.0–1.0,
  "coverage": 0.0–1.0,
  "reasoning_path": [...],
  "constraints_triggered": [...],
  "notes": "core-specific insight"
}
```

**No core sees another's result at this stage.**

---

## IV. Convergence Observation Layer (+1 Softmax SKG)

### Purpose (Strictly Limited)
The +1 exists to **observe**, not rule.  
It answers:
- Do the independent systems converge?
- Is divergence meaningful or faulty?
- Is the outcome epistemically inevitable?

It **never** answers:
- Which core is correct?

### 2️⃣ Softmax SKG Processing

#### Inputs
- Four completed verdicts
- **No mutation, no feedback injection**

#### Evaluations performed
- Internal consistency scoring
- Seed-vault coverage assessment
- Confidence stability analysis
- Cross-verdict agreement patterns
- Byzantine fault detection (**flag only**)
- Epistemic inevitability detection

#### Normalization
Softmax converts weighted assessments into a probability field, **not a vote**.  
**Verdicts → Raw Scores → Softmax → Distribution**

#### Produces
- Relative alignment
- Outlier visibility
- Reliability tier
- Inevitability signal

#### Output of the +1 (Advisory Only)
```json
{
  "verdict_probabilities": {...},
  "byzantine_flags": [...],
  "epistemic_inevitability": 0.00–1.00,
  "reliability_tier": "A|B|C|D",
  "advisory_message": "human-readable synthesis"
}
```

**No verdict is removed.**  
**No verdict is altered.**

---

## V. CALI Synthesis (Supervisory, Not Cognitive)

CALI's role is **coordination and state**, not reasoning.

### 3️⃣ CALI Aggregation
CALI receives:
- 4 sovereign verdicts
- +1 advisory report

CALI:
- checks system health
- enforces invariants
- packages outputs coherently
- determines escalation policy

---

## VI. Final Outcome Determination (Emergent, Not Assigned)

The system outcome is determined by **structured rules**, not authority.

### Possible Outcomes

| Condition | Result |
|-----------|--------|
| High convergence + high inevitability | ACCEPT |
| Convergence with bounded caveats | CONDITIONAL |
| High confidence + philosophical divergence | REINTERPRETED |
| Strong disagreement or fault flags | SUSPEND |
| Explicit constraint violation | REJECT |

**This is not chosen by a component.**  
**It emerges from the combined state.**

---

## VII. Human Escalation (When Required)

Human review occurs **only** when:
- epistemic ambiguity remains
- inevitability < threshold
- faults undermine confidence

**Human input is logged as external, never injected as truth.**

---

## VIII. Final Output (Immutable, Auditable)

```json
{
  "final_status": "...",
  "core_verdicts": {...},
  "softmax_advisory": {...},
  "system_confidence": 0.00–1.00,
  "inevitability_score": 0.00–1.00,
  "audit_signature": "hash"
}
```

**Every decision is:**
- reproducible
- traceable
- cryptographically anchored

---

## IX. One-Sentence Canonical Summary (Lock This)

**The system does not decide because a core is right; it decides because independent reasoning collapses uncertainty under shared truth constraints, with the +1 revealing—not enforcing—inevitability.**

---

## X. Implementation Invariants (Enforced)

### Core Sovereignty Invariants
1. **Input Parity**: All cores receive identical canonical input
2. **Execution Isolation**: No core may inspect another's intermediate state
3. **Output Completeness**: Each core produces full verdict or fails entirely
4. **No Feedback Loops**: Advisory layer never modifies core inputs/outputs

### Convergence Layer Invariants
1. **Advisory Only**: +1 layer provides observation, never decision
2. **No Verdict Removal**: All core verdicts preserved in final output
3. **Probability Normalization**: Softmax outputs sum to 1.0 ± 1e-6
4. **Fault Flagging Only**: Byzantine detection marks, never excludes

### CALI Coordination Invariants
1. **State Only**: CALI maintains system state, never cognitive processing
2. **Invariant Enforcement**: Runtime validation of all architectural rules
3. **Escalation Logic**: Human review triggered by quantitative thresholds only
4. **Output Immutability**: Final verdict cryptographically signed and timestamped

### Decision Emergence Invariants
1. **Rule-Based Only**: Outcomes determined by explicit threshold logic
2. **No Authority Assignment**: No component may override emergent decision
3. **Audit Completeness**: All reasoning paths preserved for forensic analysis
4. **Temporal Consistency**: Decision logic deterministic for identical inputs

---

## XI. Semantic Clarity Invariants (Preventing Misinterpretation)

### Naming Conventions
1. **"Tribunal" Refers to Synthesis**: Classes named "TribunalSynthesizer" perform convergence detection and narrative synthesis, not judicial authority
2. **"Dominance" Means Explanatory Strength**: Axis dominance identifies strongest explanatory frameworks along dimensions, not hierarchical winners
3. **"Decision" Means State Assessment**: ECMRuntime.decide() assesses whether consensus exists, not what the final verdict should be

### Documentation Requirements
1. **Architectural Comments**: All classes must include invariant documentation explaining what they do and do not do
2. **Authority Disclaimers**: Any term that could imply hierarchy must be accompanied by explicit disclaimers
3. **Emergence Emphasis**: Code must clearly document that final outcomes emerge from rules, not authority

### Code Review Requirements
1. **Semantic Audit**: Code reviews must verify that naming and comments prevent hierarchical misinterpretation
2. **Invariant Validation**: All changes must pass architectural invariant tests
3. **Constitution Compliance**: Changes must maintain alignment with this frozen constitution

---

## XII. Breach Protocol

Any violation of these invariants constitutes an **architectural breach** requiring:
1. **Immediate System Halt**: All processing suspended
2. **Forensic Analysis**: Complete state dump and invariant validation
3. **Root Cause Resolution**: Code changes to restore architectural integrity
4. **Regression Testing**: Validation that breach cannot recur

**No production deployment permitted with active invariant violations.**

---

## XII. Evolution Protocol

This constitution may only be amended by:
1. **Unanimous Core Consensus**: All four cores demonstrate invariant-preserving evolution
2. **Invariant Validation**: New design passes all existing invariant tests
3. **Backward Compatibility**: Existing decisions remain reproducible
4. **Audit Trail**: Complete documentation of changes and rationale

**This constitution supersedes all prior architectural decisions.**

---

*This design constitution is cryptographically anchored and serves as the immutable foundation for UCM+CALI unified decision flow. Any code changes must validate against these principles.*