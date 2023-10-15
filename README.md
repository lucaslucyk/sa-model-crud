# SQLAlchemy Model CRUD
Base CRUD manager to manage databases with asynchronous SQLAlchemy sessions.


- Repository: [https://github.com/lucaslucyk/sa-model-crud](https://github.com/lucaslucyk/sa-model-crud)
- PyPi: [https://pypi.org/project/sa-modelcrud](https://pypi.org/project/sa-modelcrud)
- Documentation: Coming soon.


## Project Status
⚠️ **_Warning_**: This project is currently in __*development phase*__.

This project is in an early stage of development and may contain bugs. It is not recommended for use in production environments.


## Requirements
Python 3.8+

SQLAlchemy Model CRUD stands on the soulders of giants:
- [SQLAlchemy](https://www.sqlalchemy.org/) for the database parts.
- [Pydantic](https://docs.pydantic.dev) for the data parts.


## Installation
```bash
$  pip install sa-modelcrud
```

## Example

### Database Model prepare
- Create a database model with:

```python
from uuid import uuid1, UUID
from sqlalchemy.orm import Mapped, mapped_column
from sa_modelcrud.models import ModelBase, Timestamp


class Sample(Timestamp, ModelBase):
    # ModelBase contains id and uid properties
    email: Mapped[str] = mapped_column(nullable=True, unique=True)
```

### Create schemas

```python
from typing import Optional
from uuid import UUID
from pydantic import BaseModel


class SampleBase(BaseModel):
    id: Optional[int] = None
    uid: Optional[UUID] = None
    email: Optional[str] = None

class SampleCreate(SampleBase):
    ...

class SampleUpdate(SampleBase):
    ...
```

### Create CRUD

```python
from sa_modelcrud import CRUDBase


class CRUDSample(CRUDBase[Sample, SampleCreate, SampleUpdate]):
    ...


samples = CRUDSample(Sample)
```


### Create session

```python
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    create_async_engine,
    async_sessionmaker
)


DB_URI = "sqlite+aiosqlite:///./db.sqlite3"

async_engine: AsyncEngine = create_async_engine(
    DB_URI,
    future=True,
    connect_args={"check_same_thread": False}
)

AsyncSessionLocal: AsyncSession = async_sessionmaker(
    bind=async_engine,
    class_=AsyncSession,
    expire_on_commit=False
)
```

### Use the CRUD

```python
async with AsyncSessionLocal() as db:
    data = SampleCreate(email="sample@fakedomain.com")

    # save data into database
    sample_obj = await samples.create(db=db, element=data)
```



## General CRUD Methods

All inherited CRUDBase instances have the following methods:

- `.get(...)`: Get row from model by uid.
- `.get_or_raise(...)`: Try to get row from model by uid. Raise if not object found.
- `.list(...)`: Get multi items from database.
- `.filter(...)`: Get items from database using `whereclause` to filter.
- `.find(..., **kwargs)`: Find elements with kwargs.
- `.find_one(..., **kwargs)`: Find an element with kwargs.
- `.save(...)`: Save an object into database.
- `.save_all(...)`: Save an iterable of elements into database.
- `.create(...)`: Create an item into database.
- `.bulk_create(...)`: Create items into database.
- `.update(...)`: Update a database item with an update schema.
- `.delete(...)`: Delete an item from database.


## Contributions and Feedback
I would love to receive contributions and feedback! If you'd like to get involved, please contact me through one of the contact methods in my [Profile](https://github.com/lucaslucyk).


## License
This project is licensed under the terms of the MIT license.