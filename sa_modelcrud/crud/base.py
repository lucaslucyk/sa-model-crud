from abc import ABC, abstractproperty
from datetime import datetime
from typing import (
    Any,
    Dict,
    Generic,
    Iterable,
    List,
    Optional,
    Type,
    TypeVar,
    Union,
)
from uuid import UUID
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from ..models.base import ModelBase
from ..exceptions.crud import NotFoundException, CreateException


ModelType = TypeVar("ModelType", bound=ModelBase)
CreateSchemaType = TypeVar("CreateSchemaType", bound=BaseModel)
UpdateSchemaType = TypeVar("UpdateSchemaType", bound=BaseModel)


class CRUDBase(Generic[ModelType, CreateSchemaType, UpdateSchemaType], ABC):
    @abstractproperty
    def model(self) -> Type[ModelType]:
        ...

    async def get(self, db: AsyncSession, uid: UUID) -> Optional[ModelType]:
        """Get row from model by uid

        Args:
            db (AsyncSession): Async db session
            uid (UUID): UUID to filter

        Returns:
            Optional[ModelType]: ModelType instance or None if id not exists
        """

        res = await db.execute(select(self.model).where(self.model.uid == uid))
        return res.scalar()

    async def get_or_raise(
        self, db: AsyncSession, uid: UUID
    ) -> Optional[ModelType]:
        """Try to get row from model by uid

        Args:
            db (AsyncSession): Async db session
            uid (UUID): UUID to filter

        Raises:
            NotFoundException: If item does not exist

        Returns:
            Optional[ModelType]: ModelType instance
        """

        # try get item
        obj = await self.get(db=db, uid=uid)

        if not obj:
            raise NotFoundException(f"{self.model.__name__} not found")

        return obj

    async def list(
        self, db: AsyncSession, *, offset: int = 0, limit: int = 100
    ) -> List[ModelType]:
        """Get multi items from database without filter criteria

        Args:
            db (AsyncSession): Async db session
            offset (int, optional): Optional Offset. Defaults to 0.
            limit (int, optional): Optional limit. Defaults to 100.

        Returns:
            List[ModelType]: Matching results list
        """

        results = await db.execute(
            select(self.model).offset(offset).limit(limit)
        )
        return results.scalars().all()

    async def filter(
        self,
        db: AsyncSession,
        whereclause: Any,
        *,
        offset: int = 0,
        limit: int = 100,
    ) -> List[ModelType]:
        """Get items from database using `whereclause` to filter

        Args:
            db (AsyncSession): Async db session
            whereclause (Any): Whereclause to filter.
            offset (int, optional): Optional Offset. Defaults to 0.
            limit (int, optional): Optional limit. Defaults to 100.

        Returns:
            List[ModelType]:
                Instance or list of intance of matching items.
        """

        # try to get
        result = await db.execute(
            select(self.model).where(whereclause).offset(offset).limit(limit)
        )

        return result.scalars().all()

    async def find(
        self, db: AsyncSession, *, offset: int = 0, limit: int = 100, **kwargs
    ) -> List[ModelType]:
        """Find elements with kwargs

        Args:
            db (AsyncSession): Async db session
            offset (int, optional): Optional Offset. Defaults to 0.
            limit (int, optional): Optional limit. Defaults to 100.

        Returns:
            List[ModelType]: list of results
        """

        result = await db.execute(
            select(self.model).filter_by(**kwargs).offset(offset).limit(limit)
        )

        return result.scalars().all()

    async def find_one(self, db: AsyncSession, **kwargs) -> ModelType:
        """Find an element with kwargs

        Args:
            db (AsyncSession): Async db session

        Returns:
            ModelType: First result object
        """

        result = await db.execute(
            select(self.model).filter_by(**kwargs).limit(1)
        )

        return result.scalar()

    @staticmethod
    def _set_updated_at(element: ModelType) -> None:
        """Set `updated_at` property to current time if property exists

        Args:
            obj (ModelType): Object instance
        """

        if hasattr(element, "updated_at"):
            setattr(element, "updated_at", datetime.utcnow())

    async def _save(self, db: AsyncSession, element: ModelType) -> ModelType:
        """_save an object into database

        Args:
            db (AsyncSession): Async db session
            element (ModelType): ModelType instance to _save

        Returns:
            ModelType: _saved object instance
        """

        # set updated_at
        self._set_updated_at(element)

        # add, commit and refresh
        db.add(element)
        await db.commit()
        await db.refresh(element)

        # return instance
        return element

    async def _save_all(
        self, db: AsyncSession, elements: Iterable[ModelType]
    ) -> Iterable[ModelType]:
        """_save an iterable of elements into database

        Args:
            db (AsyncSession): Async db session
            elements (Iterable[ModelType]): Iterable of ModelType instance to _save

        Returns:
            Iterable[ModelType]: Iterable of ModelType instance
        """

        # set updated_at
        _ = list(map(self._set_updated_at, elements))

        # add, commit and refresh
        db.add_all(elements)
        await db.commit()
        for element in elements:
            await db.refresh(element)

        # return instances
        return elements

    async def create(
        self, db: AsyncSession, element: CreateSchemaType
    ) -> ModelType:
        """Create an item into database

        Args:
            db (AsyncSession): Async db session
            element (CreateSchemaType): Schema to create

        Raises:
            CreateException: if item already exists or unexpected error

        Returns:
            ModelType: Instance of created object
        """

        try:
            # try json encode
            db_obj = self.model(**element.model_dump(mode="json"))
            return await self._save(db=db, element=db_obj)

        except IntegrityError:
            raise CreateException(f"{self.model.__name__} already exists.")

    async def bulk_create(
        self, db: AsyncSession, elements: Iterable[CreateSchemaType]
    ) -> Iterable[ModelType]:
        """Create items into database

        Args:
            db (AsyncSession): Async db session
            data (Iterable[CreateSchemaType]): Iterable of Schema to create

        Raises:
            CreateException: if an item already exists or unexpected error

        Returns:
            Iterable[ModelType]: Iterable of Instance of created object
        """

        try:
            # try json encode
            db_objs = [
                self.model(**d.model_dump(mode="python")) for d in elements
            ]
            return await self._save_all(db=db, elements=db_objs)

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
            data (Union[UpdateSchemaType, Dict[str, Any]]):
                New partial or full data for database item

        Returns:
            ModelType: Instance of updated object
        """

        # obj to dict
        if isinstance(data, dict):
            update_data = data
        else:
            update_data = data.model_dump(exclude_unset=True)

        # update obj with each field of obj
        for field, value in update_data.items():
            setattr(obj, field, value)

        return await self._save(db=db, element=obj)

    async def delete(self, db: AsyncSession, uid: UUID) -> ModelType:
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
