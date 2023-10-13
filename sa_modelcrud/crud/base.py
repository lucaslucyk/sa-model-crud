from datetime import datetime
from typing import Any, Dict, Generic, List, Optional, Type, TypeVar, Union
from uuid import UUID
from pydantic import BaseModel
from sqlalchemy import select, and_, or_
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from ..models.base import ModelBase
from ..exceptions.crud import NotFoundException, CreateException


ModelType = TypeVar("ModelType", bound=ModelBase)
CreateSchemaType = TypeVar("CreateSchemaType", bound=BaseModel)
UpdateSchemaType = TypeVar("UpdateSchemaType", bound=BaseModel)


class CRUDBase(Generic[ModelType, CreateSchemaType, UpdateSchemaType]):
    def __init__(self, model: Type[ModelType]) -> None:
        """CRUD object with default methods to Create, Read, Update, & Delete

        Args:
            model (Type[ModelType]): A SQLAlchemy model class
        """
        self.model = model
        self.and_ = and_
        self.or_ = or_

    async def get(self, db: AsyncSession, uid: UUID) -> Optional[ModelType]:
        """Get row from model where id == model.id

        Args:
            db (AsyncSession): Async db session
            id (Any): Id to filter

        Returns:
            Optional[ModelType]: ModelType instance or None if id not exists
        """
        res = await db.execute(select(self.model).where(self.model.uid == uid))
        return res.scalar()

    async def get_or_raise(
        self, db: AsyncSession, uid: UUID
    ) -> Optional[ModelType]:
        """Try to dgt row from model where id == model.id

        Args:
            db (AsyncSession): Async db session
            id (Any): Id to filter

        Raises:
            HTTPException: HTTP_404_NOT_FOUND if item does not exist

        Returns:
            Optional[ModelType]: ModelType instance
        """

        # try get item
        obj = await self.get(db=db, uid=uid)

        if not obj:
            raise NotFoundException(f"{self.model.__name__} not found")

        return obj

    async def list(
        self, db: AsyncSession, *, skip: int = 0, limit: int = 100
    ) -> List[ModelType]:
        """Get multi items from database without filter criteria

        Args:
            db (AsyncSession): Async db session
            skip (int, optional): Optional Offset. Defaults to 0.
            limit (int, optional): Optional limit. Defaults to 100.

        Returns:
            List[ModelType]: Matching results list
        """
        results = await db.execute(select(self.model).offset(skip).limit(limit))
        return results.scalars().all()

    async def filter(
        self,
        db: AsyncSession,
        *,
        whereclause: Any,
        skip: int = 0,
        limit: int = 100,
    ) -> List[ModelType]:
        """Get items from database using `filters` to filter

        Args:
            db (AsyncSession): Async db session
            filters (Union[list, tuple]): [description]
            criterion (str, optional): [description]. Defaults to 'and'.
            skip (int, optional): Optional Offset. Defaults to 0.
            limit (int, optional): Optional limit. Defaults to 100.
            multiple (bool, optional):
                Optional bool to get single or multi items.
                Defaults to True.

        Returns:
            List[ModelType]:
                Instance or list of intance of matching items.
        """

        # try to get
        result = await db.execute(
            select(self.model).where(whereclause).offset(skip).limit(limit)
        )

        return result.scalars().all()

    async def find(
        self, db: AsyncSession, *, skip: int = 0, limit: int = 100, **kwargs
    ) -> List[ModelType]:
        result = await db.execute(
            select(self.model).filter_by(**kwargs).offset(skip).limit(limit)
        )
        return result.scalars().all()

    async def find_one(self, db: AsyncSession, **kwargs):
        result = await db.execute(
            select(self.model).filter_by(**kwargs).limit(1)
        )
        return result.scalar()

    async def save(self, db: AsyncSession, *, obj: ModelType) -> ModelType:
        # add to database
        if hasattr(obj, "updated_at"):
            setattr(obj, "updated_at", datetime.utcnow())

        db.add(obj)
        await db.commit()
        await db.refresh(obj)

        # return instance
        return obj

    async def create(
        self, db: AsyncSession, *, data: CreateSchemaType
    ) -> ModelType:
        """Try to create item in database

        Args:
            db (AsyncSession): Async db session
            data (CreateSchemaType): Schema to create

        Raises:
            HTTPException: HTTP_400_BAD_REQUEST if item already exists
            HTTPException: HTTP_400_BAD_REQUEST for other errors

        Returns:
            ModelType: Instance of created object
        """

        try:
            # try json encode
            db_obj = self.model(data.model_dump(mode="json"))
            return await self.save(db=db, obj=db_obj)

        except IntegrityError:
            raise CreateException(f"{self.model.__name__} already exists.")

    async def update(
        self,
        db: AsyncSession,
        *,
        obj: ModelType,
        data: Union[UpdateSchemaType, Dict[str, Any]],
    ) -> ModelType:
        """Update a database item with an update schema

        Args:
            db (AsyncSession): Async db session
            obj (ModelType): Item to update
            obj (Union[UpdateSchemaType, Dict[str, Any]]):
                New partial or full data for database item

        Returns:
            ModelType: [description]
        """

        # obj to dict
        if isinstance(data, dict):
            update_data = data
        else:
            update_data = data.model_dump(exclude_unset=True)

        # update obj with each field of obj
        for field, value in update_data.items():
            setattr(obj, field, value)

        return await self.save(db=db, obj=obj)

    async def delete(self, db: AsyncSession, *, uid: UUID) -> ModelType:
        """Delete an item from database

        Args:
            db (AsyncSession): Async db session
            id (int): Id of model to delete

        Returns:
            ModelType: Deleted object instance
        """
        obj = await self.get_or_raise(db=db, uid=uid)

        await db.delete(obj)
        await db.commit()

        return obj
