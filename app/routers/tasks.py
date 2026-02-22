from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.database import get_db
from app.models.task import Task
from app.models.user import User
from app.schemas.task import TaskCreate, TaskUpdate, TaskStatusUpdate, TaskResponse
from app.dependencies import get_current_user

router = APIRouter(prefix="/tasks", tags=["Tasks"])

# Valid status transitions
TRANSITIONS = {
    "todo": "in_progress",
    "in_progress": "done",
}


@router.post("/", response_model=TaskResponse, status_code=201)
async def create_task(
    body: TaskCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    task = Task(**body.model_dump(), owner_id=current_user.id)
    db.add(task)
    await db.flush()
    return task


@router.get("/", response_model=list[TaskResponse])
async def get_tasks(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    query = select(Task)
    if not current_user.is_admin:
        query = query.where(Task.owner_id == current_user.id)
    result = await db.execute(query)
    return result.scalars().all()


@router.get("/{task_id}", response_model=TaskResponse)
async def get_task(
    task_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await db.execute(select(Task).where(Task.id == task_id))
    task = result.scalar_one_or_none()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    if task.owner_id != current_user.id and not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Not your task")
    return task


@router.patch("/{task_id}", response_model=TaskResponse)
async def update_task(
    task_id: str,
    body: TaskUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await db.execute(select(Task).where(Task.id == task_id))
    task = result.scalar_one_or_none()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    if task.owner_id != current_user.id and not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Not your task")

    if body.title is not None:
        task.title = body.title
    if body.description is not None:
        task.description = body.description
    if body.total_minutes is not None:
        task.total_minutes = body.total_minutes

    return task


@router.patch("/{task_id}/status", response_model=TaskResponse)
async def update_status(
    task_id: str,
    body: TaskStatusUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await db.execute(select(Task).where(Task.id == task_id))
    task = result.scalar_one_or_none()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    if task.owner_id != current_user.id and not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Not your task")

    allowed_next = TRANSITIONS.get(task.status)
    if body.status != allowed_next:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid transition: '{task.status}' → '{body.status}'. Expected '{allowed_next}'",
        )

    task.status = body.status
    return task


@router.delete("/{task_id}", status_code=204)
async def delete_task(
    task_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await db.execute(select(Task).where(Task.id == task_id))
    task = result.scalar_one_or_none()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    if task.owner_id != current_user.id and not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Not your task")
    await db.delete(task)