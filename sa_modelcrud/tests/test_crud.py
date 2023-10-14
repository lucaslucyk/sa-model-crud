import os
from pathlib import Path
import unittest
from uuid import uuid1

from ..models import ModelBase
from ..exceptions.crud import NotFoundException
from .schemas import SampleCreate, SampleUpdate
from .models import Sample
from .session import AsyncSessionLocal, engine
from .crud import samples
from .config import DB_NAME


class TestCRUD(unittest.IsolatedAsyncioTestCase):
    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()
        cls.db_path = Path(__file__).absolute().parent.parent.parent / DB_NAME
        if cls.db_path.is_file():
            os.remove(cls.db_path)
        ModelBase.metadata.create_all(bind=engine)

    @classmethod
    def tearDownClass(cls) -> None:
        ModelBase.metadata.drop_all(bind=engine)
        if cls.db_path.is_file():
            os.remove(cls.db_path)
        super().tearDownClass()

    async def test_00_create(self) -> None:
        async with AsyncSessionLocal() as db:
            sample_create = SampleCreate(token="fake-token")
            sample_obj = await samples.create(db=db, element=sample_create)

            assert isinstance(sample_obj, Sample)
            assert sample_obj.token == sample_create.token

    async def test_01_bulk_create(self) -> None:
        async with AsyncSessionLocal() as db:
            sample_2 = SampleCreate(token="fake-token-2")
            sample_3 = SampleCreate(token="fake-token-3")

            sample_2_db, sample_3_db = await samples.bulk_create(
                db=db, elements=(sample_2, sample_3)
            )
            assert isinstance(sample_2_db, Sample)
            assert isinstance(sample_3_db, Sample)
            assert sample_2_db.token == sample_2.token
            assert sample_3_db.token == sample_3.token

    
    async def test_02_list(self) -> None:
        async with AsyncSessionLocal() as db:
            all_ = await samples.list(db=db)
            assert len(all_) > 0

            limited = await samples.list(db=db, limit=1)
            assert len(limited) == 1

            skipped = await samples.list(db=db, skip=1)
            assert len(skipped) < len(all_)


    # async def test_03_get(self) -> None:
    #     async with AsyncSessionLocal() as db:

    #         sample = await samples.get(db=db, uid=self.sample_1.uid)
    #         sample_2 = await samples.get_or_raise(db=db, uid=self.sample_2.uid)
    #         assert sample.id == self.sample_1.id
    #         assert sample_2.id == self.sample_2.id

    #         with self.assertRaises(NotFoundException):
    #             samples.get_or_raise(db=db, uid=uuid1())
