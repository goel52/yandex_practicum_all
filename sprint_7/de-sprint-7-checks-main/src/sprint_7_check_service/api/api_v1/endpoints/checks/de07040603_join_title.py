from fastapi import APIRouter

from sprint_7_check_service.lessons.pyspark_for_data_engineer.join_union.join_title import \
    JoinTitle as Sp7Checker  # noqa

from .checks_dto import CheckRequest, CheckResponse

router = APIRouter()


def default_msg(code: str) -> str:
    return f"Задание выполнено. Ваш код: {code}"


@router.post("/", response_model=CheckResponse)
def read_items(
    request: CheckRequest
) -> CheckResponse:

    checker = Sp7Checker()

    status, message = checker.check(request.student_solution)
    if not status:
        return CheckResponse(
            status='error',
            message=message
        )

    return CheckResponse(
        status="success",
        message=default_msg(checker.RESPONSE_KEY))
