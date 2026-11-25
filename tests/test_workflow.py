def test_complete_staff_order_workflow(client, student, staff, sample_order):
    order_id = client.post("/api/orders", headers=student, json=sample_order).json()["data"]["id"]
    assert client.patch(f"/api/orders/{order_id}/status", headers=student, json={"status": "SUBMITTED"}).status_code == 200
    assert client.patch(f"/api/orders/{order_id}/status", headers=staff, json={"status": "PRINTING"}).status_code == 200
    assert client.patch(f"/api/orders/{order_id}/status", headers=staff, json={"status": "READY"}).status_code == 200
    finished = client.patch(f"/api/orders/{order_id}/status", headers=staff, json={"status": "COLLECTED"})
    assert finished.status_code == 200
    assert finished.json()["data"]["status"] == "COLLECTED"


def test_invalid_jump_and_role_enforcement(client, student, staff, sample_order):
    order_id = client.post("/api/orders", headers=student, json=sample_order).json()["data"]["id"]
    assert client.patch(f"/api/orders/{order_id}/status", headers=staff, json={"status": "READY"}).status_code == 409
    assert client.patch(f"/api/orders/{order_id}/status", headers=staff, json={"status": "SUBMITTED"}).status_code == 403
    assert client.patch(f"/api/orders/{order_id}/status", headers=student, json={"status": "SUBMITTED"}).status_code == 200
    assert client.patch(f"/api/orders/{order_id}/status", headers=student, json={"status": "PRINTING"}).status_code == 403
    assert client.patch(f"/api/orders/{order_id}", headers=student, json={"copies": 5}).status_code == 409
    assert client.delete(f"/api/orders/{order_id}", headers=student).status_code == 409


def test_student_may_cancel_submitted_order_but_not_subsequently_print(client, student, staff, sample_order):
    order_id = client.post("/api/orders", headers=student, json=sample_order).json()["data"]["id"]
    client.patch(f"/api/orders/{order_id}/status", headers=student, json={"status": "SUBMITTED"})
    cancelled = client.patch(f"/api/orders/{order_id}/status", headers=student, json={"status": "CANCELLED"})
    assert cancelled.status_code == 200
    assert client.patch(f"/api/orders/{order_id}/status", headers=staff, json={"status": "PRINTING"}).status_code == 409


def test_new_app_has_fresh_isolated_data(client, student, sample_order):
    assert client.get("/api/orders", headers=student).json()["meta"]["total"] == 0
    client.post("/api/orders", headers=student, json=sample_order)
    assert client.get("/api/orders", headers=student).json()["meta"]["total"] == 1
