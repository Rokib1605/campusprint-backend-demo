# CampusPrint Backend - CRUD & Integration Testing Demo

**IIT, University of Dhaka | Web Technology Lab | Backend demonstration**

Standalone classroom project implementing **two CampusPrint features** using **Python + FastAPI + Pydantic**. Integration tests use **pytest + FastAPI TestClient (HTTPX)** to automatically perform the HTTP calls that would otherwise be tested manually in Postman.

The implementation is original to this demo and independent of the reference Node.js repository.

## Features

**Feature 1 - Print options & pricing (Admin CRUD)**

| Method | Route | Why |
|---|---|---|
| POST | `/api/print-options` | Create option (201) |
| GET | `/api/print-options` | List with category, availability, sorting and pagination (200) |
| GET | `/api/print-options/{id}` | Read one option (200/404) |
| PUT | `/api/print-options/{id}` | Replace all editable fields (200) |
| PATCH | `/api/print-options/{id}` | Update selected fields (200) |
| DELETE | `/api/print-options/{id}` | Delete option (204/409 when referenced) |

**Feature 2 - Student print orders (CRUD + quote + status)**

| Method | Route | Why |
|---|---|---|
| POST | `/api/orders` | Create an order; automatically calculate BDT price (201) |
| GET | `/api/orders` | List only your orders (staff/admin see all), filter and paginate (200) |
| GET | `/api/orders/{id}` | Read one order (200/403/404) |
| PUT | `/api/orders/{id}` | Replace editable details of own DRAFT order (200) |
| PATCH | `/api/orders/{id}` | Update some details, recalculate quote (200) |
| DELETE | `/api/orders/{id}` | Delete your own DRAFT order (204) |
| PATCH | `/api/orders/{id}/status` | Valid transitions by student/staff role (200/403/409) |

**Quote example:** 20 pages x 2 BDT x 2 copies + 35 BDT binding x 2 copies = **150 BDT**. Prices are integers in BDT to avoid floating-point rounding issues. An existing quote retains its price snapshot when catalog rates change; a draft edit recalculates using current rates.

## Quick start

Requires Python 3.10+.

```bash
python -m venv .venv
source .venv/bin/activate            # Windows: .venv\Scripts\activate
python -m pip install -r requirements.txt
python -m pytest -v                 # AUTOMATED TESTS; no Postman needed
python -m scripts.demo              # Step-by-step demo of HTTP status codes
uvicorn app.main:app --reload       # Optional running server
```

Interactive API docs are available at **http://127.0.0.1:8000/docs** after starting Uvicorn.

## Demo users (x-user-id request header)

| Header value | Role | Allowed actions |
|---|---|---|
| `student-1605` | Student 1 | Create and manage own draft orders |
| `student-1609` | Student 2 | Cannot view Student 1's orders |
| `staff-01` | Staff | See all orders and advance printing workflow |
| `admin-01` | Admin | Manage print options and advance printing workflow |

**Important:** The `x-user-id` header simulates identity for teaching. This is **not real authentication** and must not be used as a security system in production. Data is stored **in memory** and is lost on server restart. No real PDF uploads, database, payments or production login are implemented.

## How integration testing replaces Postman

`tests/` uses a **fresh FastAPI application and fresh in-memory database in every test**. FastAPI's `TestClient` sends full HTTP requests through the routes, role checks, Pydantic validation and business logic, then pytest asserts the status code and JSON response. Tests cover complete CRUD lifecycles, negative validation, forbidden access, ownership, filtering, duplicate codes, pricing snapshots and workflow transitions.

```python
response = client.post('/api/orders', headers={'x-user-id':'student-1605'}, json={
    'document_name':'assignment.pdf', 'pages':20, 'copies':2,
    'print_option_id':1, 'binding_option_id':2
})
assert response.status_code == 201
assert response.json()['data']['total_price_bdt'] == 150
```

**Complete CRUD demonstration:** `tests/test_orders.py::test_full_order_crud_lifecycle_and_quote` and `tests/test_print_options.py::test_complete_option_crud_lifecycle` send `POST -> GET -> PUT -> PATCH -> DELETE -> GET (404)` automatically.

### Test case matrix

See [`TEST_CASES.md`](TEST_CASES.md) for the table of expected success and failure responses.

### CI

On each push or pull request, `.github/workflows/tests.yml` installs requirements and runs `python -m pytest -v`. Inspect the Actions tab after publishing to GitHub to confirm the checks pass there too.

## Viva script (30 seconds)

> Sir, I implemented two CampusPrint backend features: Print Option Management and Print Order Management. FastAPI defines the GET, POST, PUT, PATCH and DELETE routes. Pydantic validates inputs. Student, staff and admin demo identities enforce role checks and order ownership. The order service automatically calculates the price. I used pytest and FastAPI TestClient for integration testing; tests send real HTTP requests to the application without starting a separate server, check JSON and status codes, and automatically cover the full CRUD lifecycle plus failure cases. I can show the routes, test files and execute `python -m pytest -v`.

## Folder guide

- `app/options.py` - feature 1 endpoint implementation
- `app/orders.py` - feature 2 endpoint implementation + quote/workflow
- `app/models.py` - request/data validation
- `app/auth.py` - demo identity and role checks
- `app/storage.py` - testable in-memory data store
- `tests/` - automated integration tests
- `scripts/demo.py` - one-command classroom scenario
- `.github/workflows/tests.yml` - GitHub Actions test run

## Publish as a public GitHub repo

Create a **public** repository named `campusprint-backend-demo` on GitHub **without** auto-generating a README or .gitignore, then from this directory run:

```bash
git init
git add .
git commit -m "Implement CampusPrint CRUD API and integration tests"
git branch -M main
git remote add origin https://github.com/Rokib1605/campusprint-backend-demo.git
git push -u origin main
```

The target account is `Rokib1605`. GitHub must have the new public repository created first. Do not upload the `.venv/` directory.
