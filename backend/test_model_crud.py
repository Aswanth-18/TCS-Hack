from fastapi.testclient import TestClient
from app.main import app

def test_model_lifecycle():
    print("=== Testing Dynamic Model Registry Persistence ===")
    with TestClient(app) as client:
        # 1. Fetch initial models
        r = client.get("/api/models")
        assert r.status_code == 200
        initial_count = len(r.json())
        print(f"[PASS] Initial model count: {initial_count}")

        # 2. Add New Model
        new_model_payload = {
            "name": "Dynamic Llama 3.3 70B",
            "model_id": "dynamic-llama-70b-test",
            "provider": "groq",
            "tier": "balanced",
            "input_cost_per_m": 0.55,
            "output_cost_per_m": 0.75,
            "latency_p50_ms": 280,
            "context_window": 128000,
            "supported_tasks": ["coding", "reasoning"],
            "capabilities": ["code", "reasoning"],
            "privacy_tier": "standard",
            "benchmark_quality_score": 0.88,
            "reliability_rate": 0.995,
            "enabled": True,
            "is_healthy": True
        }
        r_add = client.post("/api/models", json=new_model_payload)
        assert r_add.status_code == 200, f"Add failed: {r_add.text}"
        added = r_add.json()
        assert added["model_id"] == "dynamic-llama-70b-test"
        print(f"[PASS] Successfully registered: {added['name']} ({added['model_id']})")

        # 3. Verify it persists and is returned in registry
        r_list = client.get("/api/models")
        assert len(r_list.json()) == initial_count + 1
        print(f"[PASS] Persisted in registry. New count: {len(r_list.json())}")

        # 4. Edit Model
        r_edit = client.patch("/api/models/dynamic-llama-70b-test", json={
            "input_cost_per_m": 0.45,
            "benchmark_quality_score": 0.91,
            "enabled": False
        })
        assert r_edit.status_code == 200
        updated = r_edit.json()
        assert updated["input_cost_per_m"] == 0.45
        assert updated["benchmark_quality_score"] == 0.91
        assert updated["enabled"] is False
        print("[PASS] Successfully updated model metadata and disabled status.")

        # 5. Remove Model
        r_del = client.delete("/api/models/dynamic-llama-70b-test")
        assert r_del.status_code == 200
        del_data = r_del.json()
        assert del_data["status"] in ["deleted", "deactivated"]
        print(f"[PASS] Delete action executed: {del_data['status']} - {del_data['message']}")

        # 6. Verify count restored
        r_after = client.get("/api/models")
        assert len(r_after.json()) == initial_count
        print(f"[PASS] Registry count restored to {len(r_after.json())}")

    print("\n>>> Dynamic Model Registry Add/Edit/Delete Tests Verified 100% Successfully! <<<")

if __name__ == "__main__":
    test_model_lifecycle()

