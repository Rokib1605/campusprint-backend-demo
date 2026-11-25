from typing import Annotated, Literal

from fastapi import APIRouter, Depends, HTTPException, Query, Response
from pydantic import ValidationError

from app.auth import CurrentUser, require_role
from app.models import Category, OptionInput, OptionPatch, PrintOption
from app.storage import MemoryStore, get_store


router = APIRouter(prefix="/api/print-options", tags=["Print Options"])
Store = Annotated[MemoryStore, Depends(get_store)]


def find_option(store: MemoryStore, option_id: int) -> PrintOption:
    option = store.options.get(option_id)
    if option is None:
        raise HTTPException(status_code=404, detail="Print option not found")
    return option


def assert_unique_code(store: MemoryStore, code: str, except_id: int | None = None) -> None:
    if any(o.code == code and o.id != except_id for o in store.options.values()):
        raise HTTPException(status_code=409, detail="Print option code already exists")


@router.get("")
def list_options(
    store: Store,
    user: CurrentUser,
    category: Category | None = None,
    available: bool | None = None,
    sort: Literal["name", "unit_price_bdt"] = "name",
    direction: Literal["asc", "desc"] = "asc",
    page: int = Query(default=1, ge=1),
    limit: int = Query(default=10, ge=1, le=50),
):
    items = list(store.options.values())
    if category:
        items = [item for item in items if item.category == category]
    if available is not None:
        items = [item for item in items if item.available == available]
    items.sort(key=lambda x: (getattr(x, sort), x.id), reverse=direction == "desc")
    total = len(items)
    return {"data": items[(page - 1) * limit:page * limit], "meta": {"page": page, "limit": limit, "total": total}}


@router.get("/{option_id}")
def get_option(option_id: int, store: Store, user: CurrentUser):
    return {"data": find_option(store, option_id)}


@router.post("", status_code=201)
def create_option(payload: OptionInput, store: Store, user: CurrentUser):
    require_role(user, "ADMIN")
    assert_unique_code(store, payload.code)
    option = PrintOption(id=store.next_option_id, **payload.model_dump())
    store.options[option.id] = option
    store.next_option_id += 1
    return {"data": option}


@router.put("/{option_id}")
def replace_option(option_id: int, payload: OptionInput, store: Store, user: CurrentUser):
    require_role(user, "ADMIN")
    find_option(store, option_id)
    assert_unique_code(store, payload.code, except_id=option_id)
    replacement = PrintOption(id=option_id, **payload.model_dump())
    store.options[option_id] = replacement
    return {"data": replacement}


@router.patch("/{option_id}")
def patch_option(option_id: int, payload: OptionPatch, store: Store, user: CurrentUser):
    require_role(user, "ADMIN")
    old = find_option(store, option_id)
    changes = payload.model_dump(exclude_unset=True)
    if not changes or any(value is None for value in changes.values()):
        raise HTTPException(status_code=422, detail="Supply at least one non-null field")
    try:
        replacement = PrintOption.model_validate({**old.model_dump(), **changes})
    except ValidationError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    assert_unique_code(store, replacement.code, except_id=option_id)
    store.options[option_id] = replacement
    return {"data": replacement}


@router.delete("/{option_id}", status_code=204)
def delete_option(option_id: int, store: Store, user: CurrentUser):
    require_role(user, "ADMIN")
    find_option(store, option_id)
    if any(order.print_option_id == option_id or order.binding_option_id == option_id for order in store.orders.values()):
        raise HTTPException(status_code=409, detail="Option is referenced by an order")
    del store.options[option_id]
    return Response(status_code=204)
