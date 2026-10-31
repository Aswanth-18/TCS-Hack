from fastapi.testclient import TestClient
from app.main import app

def test_recommendations_lifecycle():
    print("=== Testing Recommendations Lifecycle & Count Accuracy ===")
    with TestClient(app) as client:
        # 1. Fetch all recommendations
        r = client.get("/api/finops/recommendations")
        assert r.status_code == 200
        all_recs = r.json()
        print(f"[PASS] Total recommendations in DB: {len(all_recs)}")

        # 2. Count active pending
        pending = [rec for rec in all_recs if rec["status"] == "pending"]
        applied = [rec for rec in all_recs if rec["status"] == "applied"]
        dismissed = [rec for rec in all_recs if rec["status"] == "dismissed"]
        print(f"[PASS] Breakdown: Pending={len(pending)}, Applied={len(applied)}, Dismissed={len(dismissed)}")
        initial_pending_count = len(pending)

        # 3. Test applying a pending recommendation if available
        if pending:
            target = pending[0]
            r_apply = client.post(f"/api/finops/recommendations/{target['id']}/apply")
            assert r_apply.status_code == 200
            print(f"[PASS] Applied recommendation '{target['title']}': {r_apply.json()['message']}")

            # Verify pending count decreased by 1
            r_after = client.get("/api/finops/recommendations")
            new_pending = [rec for rec in r_after.json() if rec["status"] == "pending"]
            assert len(new_pending) == initial_pending_count - 1
            print(f"[PASS] Active pending count properly decreased from {initial_pending_count} to {len(new_pending)}")

        # 4. Verify no duplicates on repeated fetch
        r_repeat = client.get("/api/finops/recommendations")
        assert len(r_repeat.json()) == len(all_recs)
        print("[PASS] Duplicate prevention verified: No duplicate records created on repeated queries.")

    print("\n>>> Recommendations Lifecycle & Count Verified 100% Successfully! <<<")

if __name__ == "__main__":
    test_recommendations_lifecycle()
