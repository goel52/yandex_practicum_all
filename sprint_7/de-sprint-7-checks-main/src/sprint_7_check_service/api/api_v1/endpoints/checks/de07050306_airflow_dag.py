from fastapi import APIRouter, Depends
from pyspark.sql import SparkSession

from sprint_7_check_service.api.dependency_config import DependencyConfig
from sprint_7_check_service.lessons.data_preparation_and_lake_filling.user_portrait.airflow_dag import \
    AirflowDag as Sp7Checker  # noqa
from sprint_7_check_service.lessons.data_preparation_and_lake_filling.updating_the_tag_directory.dag_joba_find_new_tags import \
    DagJobBashOperator  # noqa
from sprint_7_check_service.lessons.pyspark_for_data_engineer.job_automation.job_bash_operator import \
    JobBashOperator  # noqa

from .checks_dto import CheckRequest, CheckResponse

router = APIRouter()


def default_msg(code: str) -> str:
    return f"Задание выполнено. Ваш код: {code}"


@router.post("/", response_model=CheckResponse)
def read_items(
    request: CheckRequest
) -> CheckResponse:

    checker = JobBashOperator()

    status, message = checker.check(request.student_solution)
    if not status:
        return CheckResponse(
            status='error',
            message=message
        )

    checker = DagJobBashOperator()
    status, message = checker.check(request.student_solution)

    if not status:
        return CheckResponse(
            status='error',
            message=message
        )

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
