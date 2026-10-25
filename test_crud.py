"""
Automated Integration Tests for Students Database CRUD API
Covers Step 3 (Core CRUD) and Step 4 (Error Handling & Validation Edge Cases).
"""
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)


def test_crud_and_error_handling():
    print("\n--- [1] POST /students (Create) ---")
    student_payload = {
        "name": "Priya Patel",
        "date_of_birth": "2003-04-12",
        "email": "priya.patel@example.com",
        "phone": "+91-9876543210",
        "course": "Data Science",
        "address": "Ahmedabad, Gujarat",
        "enrollment_date": "2023-07-15",
    }
    r = client.post("/students", json=student_payload)
    assert r.status_code == 201, f"Failed: {r.text}"
    student_data = r.json()
    student_id = student_data["student_id"]
    print(f"Created student #{student_id}: {student_data['name']} (Course: {student_data['course']})")

    print("\n--- [2] GET /students (List with filter) ---")
    r = client.get("/students?course=Data")
    assert r.status_code == 200
    results = r.json()
    assert len(results) >= 1
    print(f"Filter ?course=Data returned {len(results)} student(s)")

    print("\n--- [3] GET /students/{id} (View single profile) ---")
    r = client.get(f"/students/{student_id}")
    assert r.status_code == 200
    assert r.json()["email"] == "priya.patel@example.com"
    print(f"Retrieved student profile #{student_id}: {r.json()['name']}")

    print("\n--- [4] PATCH /students/{id} (Partial update) ---")
    r = client.patch(f"/students/{student_id}", json={"course": "Advanced Data Science & AI"})
    assert r.status_code == 200
    assert r.json()["course"] == "Advanced Data Science & AI"
    print(f"PATCH successfully updated course: {r.json()['course']}")

    print("\n--- [5] PUT /students/{id} (Update address) ---")
    r = client.put(f"/students/{student_id}", json={"address": "Gandhinagar, Gujarat"})
    assert r.status_code == 200
    assert r.json()["address"] == "Gandhinagar, Gujarat"
    print(f"PUT successfully updated address: {r.json()['address']}")

    print("\n--- [6] DELETE /students/{id} (Remove student) ---")
    r = client.delete(f"/students/{student_id}")
    assert r.status_code == 200
    print(f"DELETE successful: {r.json()['message']}")

    print("\n--- [7] Edge Case: 404 Not Found Handling ---")
    # GET missing student
    r = client.get(f"/students/{student_id}")
    assert r.status_code == 404
    print(f"GET missing student -> 404: {r.json()['detail']}")

    # PATCH missing student
    r = client.patch(f"/students/{student_id}", json={"name": "Ghost"})
    assert r.status_code == 404
    print(f"PATCH missing student -> 404: {r.json()['detail']}")

    # DELETE missing student
    r = client.delete(f"/students/{student_id}")
    assert r.status_code == 404
    print(f"DELETE missing student -> 404: {r.json()['detail']}")

    print("\n--- [8] Edge Case: 422 Unprocessable Entity Validation ---")
    # Malformed date
    r = client.post("/students", json={
        "name": "Invalid Date Student",
        "date_of_birth": "31-02-2004",  # Malformed
        "email": "test@example.com"
    })
    assert r.status_code == 422
    print("Malformed date correctly caught -> 422 Unprocessable Entity")

    # Invalid email format
    r = client.post("/students", json={
        "name": "Invalid Email Student",
        "date_of_birth": "2003-01-01",
        "email": "not-an-email-at-all"
    })
    assert r.status_code == 422
    print("Invalid email format correctly caught -> 422 Unprocessable Entity")

    # Missing both email and phone (contact requirement)
    r = client.post("/students", json={
        "name": "No Contact Student",
        "date_of_birth": "2003-01-01"
    })
    assert r.status_code == 422
    print("Missing contact info (no email AND no phone) -> 422 Unprocessable Entity")

    print("\n--- [9] Step 5: POST /ask (Ollama AI Extension) ---")
    # Test 1: Real offline check (returns 503 with instructions)
    r = client.post("/ask", json={"query": "How many students are enrolled?"})
    assert r.status_code in [200, 503]
    if r.status_code == 503:
        print("Offline Ollama properly handled -> 503 Service Unavailable with setup guidance:")
        print(f"Detail: {r.json()['detail'][:90]}...")

    # Test 2: Mocked AI query to verify grounding & response schema
    from unittest.mock import patch
    with patch("main.query_local_ollama") as mock_ollama:
        mock_ollama.return_value = "There is 1 student currently enrolled."
        # Create a sample student first
        client.post("/students", json={
            "name": "Ananya Roy",
            "date_of_birth": "2004-09-18",
            "email": "ananya@example.com",
            "course": "Computer Science"
        })
        r = client.post("/ask", json={"query": "How many students are enrolled in Computer Science?"})
        assert r.status_code == 200, f"AI ask failed: {r.text}"
        ai_data = r.json()
        assert ai_data["response"] == "There is 1 student currently enrolled."
        assert ai_data["grounded_record_count"] >= 1
        print(f"Mocked Ollama response verified -> 200 OK:")
        print(f"Query: '{ai_data['query']}'")
        print(f"Response: '{ai_data['response']}' (Grounded on {ai_data['grounded_record_count']} records)")

    print("\n==============================================")
    print("ALL CRUD, VALIDATION, AND AI TESTS PASSED!")
    print("==============================================")


if __name__ == "__main__":
    test_crud_and_error_handling()

