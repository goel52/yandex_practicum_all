# de-sprint-7-checks

Единый сервис проверок `sprint_7_check_service`.

## API

Корень маршрутов — `/api/v1/checks`. Для каждого задания предусмотрен
`POST /api/v1/checks/<зарегистрированное_имя>/` с JSON:

```json
{"student_id": "учебный-логин", "student_solution": "текст решения"}
```

Ответ успешной проверки имеет `status: "success"` и `message` с сообщением
и секретным кодом для платформы. При ошибке решения возвращаются HTTP 200,
`status: "error"` и пояснение в `message`. Отдельного поля для кода нет.
Неполный запрос даёт HTTP 422, неподдерживаемый метод — HTTP 405.

Маршруты определены в `src/sprint_7_check_service/api/api_v1/endpoints/checks_api.py`.
Историческое имя `/de07040603_union_by_name/` относится к `join_title` и сохранено.
Для `de07050401` предусмотрен
`POST /api/v1/checks/de07050401_connection_interests/`.
В `student_solution` передаётся JSON-строка с тремя ключами:
`connection_interests.py`, `run_jobs.sh`, `dag.py`; значения — содержимое файлов.
[Контракт и ограничения новой проверки](docs/de07050401.md).

## Локальная проверка

Целевой контейнер: Python 3.10, Java 8, PySpark 3.3.2 (как в
`[de-spark/sprint-7-builder/src/image/sp7/sp7infra/jupyter](https://practicum.gitlab.yandexcloud.net/faculties/data-engineer/de-spark/-/tree/master/sprint-7-builder/src/image/sp7/sp7infra/jupyter?ref_type=heads)`).
NumPy 1.24.4 и PyArrow 7.0.0 закреплены по тому же образцу.
Для локального запуска используйте Python 3.10 и JDK 8.

Установите зависимости из `src/requirements.txt` в виртуальное окружение.
Для полного набора тестов нужны JDK и возможность открыть локальные сокеты.
Spark запускается лениво при обращении к DataFrame-проверкам; Airflow и HDFS для этих тестов
не требуются, данные Spark формируются локально.

Из корня этого репозитория, с активированным окружением и `JAVA_HOME`,
указывающим на JDK 8:

```bash
SPARK_LOCAL_IP=127.0.0.1 PYSPARK_PYTHON="$(command -v python)" PYTHONPATH=src python -m pytest -q
```

Проверки без запуска JVM (авторские решения для текстовых/AST-проверок и регрессии):

```bash
PYTHONPATH=src python -m pytest tests/unit -q
```

Полный набор включает API-тесты для шести маршрутов с операциями DataFrame,
которые намеренно отсутствуют в `tests/unit/test_author_checks.py`.
Параметр `spark=None` используется в unit-тестах только там, где старый
аргумент присутствует в сигнатуре, но не используется в реализации.

Тесты показывают прохождение авторских решений и проверяют конкретные ошибки.
Они не подтверждают выполнение DAG в Airflow или корректность расчётов
на полном учебном HDFS. Покрытие части заданий пока ограничено поиском
фрагментов текста или анализом отдельных узлов AST; миграционный отчёт
в общей рабочей области перечисляет эти ограничения по заданиям.

Проверка `de07050401` использует только AST: не исполняет джобу и не требует JVM.
Её отдельный набор запускается по команде из [документации](docs/de07050401.md).

## Docker, Helm и GitLab CI/CD

Конфигурация повторяет схему `de-start-checks`: сборка `linux/amd64` через
Docker Buildx, registry cache, передача тега через dotenv и автоматический
`helm upgrade --install --atomic --wait --timeout 10m`.

Pipeline запускается только для тегов `de-sprint-7-checks` или
`de-sprint-7-checks-*`, например `de-sprint-7-checks-v1.0.0`:

1. `validate_helm` — lint и рендеринг chart.
2. `build_image` — сборка стадии `test` и полный pytest внутри целевого
   контейнера, затем публикация production-образа без каталога тестов.
3. `deploy` — проверка доступа к namespace и установка Helm release.
   Деплои сериализованы через `resource_group`; при ошибке Helm откатывает релиз.

Параметры по умолчанию:

| Параметр | Значение |
| --- | --- |
| Registry repository | `cr.yandex/crprrfjafjnhr7os2f25/de_sprint_7_checks` |
| Helm release | `de-sprint-7-checks` |
| Namespace | `sprints-infra` |
| Kubernetes context в CI | `current-context` из переданного kubeconfig |
| YC CLI profile в CI | `data-engineer-sa` |
| Домен | `de-sp7-checks.de.education-services.ru` |
| Порт контейнера | `8000` |

В GitLab нужны CI/CD variables типа **Variable**, по аналогии с исходным сервисом:

- `YC_SA_KEY` — JSON авторизованного ключа сервисного аккаунта с правом
  публикации образов в registry; защищённая переменная.
- `KUBECONFIG_B64_SA_DEPLOY_SPRINTS_INFRA` — kubeconfig в base64 с выбранным
  `current-context` целевого кластера и правами на Helm release, Deployment, Service,
  ConfigMap и Ingress в `sprints-infra`; защищённая переменная.

Имя контекста в CI kubeconfig может отличаться от локального
`yc-k8s-de-cluster`: pipeline использует выбранный в нём `current-context`
и выводит его перед проверкой доступа. Для локальных команд по-прежнему
используется `yc-k8s-de-cluster`.

Теги запуска должны быть protected, чтобы получать protected variables.
Runner должен поддерживать privileged Docker-in-Docker и иметь сетевой доступ
к registry и API Kubernetes. Namespace должен существовать заранее.
Узлам нужен доступ на скачивание образов; при необходимости задайте
`imagePullSecrets` в Helm values. Секреты приложения и доступ к БД не требуются.

DNS домена должен указывать на nginx ingress controller. TLS настроен так же,
как в `de-start-checks`: используется сертификат контроллера по умолчанию.
Он должен покрывать этот домен. Для отдельного сертификата chart поддерживает
`ingress.tls[].secretName`. DNS и сертификаты pipeline не создаёт.
`INGRESS_HOST` позволяет переопределить домен в CI.

Контейнер запускает один worker Uvicorn и локальный Spark JVM; HDFS/YARN
не требуются. Начальные ресурсы: request 500m CPU / 1536Mi RAM,
limit 2 CPU / 3Gi RAM, heap Spark 1g. Их следует уточнить по нагрузке.
Liveness/readiness/startup проверяют `GET /api/v1/health/healthcheck`.
Маршрут проверяет HTTP-процесс и не запускает Spark; DataFrame-проверки
проверяются полным pytest при сборке. Изменение ConfigMap перезапускает pod
через checksum аннотацию.

Локальная проверка из корня репозитория:

```bash
helm lint helm --strict --set-string image.tag=local
helm template de-sprint-7-checks helm --namespace sprints-infra --set-string image.tag=local
docker build --platform linux/amd64 -f dockerfile --target test .
docker build --platform linux/amd64 -f dockerfile -t de-sprint-7-checks:local .
docker run --rm -p 8000:8000 de-sprint-7-checks:local
```

Chart требует явный `image.tag`; pipeline подставляет тег вида
`vYYYY-MM-DD-r<CI_PIPELINE_IID>`.
