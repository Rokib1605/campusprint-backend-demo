from typing import Annotated, Literal

from fastapi import APIRouter, Depends, HTTPException, Query, Response
from pydantic import ValidationError

from app.auth import CurrentUser, DemoUser, require_role
from app.models import OrderInput, OrderPatch, PrintOrder, StatusChange
from app.storage import MemoryStore, get_store


router = APIRouter(prefix="/api/orders", tags=["Orders"])
Store = Annotated[MemoryStore, Depends(get_store)]
ORDER_FIELDS = {"document_name", "pages", "copies", "print_option_id", "binding_option_id"}
TRANSITIONS = {
    "DRAFT": {"SUBMITTED"},
    "SUBMITTED": {"PRINTING", "CANCELLED"},
    "PRINTING": {"READY"},
    "READY": {"COLLECTED"},
}


def find_order(store: MemoryStore, order_id: int) -> PrintOrder:
    order = store.orders.get(order_id)
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    return order


def check_access(order: PrintOrder, user: DemoUser) -> None:
    if user.role == "STUDENT" and order.student_id != user.id:
        raise HTTPException(status_code=403, detail="You cannot access another student's order")


def editable_order(store: MemoryStore, order_id: int, user: DemoUser) -> PrintOrder:
    require_role(user, "STUDENT")
    order = find_order(store, order_id)
    check_access(order, user)
    if order.status != "DRAFT":
        raise HTTPException(status_code=409, detail="Only draft orders can be edited or deleted")
    return order


def calculate(store: MemoryStore, payload: OrderInput) -> dict[str, int]:
    printer = store.options.get(payload.print_option_id)
    if printer is None or printer.category != "PRINT" or not printer.available:
        raise HTTPException(status_code=400, detail="Invalid or unavailable print option")
    binding_rate = 0
    if payload.binding_option_id is not None:
        binder = store.options.get(payload.binding_option_id)
        if binder is None or binder.category != "BINDING" or not binder.available:
            raise HTTPException(status_code=400, detail="Invalid or unavailable binding option")
        binding_rate = binder.unit_price_bdt
    # BDT integers prevent floating point currency rounding errors.
    total = (payload.pages * printer.unit_price_bdt + binding_rate) * payload.copies
    return {
        "print_rate_snapshot_bdt": printer.unit_price_bdt,
        "binding_rate_snapshot_bdt": binding_rate,
        "total_price_bdt": total,
    }


@router.post("", status_code=201)
def create_order(payload: OrderInput, store: Store, user: CurrentUser):
    require_role(user, "STUDENT")
    prices = calculate(store, payload)
    order = PrintOrder(id=store.next_order_id, student_id=user.id, **payload.model_dump(), **prices)
    store.orders[order.id] = order
    store.next_order_id += 1
    return {"data": order}


@router.get("")
def list_orders(
    store: Store,
    user: CurrentUser,
    status: Literal["DRAFT", "SUBMITTED", "PRINTING", "READY", "COLLECTED", "CANCELLED"] | None = None,
    page: int = Query(default=1, ge=1),
    limit: int = Query(default=10, ge=1, le=50),
):
    orders = list(store.orders.values())
    if user.role == "STUDENT":
        orders = [order for order in orders if order.student_id == user.id]
    if status:
        orders = [order for order in orders if order.status == status]
    orders.sort(key=lambda x: x.id, reverse=True)
    total = len(orders)
    return {"data": orders[(page - 1) * limit:page * limit], "meta": {"page": page, "limit": limit, "total": total}}


@router.get("/{order_id}")
def get_order(order_id: int, store: Store, user: CurrentUser):
    order = find_order(store, order_id)
    check_access(order, user)
    return {"data": order}


def update_order(store: MemoryStore, order: PrintOrder, payload: OrderInput) -> PrintOrder:
    prices = calculate(store, payload)
    updated = order.model_copy(update={**payload.model_dump(), **prices})
    store.orders[order.id] = updated
    return updated


@router.put("/{order_id}")
def replace_order(order_id: int, payload: OrderInput, store: Store, user: CurrentUser):
    order = editable_order(store, order_id, user)
    return {"data": update_order(store, order, payload)}


@router.patch("/{order_id}")
def patch_order(order_id: int, payload: OrderPatch, store: Store, user: CurrentUser):
    order = editable_order(store, order_id, user)
    changes = payload.model_dump(exclude_unset=True)
    if not changes:
        raise HTTPException(status_code=422, detail="Supply at least one field")
    try:
        new_values = {key: getattr(order, key) for key in ORDER_FIELDS}
        new_payload = OrderInput.model_validate({**new_values, **changes})
    except ValidationError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    return {"data": update_order(store, order, new_payload)}


@router.patch("/{order_id}/status")
def change_status(order_id: int, payload: StatusChange, store: Store, user: CurrentUser):
    order = find_order(store, order_id)
    check_access(order, user)
    if payload.status not in TRANSITIONS.get(order.status, set()):
        raise HTTPException(status_code=409, detail=f"Invalid status change: {order.status} -> {payload.status}")
    if payload.status in {"SUBMITTED", "CANCELLED"}:
        require_role(user, "STUDENT")
    else:
        if user.role not in {"STAFF", "ADMIN"}:
            raise HTTPException(status_code=403, detail="Only staff/admin can advance printing")
    updated = order.model_copy(update={"status": payload.status})
    store.orders[order_id] = updated
    return {"data": updated}


@router.delete("/{order_id}", status_code=204)
def delete_order(order_id: int, store: Store, user: CurrentUser):
    editable_order(store, order_id, user)
    del store.orders[order_id]
    return Response(status_code=204)
