curl -X POST https://order-gen-service.de.education-services.ru/delete_kafka  \
-H 'Content-Type: application/json; charset=utf-8' \
--data-binary @- << EOF
{
    "student": "goel52"
}
EOF

#перепиши вот так:
#curl -X POST -H "Content-Type: application/json" -d "{\"student\":\"goel52\"}"  https://order-gen-service.sprint9.tgcloudenv.ru/delete_kafka