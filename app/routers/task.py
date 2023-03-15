from fastapi import Response, status, HTTPException, Depends, APIRouter
from sqlalchemy.orm import Session
from typing import List, Optional

from sqlalchemy import func
# from sqlalchemy.sql.functions import func
from .. import models, schemas, oauth2
from ..database import get_db

router = APIRouter(
    prefix="/tasks",
    tags=['Tasks']
)


@router.get("/", response_model=List[schemas.Task])
def get_tasks(db: Session = Depends(get_db), current_user: int = Depends(oauth2.get_current_user), limit: int = 10,
              skip: int = 0, search: Optional[str] = ""):
    tasks = db.query(models.Task).filter(
        models.Task.title.contains(search)).limit(limit).offset(skip).all()
    return tasks


@router.post("/", status_code=status.HTTP_201_CREATED, response_model=schemas.Task)
def create_tasks(task: schemas.TaskCreate, db: Session = Depends(get_db),
                 current_user: int = Depends(oauth2.get_current_user)):
    new_task = models.Task(owner_id=current_user.id, **task.dict())
    db.add(new_task)
    db.commit()
    db.refresh(new_task)

    return new_task


@router.get("/{id}", response_model=schemas.Task)
def get_task(id: int, db: Session = Depends(get_db), current_user: int = Depends(oauth2.get_current_user)):
    task = db.query(models.Task).filter(models.Task.id == id).first()

    if not task:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"post with id: {id} was not found")

    return task


@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_task(id: int, db: Session = Depends(get_db), current_user: int = Depends(oauth2.get_current_user)):
    task_query = db.query(models.Task).filter(models.Task.id == id)

    task = task_query.first()

    if task is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"post with id: {id} does not exist")

    if str(task.owner_id) != str(current_user.id):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail="Not authorized to perform requested action")

    task_query.delete(synchronize_session=False)
    db.commit()

    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.put("/{id}", response_model=schemas.Task)
def update_task(id: int, updated_post: schemas.TaskCreate, db: Session = Depends(get_db),
                current_user: int = Depends(oauth2.get_current_user)):
    task_query = db.query(models.Task).filter(models.Task.id == id)

    task = task_query.first()

    if task is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"post with id: {id} does not exist")

    if str(task.owner_id) != str(current_user.id):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail="Not authorized to perform requested action")

    task_query.update(updated_post.dict(), synchronize_session=False)

    db.commit()

    return task_query.first()
