import os
from pathlib import Path
import unittest
from uuid import uuid1
from sqlalchemy.sql import text
from ..models import ModelBase
from ..exceptions.crud import NotFoundException, CreateException
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

    async def test_create(self) -> None:
        async with AsyncSessionLocal() as db:
            email = "fake-create@fakedomain.com"
            sample_create = SampleCreate(email=email, token="fake-token-1")
            sample_obj = await samples.create(db=db, element=sample_create)

            self.assertIsInstance(sample_obj, Sample)
            self.assertEqual(sample_obj.token, sample_create.token)

            # create with raise
            with self.assertRaises(CreateException):
                error = SampleCreate(email=email)
                await samples.create(db=db, element=error)

    async def test_bulk_create(self) -> None:
        async with AsyncSessionLocal() as db:
            email = "fake-bulk-create@fakedomain.com"
            sample_2 = SampleCreate(
                email=email, token="fake-token-2", describe="text"
            )
            sample_3 = SampleCreate(token="fake-token-3", describe="text")

            sample_2_db, sample_3_db = await samples.bulk_create(
                db=db, elements=(sample_2, sample_3)
            )
            self.assertIsInstance(sample_2_db, Sample)
            self.assertIsInstance(sample_3_db, Sample)
            self.assertEqual(sample_2_db.token, sample_2.token)
            self.assertEqual(sample_3_db.token, sample_3.token)

            # create with raise
            with self.assertRaises(CreateException):
                s = SampleCreate(describe="text-ok")
                error = SampleCreate(email=email)
                await samples.bulk_create(db=db, elements=(s, error))

    async def test_list(self) -> None:
        async with AsyncSessionLocal() as db:
            all_ = await samples.list(db=db)
            self.assertGreater(len(all_), 0, "DB items were expected")
            for obj in all_:
                self.assertIsInstance(obj, Sample)

            limited = await samples.list(db=db, limit=1)
            self.assertEqual(len(limited), 1)

            skipped = await samples.list(db=db, offset=1)
            self.assertLess(len(skipped), len(all_))

    async def test_filter(self) -> None:
        async with AsyncSessionLocal() as db:
            single = await samples.filter(
                db=db, whereclause=samples.model.token == "fake-token-1"
            )
            self.assertEqual(len(single), 1, "One single item was expected")
            self.assertIsInstance(single[0], Sample)

            wc = text("token LIKE '%fake%'")
            multi = await samples.filter(db=db, whereclause=wc)
            self.assertGreater(len(multi), 1)
            for obj in multi:
                self.assertIsInstance(obj, Sample)

            skipped_limited = await samples.filter(
                db=db, whereclause=wc, offset=1, limit=1
            )
            self.assertEqual(len(skipped_limited), 1)

    async def test_find(self) -> None:
        async with AsyncSessionLocal() as db:
            single = await samples.find(db=db, token="fake-token-1")
            self.assertEqual(len(single), 1, "One single item was expected")
            self.assertIsInstance(single[0], Sample)

            multi = await samples.find(db=db, describe="text")
            self.assertGreater(len(multi), 1)
            for obj in multi:
                self.assertIsInstance(obj, Sample)

            limited = await samples.find(db=db, describe="text", limit=1)
            self.assertEqual(len(limited), 1, "One single item was expected")

            skipped = await samples.find(db=db, describe="text", offset=1)
            self.assertEqual(len(skipped), 1, "One single item was expected")

            not_found = await samples.find(db=db, describe="not-found")
            self.assertEqual(len(not_found), 0)

            skip_all = await samples.find(db=db, describe="text", offset=5)
            self.assertEqual(len(skip_all), 0)

    async def test_find_one(self) -> None:
        async with AsyncSessionLocal() as db:
            # unique with some data
            unique = await samples.find_one(db=db, describe=None)
            self.assertIsInstance(unique, Sample)

            # first of multi
            multi = await samples.find_one(db=db, describe="text")
            self.assertIsInstance(multi, Sample)

            # first of db
            empty = await samples.find_one(db=db)
            self.assertIsInstance(empty, Sample)

            # not found data
            not_found = await samples.find_one(db=db, describe="not-found")
            self.assertIsNone(not_found)

    async def test_get(self) -> None:
        async with AsyncSessionLocal() as db:
            # get all samples
            all_samples = await samples.list(db=db)

            sample = await samples.get(db=db, id=all_samples[0].id)
            self.assertIsInstance(sample, Sample)
            self.assertEqual(sample.id, all_samples[0].id)

            # not found
            empty = await samples.get(db=db, id=uuid1())
            self.assertIsNone(empty)

    async def test_get_or_raise(self) -> None:
        async with AsyncSessionLocal() as db:
            # get all samples
            all_samples = await samples.list(db=db, offset=1, limit=1)

            # with raise
            sample = await samples.get_or_raise(db=db, id=all_samples[0].id)
            self.assertIsInstance(sample, Sample)
            self.assertEqual(sample.id, all_samples[0].id)

            # not found with raise
            with self.assertRaises(NotFoundException):
                await samples.get_or_raise(db=db, id=uuid1())

    async def test_save(self) -> None:
        async with AsyncSessionLocal() as db:
            # get element
            obj = await samples.find_one(db=db, describe=None)
            updated_at = obj.updated_at
            id = obj.id
            id_ = obj.id

            # update and save
            obj.describe = "test-save"
            obj = await samples._save(db=db, element=obj)
            self.assertEqual(obj.describe, "test-save")

            self.assertNotEqual(updated_at, obj.updated_at)
            self.assertNotEqual(obj.created_at, obj.updated_at)
            self.assertEqual(id, obj.id)
            self.assertEqual(id_, obj.id)

    async def test_save_all(self) -> None:
        async with AsyncSessionLocal() as db:
            # get element
            objs = await samples.find(db=db, describe="text")
            updateds = [obj.updated_at for obj in objs]
            ids = [obj.id for obj in objs]
            ids = [obj.id for obj in objs]

            # update and save
            for obj in objs:
                obj.describe = "test-save-all"

            # save
            objs = await samples._save_all(db=db, elements=objs)

            # check updated
            for obj in objs:
                self.assertEqual(obj.describe, "test-save-all")

            updateds_ = [obj.updated_at for obj in objs]
            ids_ = [obj.id for obj in objs]
            ids_ = [obj.id for obj in objs]

            self.assertNotEqual(updateds, updateds_)
            self.assertEqual(ids, ids_)
            self.assertEqual(ids, ids_)

    async def test_update(self) -> None:
        async with AsyncSessionLocal() as db:
            sample = SampleCreate(describe="test-update")
            obj = await samples.create(db=db, element=sample)
            updated_ = obj.updated_at
            id = obj.id

            data = SampleUpdate(describe="test-update")
            obj = await samples.update(db=db, obj=obj, data=data)

            self.assertEqual(obj.describe, "test-update")
            self.assertEqual(obj.id, id)
            self.assertNotEqual(obj.updated_at, updated_)

            obj = await samples.update(
                db=db, obj=obj, data={"describe": "test-update-2"}
            )
            self.assertEqual(obj.describe, "test-update-2")

    async def test_delete(self) -> None:
        async with AsyncSessionLocal() as db:
            sample = SampleCreate(describe="for-test-delete")
            obj = await samples.create(db=db, element=sample)

            deleted = await samples.delete(db=db, id=obj.id)
            self.assertEqual(obj, deleted)

            not_found = await samples.find_one(
                db=db, describe="for-test-delete"
            )
            self.assertIsNone(not_found)
