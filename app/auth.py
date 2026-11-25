from dataclasses import dataclass
from typing import Annotated, Literal

from fastapi import Depends, Header, HTTPException


Role = Literal["STUDENT", "STAFF", "ADMIN"]


@dataclass(frozen=True)
class DemoUser:
    id: str
    role: Role


USERS = {
    "student-1605": DemoUser("student-1605", "STUDENT"),
    "student-1609": DemoUser("student-1609", "STUDENT"),
    "staff-01": DemoUser("staff-01", "STAFF"),
    "admin-01": DemoUser("admin-01", "ADMIN"),
}


def get_user(x_user_id: Annotated[str | None, Header()] = None) -> DemoUser:
    """Header based identity is ONLY for classroom demos, not production auth."""
    user = USERS.get(x_user_id or "")
    if user is None:
        raise HTTPException(status_code=401, detail="Use a valid x-user-id demo header")
    return user


CurrentUser = Annotated[DemoUser, Depends(get_user)]


def require_role(user: DemoUser, role: Role) -> None:
    if user.role != role:
        raise HTTPException(status_code=403, detail=f"Only {role.lower()} users can do this")
