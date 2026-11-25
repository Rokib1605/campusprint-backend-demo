def test_full_order_crud_lifecycle_and_quote(client, student, sample_order):
    # 20 pages x 2 BDT + 35 BDT binding = 75 BDT per copy; x2 = 150.
    created = client.post("/api/orders", headers=student, json=sample_order)
    assert created.status_code == 201
    order_id = created.json()["data"]["id"]
    assert created.json()["data"]["total_price_bdt"] == 150
    assert created.json()["data"]["status"] == "DRAFT"

    fetched = client.get(f"/api/orders/{order_id}", headers=student)
    assert fetched.status_code == 200
    assert fetched.json()["data"]["document_name"] == "assignment.pdf"

    replacement = {**sample_order, "pages": 10, "copies": 1}
    put = client.put(f"/api/orders/{order_id}", headers=student, json=replacement)
    assert put.status_code == 200
    assert put.json()["data"]["total_price_bdt"] == 55

    patch = client.patch(f"/api/orders/{order_id}", headers=student, json={"copies": 3})
    assert patch.status_code == 200
    assert patch.json()["data"]["total_price_bdt"] == 165

    assert client.delete(f"/api/orders/{order_id}", headers=student).status_code == 204
    assert client.get(f"/api/orders/{order_id}", headers=student).status_code == 404


def test_student_cannot_see_or_edit_others_order(client, student, other_student, sample_order):
    created = client.post("/api/orders", headers=student, json=sample_order)
    order_id = created.json()["data"]["id"]
    assert client.get(f"/api/orders/{order_id}", headers=other_student).status_code == 403
    assert client.patch(f"/api/orders/{order_id}", headers=other_student, json={"copies": 4}).status_code == 403
    assert client.delete(f"/api/orders/{order_id}", headers=other_student).status_code == 403
    assert client.get("/api/orders", headers=other_student).json()["meta"]["total"] == 0
    assert client.get("/api/orders", headers=student).json()["meta"]["total"] == 1


def test_staff_can_list_all_but_cannot_create_student_orders(client, student, other_student, staff, sample_order):
    client.post("/api/orders", headers=student, json=sample_order)
    client.post("/api/orders", headers=other_student, json=sample_order)
    assert client.get("/api/orders", headers=staff).json()["meta"]["total"] == 2
    assert client.post("/api/orders", headers=staff, json=sample_order).status_code == 403
    assert client.delete("/api/orders/1", headers=staff).status_code == 403


def test_invalid_order_input_is_422(client, student, sample_order):
    assert client.post("/api/orders", headers=student, json={**sample_order, "copies": 0}).status_code == 422
    assert client.post("/api/orders", headers=student, json={**sample_order, "pages": 0}).status_code == 422
    assert client.post("/api/orders", headers=student, json={**sample_order, "document_name": "bad.docx"}).status_code == 422
    assert client.post("/api/orders", headers=student, json={**sample_order, "document_name": "../bad.pdf"}).status_code == 422
    assert client.post("/api/orders", headers=student, json={**sample_order, "binding_option_id": -1}).status_code == 422
    assert client.post("/api/orders", headers=student, json={**sample_order, "unknown": 1}).status_code == 422


def test_invalid_print_option_returns_400(client, student, sample_order):
    assert client.post("/api/orders", headers=student, json={**sample_order, "print_option_id": 2}).status_code == 400
    assert client.post("/api/orders", headers=student, json={**sample_order, "print_option_id": 999}).status_code == 400
    assert client.post("/api/orders", headers=student, json={**sample_order, "binding_option_id": 1}).status_code == 400


def test_order_without_binding_uses_per_page_rate(client, student, sample_order):
    res = client.post("/api/orders", headers=student, json={**sample_order, "binding_option_id": None})
    assert res.status_code == 201
    assert res.json()["data"]["total_price_bdt"] == 80
    assert res.json()["data"]["binding_rate_snapshot_bdt"] == 0


def test_list_order_filter_and_pagination(client, student, sample_order):
    for n in range(3):
        client.post("/api/orders", headers=student, json={**sample_order, "copies": n+1})
    listing = client.get("/api/orders?status=DRAFT&page=2&limit=2", headers=student)
    assert listing.status_code == 200
    assert listing.json()["meta"] == {"page": 2, "limit": 2, "total": 3}
    assert len(listing.json()["data"]) == 1
    assert client.get("/api/orders?page=0", headers=student).status_code == 422


def test_missing_order_and_unauthorized_request(client, student, sample_order):
    assert client.get("/api/orders/999", headers=student).status_code == 404
    assert client.post("/api/orders", json=sample_order).status_code == 401
    assert client.get("/api/orders", headers={"x-user-id": "random"}).status_code == 401


def test_patch_revalidates_pdf_name(client, student, sample_order):
    order_id = client.post("/api/orders", headers=student, json=sample_order).json()["data"]["id"]
    assert client.patch(f"/api/orders/{order_id}", headers=student, json={"document_name": "notes.txt"}).status_code == 422
    assert client.patch(f"/api/orders/{order_id}", headers=student, json={}).status_code == 422
    assert client.get(f"/api/orders/{order_id}", headers=student).json()["data"]["document_name"] == "assignment.pdf"


def test_price_snapshot_remains_after_catalog_price_change(client, student, admin, sample_order):
    order_id = client.post("/api/orders", headers=student, json=sample_order).json()["data"]["id"]
    client.patch("/api/print-options/1", headers=admin, json={"unit_price_bdt": 5})
    assert client.get(f"/api/orders/{order_id}", headers=student).json()["data"]["total_price_bdt"] == 150
    edited = client.patch(f"/api/orders/{order_id}", headers=student, json={"copies": 3})
    assert edited.json()["data"]["total_price_bdt"] == (20*5+35)*3
