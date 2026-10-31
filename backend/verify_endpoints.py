import sys
import json
from fastapi.testclient import TestClient
from app.main import app

def run_verification():
    print("=== Starting End-to-End API Verification ===")
    with TestClient(app) as client:
        # 1. Health check
        r = client.get("/api/health")
        assert r.status_code == 200, f"/api/health returned {r.status_code}"
        h_data = r.json()
        assert h_data["liveness"] is True
        assert h_data["readiness"] is True
        assert h_data["database"]["connected"] is True
        print(f"[PASS] /api/health: {h_data['status']}, Database connected: {h_data['database']['connected']}, Mode: {h_data['mode']}")

        # 2. Liveness & Readiness
        r_live = client.get("/api/health/live")
        assert r_live.status_code == 200
        r_ready = client.get("/api/health/ready")
        assert r_ready.status_code == 200
        print("[PASS] /api/health/live & /api/health/ready: 200 OK")

        # 3. FinOps Recommendations
        r_rec = client.get("/api/finops/recommendations")
        assert r_rec.status_code == 200, f"/api/finops/recommendations returned {r_rec.status_code}"
        recs = r_rec.json()
        assert isinstance(recs, list)
        print(f"[PASS] /api/finops/recommendations: 200 OK, count={len(recs)}")

        # 4. FinOps Summary
        r_sum = client.get("/api/finops/summary")
        assert r_sum.status_code == 200, f"/api/finops/summary returned {r_sum.status_code}"
        summary = r_sum.json()
        assert "total_spend_usd" in summary
        assert "cost_per_successful_outcome" in summary
        assert "strategy_comparison" in summary
        print(f"[PASS] /api/finops/summary: 200 OK, total_spend=${summary['total_spend_usd']:.4f}, CPSO=${summary['cost_per_successful_outcome'] or 0:.4f}, strategies={len(summary['strategy_comparison'])}")

        # 5. Models Registry
        r_models = client.get("/api/models")
        assert r_models.status_code == 200
        models = r_models.json()
        assert len(models) >= 8
        print(f"[PASS] /api/models: 200 OK, model count={len(models)}")

        # 6. Policies
        r_pol = client.get("/api/policies")
        assert r_pol.status_code == 200
        pol = r_pol.json()
        assert "max_budget_per_request" in pol
        print(f"[PASS] /api/policies: 200 OK, active policy version={pol['version']}")

        # 7. Request Analysis
        r_ana = client.post("/api/requests/analyze", json={
            "prompt": "Analyze our enterprise budget spreadsheet and return a structured summary of quarterly expenses"
        })
        assert r_ana.status_code == 200
        analysis = r_ana.json()
        print(f"[PASS] /api/requests/analyze: task={analysis['detected_task_type']}, complexity={analysis['detected_complexity']}, quality_target={analysis['required_quality_target']}")

        # 8. Request Execution
        r_exec = client.post("/api/requests/execute", json={
            "prompt": "Write a Python function to validate an email address regex",
            "task_type": "coding"
        })
        assert r_exec.status_code == 200
        execution = r_exec.json()
        assert execution["execution_status"] in ["success", "partially_verified"]
        print(f"[PASS] /api/requests/execute: 200 OK, selected={execution['selected_model_id']}, status={execution['execution_status']}, cost=${execution['total_cost_usd']:.6f}")

        # 9. SPA Index HTML
        r_spa = client.get("/")
        assert r_spa.status_code == 200
        assert "<div id=\"root\"></div>" in r_spa.text
        print("[PASS] SPA root (GET /): 200 OK, served Vite production HTML index bundle")

        # 10. Audit History
        r_audit = client.get("/api/audit")
        assert r_audit.status_code == 200
        audits = r_audit.json()
        print(f"[PASS] /api/audit: 200 OK, logs recorded={len(audits)}")

    print("\n>>> All 10/10 Core End-to-End System Invariants Verified Successfully! <<<")

if __name__ == "__main__":
    run_verification()
