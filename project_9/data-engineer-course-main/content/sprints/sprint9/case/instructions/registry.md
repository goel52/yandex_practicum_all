0. export KUBECONFIG=~/Downloads/config.de

1. Создать registry через UI консоли.

2. Выдать роли container-registry.images.puller и container-registry.images.pusher

3. Собрать docker image для registry: `docker build . -t cr.yandex/crprrfjafjnhr7os2f25/sample_app:latest`
3. Собрать docker image для registry: `docker build . -t cr.yandex/crpe7gmtkh8el8rkf2ub/de_cloudtech_demo_service:latest`
3. Собрать docker image для registry: `docker build . -t cr.yandex/crprrfjafjnhr7os2f25/redis_data_service:v2023-02-25-r1`
3. Собрать docker image для registry: `docker build . -t cr.yandex/crprrfjafjnhr7os2f25/postgres_check_service:v2023-09-09-r1`
3. Собрать docker image для registry: `docker build . -t cr.yandex/crprrfjafjnhr7os2f25/order_gen_service:v2023-04-01-r1`

4. Получить oauth-token: https://cloud.yandex.ru/docs/container-registry/operations/authentication#oauth (внутри ссылка "Получить токен")

5. Залогиниться в registry с токеном: `docker login --username oauth --password {здесь вставить токен} cr.yandex/crprrfjafjnhr7os2f25`


6. Запушить image: `docker push cr.yandex/crprrfjafjnhr7os2f25/sample_app:latest`
6. Запушить image: `docker push cr.yandex/crpe7gmtkh8el8rkf2ub/de_cloudtech_demo_service:latest`
6. Запушить image: `docker push cr.yandex/crprrfjafjnhr7os2f25/redis_data_service:v2023-02-25-r1`
6. Запушить image: `docker push cr.yandex/crprrfjafjnhr7os2f25/postgres_check_service:v2023-09-09-r1`
6. Запушить image: `docker push cr.yandex/crprrfjafjnhr7os2f25/order_gen_service:v2023-04-01-r1`

7. Открыть образ в консоли.

8. Прописать тег релиза в values.yaml.

9. `helm upgrade --install --atomic redis-data-service helm/app -n sprint9-infra`
9. `helm upgrade --install --atomic postgres-check-service helm/app -n sprint9-infra`
9. `helm upgrade --install --atomic order-gen-service helm/app -n sprint9-infra`
