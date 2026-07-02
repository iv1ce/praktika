from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.limiter import limiter
from app.models.user import User
from app.schemas import UserResponse, UserUpdate, UserStatusUpdate, UserRoleUpdate
from app.middleware.security import get_current_user, require_admin
from app.services.auth import hash_password, verify_password

router = APIRouter(prefix="/api/users", tags=["users"])


@router.get(
    "/me",
    response_model=UserResponse,
    summary="Профиль текущего пользователя",
    response_description="Данные авторизованного пользователя",
)
@limiter.limit("60/minute")
def get_me(request: Request, current_user: User = Depends(get_current_user)):
    """Возвращает информацию о текущем пользователе: логин, почта, роль, статус, last_login."""
    return current_user


@router.put(
    "/me",
    response_model=UserResponse,
    summary="Обновить профиль",
    response_description="Обновлённые данные пользователя",
)
@limiter.limit("10/minute")
def update_me(
    request: Request,
    payload: UserUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if payload.email is not None:
        if db.query(User).filter(User.email == payload.email, User.id != current_user.id).first():
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already taken")
        current_user.email = payload.email

    if payload.new_password is not None:
        if not payload.old_password:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Old password is required")
        if not verify_password(payload.old_password, current_user.hashed_password):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Old password is incorrect")
        current_user.hashed_password = hash_password(payload.new_password)

    db.commit()
    db.refresh(current_user)
    return current_user


@router.get(
    "",
    response_model=list[UserResponse],
    summary="Список пользователей (admin)",
    response_description="Массив всех зарегистрированных пользователей",
)
@limiter.limit("30/minute")
def list_users(request: Request, db: Session = Depends(get_db), admin: User = Depends(require_admin)):
    """Только для admin. Возвращает всех пользователей с id, логином, почтой, ролью и статусом."""
    return db.query(User).all()


@router.patch(
    "/{user_id}/status",
    response_model=UserResponse,
    summary="Блокировка / разблокировка (admin)",
    response_description="Обновлённые данные пользователя",
)
@limiter.limit("30/minute")
def toggle_user_status(
    request: Request,
    user_id: int,
    payload: UserStatusUpdate,
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin),
):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    if user.id == admin.id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Cannot block yourself")

    user.is_active = payload.is_active
    if payload.is_active:
        user.failed_login_attempts = 0
        user.locked_until = None
    db.commit()
    db.refresh(user)
    return user


@router.patch(
    "/{user_id}/role",
    response_model=UserResponse,
    summary="Смена роли (admin)",
    response_description="Обновлённые данные пользователя",
)
@limiter.limit("30/minute")
def change_user_role(
    request: Request,
    user_id: int,
    payload: UserRoleUpdate,
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin),
):
    if payload.role not in ("user", "admin"):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Role must be 'user' or 'admin'")

    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    if user.id == admin.id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Cannot change your own role")

    user.role = payload.role
    db.commit()
    db.refresh(user)
    return user


@router.delete(
    "/{user_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Удалить пользователя (admin)",
    response_description="Пользователь удалён, тело ответа пустое",
)
@limiter.limit("30/minute")
def delete_user(request: Request, user_id: int, db: Session = Depends(get_db), admin: User = Depends(require_admin)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    db.delete(user)
    db.commit()
