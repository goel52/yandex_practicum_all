from fastapi import APIRouter, Depends
from pyspark.sql import SparkSession

from sprint_7_check_service.api.dependency_config import DependencyConfig
from sprint_7_check_service.lessons.data_preparation_and_lake_filling.user_portrait.calculate_user_interests import \
    CalculateUserInterests as Sp7Checker  # noqa

from .checks_dto import CheckRequest, CheckResponse

router = APIRouter()


def default_msg(code: str) -> str:
    return f"Задание выполнено. Ваш код: {code}"


@router.post("/", response_model=CheckResponse)
def read_items(
    request: CheckRequest,
    spark: SparkSession = Depends(DependencyConfig.spark_reaction_tag_tops)
) -> CheckResponse:

    checker = Sp7Checker()

    status, message = checker.check(request.student_solution, spark)
    if not status:
        return CheckResponse(
            status='error',
            message=message
        )

    return CheckResponse(
        status="success",
        message=default_msg(checker.RESPONSE_KEY))
