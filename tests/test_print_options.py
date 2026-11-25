def test_complete_option_crud_lifecycle(client, admin, sample_option):
    # POST -> GET -> PUT -> PATCH -> DELETE -> GET = 404
    created = client.post("/api/print-options", headers=admin, json=sample_option)
    assert created.status_code == 201
    option_id = created.json()["data"]["id"]

    fetched = client.get(f"/api/print-options/{option_id}", headers=admin)
    assert fetched.status_code == 200
    assert fetched.json()["data"]["code"] == "COLOR_A4"

    replacement = {**sample_option, "name": "Premium color A4", "unit_price_bdt": 10}
    updated = client.put(f"/api/print-options/{option_id}", headers=admin, json=replacement)
    assert updated.status_code == 200
    assert updated.json()["data"]["unit_price_bdt"] == 10

    patched = client.patch(f"/api/print-options/{option_id}", headers=admin, json={"available": False})
    assert patched.status_code == 200
    assert patched.json()["data"]["name"] == "Premium color A4"
    assert patched.json()["data"]["available"] is False

    removed = client.delete(f"/api/print-options/{option_id}", headers=admin)
    assert removed.status_code == 204
    assert client.get(f"/api/print-options/{option_id}", headers=admin).status_code == 404


def test_only_admin_may_write_options(client, student, admin, sample_option):
    assert client.post("/api/print-options", headers=student, json=sample_option).status_code == 403
    assert client.patch("/api/print-options/1", headers=student, json={"name": "Nope"}).status_code == 403
    assert client.delete("/api/print-options/1", headers=student).status_code == 403
    assert client.post("/api/print-options", json=sample_option).status_code == 401
    assert client.get("/api/print-options", headers=admin).status_code == 200


def test_validation_prevents_bad_options(client, admin, sample_option):
    assert client.post("/api/print-options", headers=admin, json={**sample_option, "unit_price_bdt": -5}).status_code == 422
    assert client.post("/api/print-options", headers=admin, json={**sample_option, "category": "FOOD"}).status_code == 422
    assert client.post("/api/print-options", headers=admin, json={**sample_option, "unknown_field": True}).status_code == 422
    assert client.patch("/api/print-options/1", headers=admin, json={}).status_code == 422


def test_duplicate_code_is_conflict(client, admin, sample_option):
    first = client.post("/api/print-options", headers=admin, json=sample_option)
    assert first.status_code == 201
    second = client.post("/api/print-options", headers=admin, json=sample_option)
    assert second.status_code == 409


def test_filter_sort_and_paginate_options(client, admin, sample_option):
    client.post("/api/print-options", headers=admin, json=sample_option)
    res = client.get("/api/print-options?category=PRINT&sort=unit_price_bdt&direction=desc&page=1&limit=1", headers=admin)
    assert res.status_code == 200
    assert res.json()["meta"] == {"page": 1, "limit": 1, "total": 2}
    assert res.json()["data"][0]["code"] == "COLOR_A4"
    hidden = client.get("/api/print-options?available=false", headers=admin)
    assert hidden.json()["meta"]["total"] == 0


def test_cannot_remove_referenced_print_option(client, admin, student, sample_order):
    created = client.post("/api/orders", headers=student, json=sample_order)
    assert created.status_code == 201
    assert client.delete("/api/print-options/1", headers=admin).status_code == 409
    assert client.delete("/api/print-options/2", headers=admin).status_code == 409


def test_missing_print_option(client, admin):
    assert client.get("/api/print-options/999", headers=admin).status_code == 404
    assert client.delete("/api/print-options/999", headers=admin).status_code == 404
