"""A zero-Postman demo: run `python -m scripts.demo`."""
from fastapi.testclient import TestClient

from app.main import create_app


ADMIN = {"x-user-id": "admin-01"}
STUDENT = {"x-user-id": "student-1605"}
OTHER = {"x-user-id": "student-1609"}


def display(label, response):
    print(f"{label:36s} HTTP {response.status_code}")
    return response


def run():
    with TestClient(create_app()) as client:
        option = display("POST create PRINT option", client.post("/api/print-options", headers=ADMIN, json={
            "code": "COLOR_A4", "name": "Color A4", "category": "PRINT", "unit_price_bdt": 8
        })).json()["data"]["id"]
        display("GET print option", client.get(f"/api/print-options/{option}", headers=ADMIN))
        display("PUT replace print option", client.put(f"/api/print-options/{option}", headers=ADMIN, json={
            "code": "COLOR_A4", "name": "Color Premium", "category": "PRINT", "unit_price_bdt": 10
        }))
        display("PATCH print option", client.patch(f"/api/print-options/{option}", headers=ADMIN, json={"available": False}))
        display("DELETE print option", client.delete(f"/api/print-options/{option}", headers=ADMIN))
        display("GET after delete (404)", client.get(f"/api/print-options/{option}", headers=ADMIN))

        data = {"document_name": "assignment.pdf", "pages": 20, "copies": 2, "print_option_id": 1, "binding_option_id": 2}
        order_res = display("POST create order", client.post("/api/orders", headers=STUDENT, json=data))
        order = order_res.json()["data"]["id"]
        print("  Total quote:", order_res.json()["data"]["total_price_bdt"], "BDT (expected 150)")
        display("GET own order", client.get(f"/api/orders/{order}", headers=STUDENT))
        display("GET other's order (403)", client.get(f"/api/orders/{order}", headers=OTHER))
        display("PATCH order copies", client.patch(f"/api/orders/{order}", headers=STUDENT, json={"copies": 3}))
        display("POST invalid copies (422)", client.post("/api/orders", headers=STUDENT, json={**data, "copies": 0}))
        display("DELETE draft order", client.delete(f"/api/orders/{order}", headers=STUDENT))
        display("GET deleted order (404)", client.get(f"/api/orders/{order}", headers=STUDENT))
    print("\nSee full automated checks: pytest -v")


if __name__ == "__main__":
    run()
