from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.limiter import limiter
from app.models.user import User
from app.models.task import Task
from app.schemas import TaskCreate, TaskUpdate, TaskResponse
from app.middleware.security import get_current_user, require_admin

router = APIRouter(prefix="/api/tasks", tags=["tasks"])


@router.get("", response_model=list[TaskResponse])
@limiter.limit("60/minute")
def list_tasks(request: Request, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    rows = (
        db.query(Task.id, Task.title, Task.description, Task.completed,
                 Task.owner_id, User.username, Task.created_at, Task.updated_at)
        .join(User, Task.owner_id == User.id)
    )
    if current_user.role != "admin":
        rows = rows.filter(Task.owner_id == current_user.id)
    rows = rows.order_by(Task.updated_at.desc())
    return [
        {
            "id": r.id,
            "title": r.title,
            "description": r.description,
            "completed": r.completed,
            "owner_id": r.owner_id,
            "owner_name": r.username,
            "created_at": r.created_at,
            "updated_at": r.updated_at,
        }
        for r in rows.all()
    ]


@router.post("", response_model=TaskResponse, status_code=status.HTTP_201_CREATED)
@limiter.limit("30/minute")
def create_task(request: Request, payload: TaskCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    task = Task(
        title=payload.title,
        description=payload.description,
        owner_id=current_user.id,
    )
    db.add(task)
    db.commit()
    db.refresh(task)
    return {
        "id": task.id,
        "title": task.title,
        "description": task.description,
        "completed": task.completed,
        "owner_id": task.owner_id,
        "owner_name": current_user.username,
        "created_at": task.created_at,
        "updated_at": task.updated_at,
    }


@router.get("/{task_id}", response_model=TaskResponse)
@limiter.limit("60/minute")
def get_task(request: Request, task_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    row = (
        db.query(Task.id, Task.title, Task.description, Task.completed,
                 Task.owner_id, User.username, Task.created_at, Task.updated_at)
        .join(User, Task.owner_id == User.id)
        .filter(Task.id == task_id)
        .first()
    )
    if not row:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")
    if row.owner_id != current_user.id and current_user.role != "admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not your task")
    return {
        "id": row.id,
        "title": row.title,
        "description": row.description,
        "completed": row.completed,
        "owner_id": row.owner_id,
        "owner_name": row.username,
        "created_at": row.created_at,
        "updated_at": row.updated_at,
    }


@router.put("/{task_id}", response_model=TaskResponse)
@limiter.limit("30/minute")
def update_task(request: Request, task_id: int, payload: TaskUpdate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    task = db.query(Task).filter(Task.id == task_id).first()
    if not task:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")
    if task.owner_id != current_user.id and current_user.role != "admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not your task")

    if payload.title is not None:
        task.title = payload.title
    if payload.description is not None:
        task.description = payload.description
    if payload.completed is not None:
        task.completed = payload.completed

    db.commit()
    db.refresh(task)
    owner = db.query(User).filter(User.id == task.owner_id).first()
    return {
        "id": task.id,
        "title": task.title,
        "description": task.description,
        "completed": task.completed,
        "owner_id": task.owner_id,
        "owner_name": owner.username,
        "created_at": task.created_at,
        "updated_at": task.updated_at,
    }


@router.delete("/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
@limiter.limit("30/minute")
def delete_task(request: Request, task_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    task = db.query(Task).filter(Task.id == task_id).first()
    if not task:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")
    if task.owner_id != current_user.id and current_user.role != "admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not your task")

    db.delete(task)
    db.commit()
