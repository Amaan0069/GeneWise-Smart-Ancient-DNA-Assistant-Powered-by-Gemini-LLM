from pydantic import BaseModel

class SampleData(BaseModel):
    id: str
    region: str
    age: int
    seed: str
