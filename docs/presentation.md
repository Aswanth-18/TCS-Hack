# AstraRoute AI — Presentation Deck
**TCS AI Engineering Hackathon 2026 · Challenge 05**  
**Team MindX**

---

## Slide 01 — Overview & Problem Statement
### AstraRoute AI: Autonomous AI FinOps & Intelligent Model Routing

> *"The cheapest model is not always right. The most powerful model is not always necessary."*

Every single AI request is a multi-dimensional trade-off:
$$\text{AI Requests} \longrightarrow \mathbf{\text{Cost} + \text{Quality} + \text{Latency} + \text{Governance}}$$

### The Four Pressing Pressures:
1. **Cost:** Unnecessary expensive inference on flagship models for routine tasks.
2. **Quality:** Cheap routing can reduce quality and cause downstream application errors.
3. **Latency:** Extra chained calls, retries, or oversized models increase response time.
4. **Governance:** Enterprise privacy, budget ceilings, and task criticality must be enforced deterministically.

---

## Slide 02 — Our Solution
### One Control Loop for Every AI Request

A closed-loop system where **every outcome informs the next decision**:

```
[01 UNDERSTAND] ──> [02 FILTER] ──> [03 ROUTE] ──> [04 EXECUTE]
       ▲                                                  │
       │                                                  ▼
  [08 ADAPT]   <── [07 MEASURE] <── [06 RECOVER] <── [05 VERIFY]
```

### Key Loop Modules:
* **01 UNDERSTAND (SLM):** Fast prompt classification and complexity detection.
* **02 FILTER (POLICY):** Hard constraints, budget ceilings, and privacy eligibility.
* **03 ROUTE (ROUTER):** Multi-objective FinOps candidate scoring (Cost vs. Quality vs. Latency).
* **04 EXECUTE:** Multi-provider abstraction with fallback support.
* **05 VERIFY (GUARDIAN):** Automated rubric evaluation and schema compliance check.
* **06 RECOVER:** Intelligent escalation path when quality thresholds fail.
* **07 MEASURE:** Exact token ledger, cost calculations, and latency logging.
* **08 ADAPT:** Continuous feedback loop converting telemetry into future routing estimates.

---

## Slide 03 — Decision Intelligence
### The Difference Happens When a Model Fails

Standard gateways fail or blindly retry. AstraRoute AI applies **Economic Recovery**:

```
[REQUEST] ──> [SLM] ──> [POLICY] ──> [ROUTER] ──> [MODEL] ──> [QUALITY CHECK]
                                                                     │
                                         ┌───────────────────────────┴───────────────────────────┐
                                         ▼                                                       ▼
                                     [PASS]                                                   [FAIL]
                                    Response                                                 Recovery
                                                                                                 │
                                                                                     [Is escalation worthwhile?]
                                                                                      │                       │
                                                                                 (YES)│                   (NO)│
                                                                                      ▼                       ▼
                                                                                 [NEXT MODEL]           [SAFE FAILURE]
                                                                                      │
                                                                                   [VERIFY]
```

### Concrete Production Example:
* **Target Required Quality:** `85%`
* **Medium Economy Model Output:** `62%` $\longrightarrow$ **FAIL**
* **Autonomous Recovery Evaluation:** Checks eligible model, remaining request budget, latency budget, task criticality, and expected quality gain.
* **Escalation Result:** Dispatches to Advanced Tier Model $\longrightarrow$ `93%` **PASS**.
* **Rule:** *Escalation is triggered only when expected improvement mathematically justifies additional cost and latency.*

---

## Slide 04 — System Architecture
### Inside AstraRoute AI

| Layer | Functional Components |
| :--- | :--- |
| **REQUEST** | API Gateway $\longrightarrow$ Request Analyzer $\longrightarrow$ SLM Pre-Router |
| **DECISION** | Policy & Eligibility $\longrightarrow$ Model Registry $\longrightarrow$ Intelligent Router |
| **EXECUTION** | Small / Medium / Advanced Tier Models $\longrightarrow$ Provider Abstraction $\longrightarrow$ Live APIs / Simulator |
| **VERIFY & RECOVER** | Quality Guardian $\longrightarrow$ Recovery Engine $\longrightarrow$ Re-verify $\longrightarrow$ Safe Failure |
| **OBSERVABILITY & FINOPS** | Request Traces $\cdot$ Cost Ledger $\cdot$ Historical Telemetry $\cdot$ Routing Arena $\cdot$ Policy Simulator |

### Technology Stack:
* **Frontend:** React, Tailwind CSS, Lucide Icons, Vite
* **Backend:** FastAPI, Python, Pydantic v2, Uvicorn
* **Database:** SQLite / PostgreSQL / Supabase, SQLAlchemy ORM
* **Intelligence:** SLM Pre-routing, LLM APIs (OpenAI, Anthropic, Gemini, Groq), Pandas
* **Deployment:** Docker ready, Multi-Platform support

---

## Slide 05 — Novelty, Differentiation & TCS Alignment
### From AI Cost Management to Closed-Loop AI Control

```
Industry Segments:               AstraRoute Connects Them:
──────────────────               ─────────────────────────
• FinOps (Cost / Budgets)   ──┐  • Policy   ──> Quality-aware FinOps
• AI Gateways (Routing)     ──┼─ • Route    ──> Economic recovery
• Observability (Latency)   ──┼─ • Execute  ──> Cost Per Successful Outcome (CPSO)
• Model Eval (Quality)      ──┘  • Verify / Recover / Measure / Adapt ──> Evidence-driven adaptation
```

### Alignment with TCS AI Engineering Framework:
1. **REASON:** Understand prompt intent, token payload, and criticality.
2. **PLAN:** Select mathematically optimal routing strategy and eligible candidates.
3. **ACT:** Execute through multi-provider abstraction layer.
4. **VERIFY:** Validate outcome schema, completeness, and quality score.
5. **ADAPT:** Learn continuously from persisted telemetry to optimize future routes.

> *"We don’t claim to invent the individual capabilities. We connect them into a request-level closed loop where AI economics directly influence execution decisions."*  
> **AstraRoute AI — Optimize the cost of achieving a verified AI outcome.**
