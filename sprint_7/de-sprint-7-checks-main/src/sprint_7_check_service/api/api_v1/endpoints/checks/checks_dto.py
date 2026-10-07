from pydantic import BaseModel


class CheckRequest(BaseModel):
    student_id: str
    student_solution: str


class CheckResponse(BaseModel):
    status: str
    message: str
