# AstraRoute AI — Autonomous AI FinOps & Intelligent Model Routing

**TCS AI Hackathon — Challenge 05: Autonomous AI FinOps & Intelligent Model Routing**  
**Domain:** AI Economics / FinOps  
**Team / Implementation:** Senior Full-Stack & AI Systems Architecture

---

## 1. Executive Summary

AstraRoute AI is an enterprise-grade autonomous AI gateway that chooses the **lowest-cost eligible AI model capable of satisfying required quality, privacy, latency, reliability, and business constraints**.

Traditional routers often prioritize the cheapest model indiscriminately, resulting in high failure rates on complex tasks and escalating developer remediation costs. AstraRoute AI solves this using an autonomous feedback loop:

$$\text{UNDERSTAND} \longrightarrow \text{DECIDE} \longrightarrow \text{ACT} \longrightarrow \text{VERIFY} \longrightarrow \text{RECOVER} \longrightarrow \text{LEARN} \longrightarrow \text{OPTIMIZE}$$

AstraRoute introduces **Cost Per Successful Outcome (CPSO)** as the primary economic benchmark in generative AI:

$$\text{CPSO} = \frac{\sum \text{Total Cost of All Execution Attempts within Scope}}{\text{Number of Verified Correct Outcomes}}$$

---

## 2. Architecture & Core Modules

```mermaid
flowchart TD
    UserReq[User Request & Constraints] --> Analyzer[Module 1: Request & Policy Analyzer]
    Analyzer --> Filter[Module 2: Eligibility & Privacy Filter]
    Filter --> HardFilterCheck{Hard Constraints Met?}
    HardFilterCheck -- No --> RejectAudit[Honest Policy Rejection & Reason]
    HardFilterCheck -- Yes --> Router[Module 3: Intelligent Model Router]
    Router --> ProviderFactory[Module 4: Provider Adapter Factory]
    ProviderFactory --> ModelExec[API Execution: OpenAI / Anthropic / Gemini / Groq / Simulator]
    ModelExec --> Guardian[Module 5: Quality Guardian]
    Guardian --> VerifiedCheck{Verified Pass?}
    VerifiedCheck -- Yes --> FinOps[Module 7: FinOps Telemetry & CPSO]
    VerifiedCheck -- No --> Fallback[Module 6: Bounded Fallback & Escalation]
    Fallback -- Within Budget/Retries --> Router
    Fallback -- Exhausted --> FailureReport[Terminal Failure with Audit Costs]
    FinOps --> Adaptation[Module 10: Adaptive Learning Feedback]
    FinOps --> Recommender[Module 11: Autonomous Recommendations]
    FinOps --> Arena[Module 8: Live Routing Arena]
```

### Module Breakdown:
1. **Module 1 — Request & Policy Analyzer:** Classifies prompt task types (`coding`, `reasoning`, `summarization`, `data_analysis`, `structured_output`, `general_qa`), estimates tokens, evaluates data sensitivity (`public`, `internal`, `confidential`, `restricted`), and sets budget caps.
2. **Module 2 — Eligibility & Privacy Filter:** Strictly excludes non-qualifying models before ranking (e.g. models without zero-data retention on restricted data, offline providers, budget overruns, latency violations).
3. **Module 3 — Intelligent Model Router:** Multi-objective scoring engine balancing Cost, Quality, Latency, and Reliability across 4 benchmarkable strategies.
4. **Module 4 — Model Execution & Telemetry:** Unified provider adapter interface with live API support (OpenAI, Anthropic, Gemini, Groq) and an integrated high-fidelity Simulator.
5. **Module 5 — Quality Guardian:** Task-aware deterministic verification (Python AST syntax parsing, JSON schema validation, quantitative consistency checks, summarization & reasoning rubrics).
6. **Module 6 — Automatic Fallback & Recovery:** Bounded recovery engine catching timeouts and verification failures with max retry limits, remaining budget checks, and candidate escalation.
7. **Module 7 — FinOps Analytics & CPSO:** Comprehensive inference accounting tracking total spend, spend by provider/model/task, and CPSO.
8. **Module 8 — Live Routing Arena:** Side-by-side benchmark executing 4 strategies (*Always Advanced*, *Cheapest Eligible*, *Rule-Based*, *AstraRoute Intelligent*) on identical workloads with CSV export.
9. **Module 9 — What-If Policy Simulator:** Interactive policy sandbox with sliders to project spend, quality trade-offs, and traffic distribution before applying changes.
10. **Module 10 — Adaptive Learning:** Bayesian-smoothed empirical performance tracking with sample thresholds and instant rollback controls.
11. **Module 11 — Autonomous FinOps Recommendations:** Proactive opportunity detector highlighting downgrade candidates, caching opportunities, and budget alerts with 1-click apply.
12. **Module 12 — Explainable Decisions & Audit Trail:** Full end-to-end traceable audit log recording constraint evaluations, candidate scores, and recovery attempts.

---

## 3. Technology Stack

- **Frontend:** React 18, Vite, TypeScript, Tailwind CSS, Lucide React, Recharts, React Router v6.
- **Backend:** Python 3.13, FastAPI, Pydantic v2, SQLAlchemy 2.0, HTTPX, Pytest.
- **Database:** Supabase PostgreSQL compatible schema with local zero-configuration SQLite fallback.
- **Design:** Academic Portal Light Theme with sage & forest-green palette, soft borders, rounded cards, and subtle shadows.

---

## 4. Getting Started & Installation

### Prerequisites
- Python 3.10+ (Tested on Python 3.13)
- Node.js v18+ (Tested on Node.js v22)
- npm or pnpm

