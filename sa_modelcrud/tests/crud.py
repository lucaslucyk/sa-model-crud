from ..crud import CRUDBase
from .models import Sample as SampleModel
from .schemas import SampleCreate, SampleUpdate



class CRUDSample(CRUDBase[SampleModel, SampleCreate, SampleUpdate]):
    model = SampleModel


samples = CRUDSample()