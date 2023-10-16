import unittest

from ..crud.base import CRUDBase
from .models import Sample
from .schemas import SampleCreate, SampleUpdate
from .crud import samples


class CRUDSampleError(CRUDBase[Sample, SampleCreate, SampleUpdate]):
    ...


class TestCRUD(unittest.TestCase):
    def test_no_model(self) -> None:

        with self.assertRaises(TypeError):
            CRUDSampleError()

    def test_model(self) -> None:
        self.assertTrue(hasattr(samples, "model"))
        self.assertEqual(samples.model, Sample)

        # create an instance from property
        sm = samples.model(email="sample@sample")
        self.assertIsInstance(sm, Sample)
