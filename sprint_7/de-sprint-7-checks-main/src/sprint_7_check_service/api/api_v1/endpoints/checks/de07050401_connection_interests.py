from fastapi import APIRouter

from sprint_7_check_service.lessons.data_preparation_and_lake_filling.contact_portrait.connection_interests import ConnectionInterests
from .checks_dto import CheckRequest, CheckResponse

router = APIRouter()


@router.post("/", response_model=CheckResponse)
def read_items(request: CheckRequest) -> CheckResponse:
    checker = ConnectionInterests()
    status, message = checker.check(request.student_solution)
    if not status:
        return CheckResponse(status='error', message=message)
    return CheckResponse(status='success',
                         message=f'Задание выполнено. Ваш код: {checker.RESPONSE_KEY}')
