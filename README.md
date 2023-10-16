# SQLAlchemy Model CRUD
Model CRUD manager to handle databases with asynchronous SQLAlchemy sessions.


- Source code: [https://github.com/lucaslucyk/sa-model-crud](https://github.com/lucaslucyk/sa-model-crud)
- Package: [https://pypi.org/project/sa-modelcrud](https://pypi.org/project/sa-modelcrud)
- Documentation: Coming soon.


## Project Status
⚠️ **_Warning_**: This project is currently in __*development phase*__.

This project is in an early stage of development and may contain bugs. It is not recommended for use in production environments.


## Why use `sa_crudmodel`?

- 🚀 __Fast to code__: Increase the speed to develop integrations features.
- ❌ __Fewer bugs__: Reduce human (developer) induced errors.
- 💡 __Intuitive__: Great editor support. Completion everywhere. Less time debugging.
- 🤓 __Easy__: Designed to be easy to use and learn. Less time reading docs.
- 〽️  __Short__: Minimize code duplication. Multiple features from each parameter declaration. Fewer bugs.


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
    model = Sample


samples = CRUDSample()
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
    data = SampleCreate(email="sample@sample")

    # save data into database
    sample_obj = await samples.create(db=db, element=data)
```



## General CRUD Methods

All inherited CRUDBase instances have the following methods:

- `.get(..., uid)`: Get row from model by uid.
- `.get_or_raise(..., uid)`: Try to get row from model by uid. Raise if not object found.
- `.list(...)`: Get multi items from database.
- `.filter(..., whereclause)`: Get items from database using `whereclause` to filter.
- `.find(..., **kwargs)`: Find elements with kwargs.
- `.find_one(..., **kwargs)`: Find an element with kwargs.
- `.create(..., element)`: Create an element into database.
- `.bulk_create(..., elements)`: Create elements into database.
- `.update(..., obj, data)`: Update a database obj with an update data schema.
- `.delete(..., uid)`: Delete an item from database.


## TODO:
- [ ] Paginate results of methods `list`, `filter` and `find`.
- [ ] Add default values for `offset` and `limit` on paginated methods.
- [ ] Add support for Sync Sessions.
- [ ] Create complete documentation in [Readthedocs](https://about.readthedocs.com/).

## Contributions and Feedback
I would love to receive contributions and feedback! If you'd like to get involved, please contact me through one of the contact methods in my [Profile](https://github.com/lucaslucyk).


## License
This project is licensed under the terms of the MIT license.