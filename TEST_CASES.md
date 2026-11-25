# Automated Integration Test Cases

All checks run with `python -m pytest -v`. Tests use HTTP requests and assertions without Postman.

| ID | Feature | Request / Scenario | Expected |
|---|---|---|---|
| OPT-01 | Options | Admin POST valid option | 201, returned new ID |
| OPT-02 | Options | GET the created option | 200, correct details |
| OPT-03 | Options | PUT all editable fields | 200, replaced values |
| OPT-04 | Options | PATCH availability | 200, updated only selected field |
| OPT-05 | Options | DELETE option then GET | 204 then 404 |
| OPT-06 | Options | Student attempts POST/PATCH/DELETE | 403 |
| OPT-07 | Options | Missing demo identity header | 401 |
| OPT-08 | Options | Invalid price/category/extra keys | 422 |
| OPT-09 | Options | POST duplicate option code | 409 |
| OPT-10 | Options | Filter, sort, paginate options | 200, correct metadata/data |
| OPT-11 | Options | Delete option in use by an order | 409 |
| OPT-12 | Options | GET missing option | 404 |
| ORD-01 | Orders | Student POST valid order | 201, total 150 BDT |
| ORD-02 | Orders | GET own order | 200 |
| ORD-03 | Orders | PUT edited draft order | 200, recalculated quote |
| ORD-04 | Orders | PATCH copies in draft | 200, recalculated quote |
| ORD-05 | Orders | DELETE draft, then GET | 204 then 404 |
| ORD-06 | Orders | Other student GET/PATCH/DELETE | 403 |
| ORD-07 | Orders | Student list isolation; staff list all | 200, correct totals |
| ORD-08 | Orders | Zero copies, bad PDF, invalid pages | 422 |
| ORD-09 | Orders | Wrong category or missing option | 400 |
| ORD-10 | Orders | Order without binding | 201, correct per-page quote |
| ORD-11 | Orders | List filter and pagination | 200, correct metadata |
| ORD-12 | Orders | Missing/unknown user header | 401 |
| ORD-13 | Orders | Change catalog rate after order | Old snapshot unchanged until edit |
| FLOW-01 | Workflow | DRAFT > SUBMITTED > PRINTING > READY > COLLECTED | 200 throughout |
| FLOW-02 | Workflow | DRAFT > READY invalid jump | 409 |
| FLOW-03 | Workflow | Student advances printing | 403 |
| FLOW-04 | Workflow | Edit or delete submitted order | 409 |
| FLOW-05 | Workflow | Student cancels submitted order | 200, staff cannot print cancelled order |

Note: HTTP 422 is FastAPI's standard request-validation response. HTTP 409 represents a business-rule conflict.
