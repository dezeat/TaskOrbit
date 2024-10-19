# from sqlalchemy.orm import Session
# from sqlalchemy.exc import NoResultFound
# from models import Task  # Assuming your Task model is imported

# def insert_task(db: Session,data_model:declarative_base, task_data: dict) -> Task:
#     """Insert a new task into the database."""
#     new_row = data_model(**task_data)
#     db.add(new_row)
#     db.commit()
#     db.refresh(new_row)
#     return new_row

# def update_task(db: Session, task_id: int, updates: dict) -> Task:
#     """Update an existing task in the database."""
#     task = db.query(Task).filter(Task.task_id == task_id).one_or_none()
#     if not task:
#         raise NoResultFound(f"Task with id {task_id} not found.")
    
#     for key, value in updates.items():
#         setattr(task, key, value)
    
#     db.commit()
#     db.refresh(task)
#     return task

# def remove_task(db: Session, task_id: int) -> None:
#     """Remove a task from the database."""
#     task = db.query(Task).filter(Task.task_id == task_id).one_or_none()
#     if not task:
#         raise NoResultFound(f"Task with id {task_id} not found.")
    
#     db.delete(task)
#     db.commit()

# def get_all_tasks(db: Session) -> list[Task]:
#     """Retrieve all tasks from the database."""
#     return db.query(Task).all()