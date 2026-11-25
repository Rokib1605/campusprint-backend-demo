# 3-Minute Teacher Demonstration

## 1. Show the public repo on GitHub
Open the README, explain the two features, then open `app/options.py`, `app/orders.py`, and `tests/`.

## 2. Run the tests

```bash
python -m pytest -v
```

Point out the two full CRUD scenarios:
- `tests/test_print_options.py::test_complete_option_crud_lifecycle`
- `tests/test_orders.py::test_full_order_crud_lifecycle_and_quote`

Both perform POST, GET, PUT, PATCH, DELETE, and GET again (expect 404).

## 3. Show an automatic Postman-style demonstration

```bash
python -m scripts.demo
```

It prints each request's HTTP response status. 201 means created; 200 means successful read or update; 204 means deleted; 404 means missing; 403 means forbidden; 422 means invalid request input.

## 4. Explain how it works

Teacher: What is backend CRUD?
Answer: CRUD is create, read, update, delete. We use POST, GET, PUT/PATCH, DELETE.

Teacher: What is integration testing?
Answer: TestClient sends an HTTP request to the real FastAPI app, passing through its routes, validation, role checks and data store. pytest verifies the response with assertions.

Teacher: Where is validation?
Answer: `app/models.py` uses Pydantic. Zero copies, negative prices and invalid files are rejected with 422.

Teacher: Why is another student forbidden?
Answer: `app/orders.py` checks the order's student_id against the `x-user-id` demo header. If mismatched, it returns 403.

Teacher: Why does a 20-page order cost 150 BDT?
Answer: `((20 pages * 2 BDT) + 35 BDT binding) * 2 copies = 150 BDT`.

Teacher: Why did you not use Postman?
Answer: The API calls and expected status/data checks are automated inside pytest tests; Postman is not needed to rerun the same cases.

Teacher: Is there real authentication or database?
Answer: No. The identity header is simulated for the lab, and data is stored in memory. I would use authentication and a persistent database in a production system.