### Quick Start (Zero-Configuration Local Run)

#### Step 1: Clone and Setup Backend
```bash
# Navigate to project directory
cd TCS-Hack

# Create Python virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
.\venv\Scripts\Activate.ps1
# macOS/Linux:
source venv/bin/activate

# Install backend dependencies
pip install -r backend/requirements.txt
```

#### Step 2: Setup Frontend
```bash
cd frontend
npm install
npm run build
cd ..
```

#### Step 3: Launch Full-Stack Application
```bash
# Launch unified server (serves React frontend & FastAPI backend on port 8000)
.\venv\Scripts\uvicorn app.main:app --app-dir backend --port 8000
```
Open your browser to: **`http://localhost:8000/`**

---

## 5. Development Mode (Hot Reloading)

If developing frontend and backend in parallel:

1. **Start Backend Server:**
   ```bash
   .\venv\Scripts\uvicorn app.main:app --app-dir backend --port 8000 --reload
   ```

2. **Start Frontend Dev Server:**
   ```bash
   cd frontend
   npm run dev
   ```
   Open **`http://localhost:5173/`** (Vite proxies all `/api/*` calls to FastAPI on port 8000).

---

## 6. Automated Testing

Run the comprehensive Pytest test suite covering unit calculations, constraints, classification, verification, fallback, and API endpoints:

```bash
# Run tests with verbose output
.\venv\Scripts\pytest backend/tests -v
```

### Test Suite Coverage:
- `test_cost_calculator`: Token costs, multi-attempt sums, CPSO formula, zero-division safeguard.
- `test_request_analyzer_classification`: Task type identification, token heuristics, sensitivity detection.
- `test_eligibility_filter_privacy_and_budget`: Hard privacy tier exclusion, budget ceiling enforcement.
- `test_intelligent_router_strategies`: Always Advanced, Cheapest Eligible, Rule-Based, and AstraRoute scoring.
- `test_quality_guardian_verification`: Python AST code checks, JSON schema validation, arithmetic checks.
- `test_api_health_endpoint`: Gateway diagnostic and provider status check.
- `test_api_models_endpoint`: Model registry retrieval.
- `test_api_request_execute_and_fallback`: Live execution and bounded fallback recovery.
- `test_api_policy_simulator`: What-if simulation projections and trade-off analysis.

---

## 7. AI Provider Integration & Credentials

AstraRoute AI features a unified adapter factory supporting both real provider APIs and high-fidelity simulation:

| Provider | Environment Variable | Models Supported |
| :--- | :--- | :--- |
| **OpenAI** | `OPENAI_API_KEY` | GPT-4o, GPT-4o Mini |
| **Anthropic** | `ANTHROPIC_API_KEY` | Claude 3.5 Sonnet, Claude 3.5 Haiku |
| **Google Gemini** | `GEMINI_API_KEY` | Gemini 1.5 Pro, Gemini 1.5 Flash |
| **Groq LPU** | `GROQ_API_KEY` | Meta Llama 3.3 70B |
| **Local / On-Prem** | Local Endpoint | Ollama Llama 3.1 8B (Zero-Cost Privacy Tier) |

To add keys, copy `.env.example` to `.env` and fill in your keys. If credentials are left blank, AstraRoute AI automatically activates the **High-Fidelity Simulator Mode**, providing realistic latency, tokens, and verification without failing or fabricating claims.

---

## 8. Supabase PostgreSQL Configuration

To persist to Supabase PostgreSQL:
1. Open your Supabase project SQL Editor.
2. Run the provided [`schema.sql`](file:///c:/Users/ASWANTH/OneDrive/Desktop/TCS-Hack/schema.sql) script to generate tables and indexes.
3. In `.env`, set:
   ```env
   DATABASE_URL=postgresql://postgres:[PASSWORD]@db.[REF].supabase.co:5432/postgres
   ```
4. Restart the backend.

---

## 9. Live Demo Walkthrough (TCS Hackathon Judges)

1. **Overview Dashboard (`/`):**
   - Review hero KPI: **Cost Per Successful Outcome ($0.00192)** showing a 63.8% spend reduction.
   - Inspect the Strategy Comparison chart comparing Always Advanced vs AstraRoute.
2. **Request Playground (`/playground`):**
   - Click the preset **"Sales Variance Analysis"** or **"Python LRU Cache"**.
   - Check **"Simulate Attempt 1 Timeout"** and click **Execute Intelligent Route**.
   - Watch the gateway fail attempt 1, catch the timeout, escalate to an eligible fallback candidate, run Quality Guardian verification, and output a verified pass!
   - Click **"Full Trace Audit"** to view the candidate rejection reasons and cost timeline.
3. **Live Routing Arena (`/arena`):**
   - Select the **15 Tasks Suite** and click **Run Benchmark**.
   - Compare all 4 strategies side-by-side. Observe how the unguided *Cheapest Eligible* strategy fails 50%+ of complex tasks, whereas *AstraRoute* maintains 96%+ accuracy with the lowest CPSO!
   - Click **"Export CSV"** to download the benchmark results.
4. **Policy Simulator (`/simulator`):**
   - Move sliders for budget cap and cost weight.
   - View instant projected savings, traffic shift distributions, and trade-off risk warnings.
5. **Adaptive Learning & Recommendations (`/adaptation`, `/recommendations`):**
   - Inspect empirical performance scores, Bayesian smoothing, and 1-click rollback controls.
   - Review actionable FinOps optimization recommendations with 1-click apply to active policy.

---

## 10. License & Compliance
Built for the **TCS AI Hackathon 2026**. Designed for enterprise FinOps excellence, explainable governance, and ethical AI economics.

