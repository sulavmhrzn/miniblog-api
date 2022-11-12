from fastapi import HTTPException, status
from loguru import logger
from sqlalchemy.orm import Session
from sqlalchemy.orm.decl_api import DeclarativeMeta

from db import engine


def get_object_or_404(model: DeclarativeMeta, pk: int):
    """Get a single object from database

    Args:
        model (_type_): Model to query
        pk (int): Primary key of the model

    Raises:
        HTTPException: If no object is found

    Returns:
        The object instance or None
    """
    with Session(engine) as db:
        logger.info(f"Querying table: {model.__tablename__}, with pk: {pk}")
        result = db.query(model).get(pk)
        if not result:
            logger.info(f"Object not found with id {pk}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Object not found"
            )
    logger.info(f"Object found with id {pk}")
    return result
