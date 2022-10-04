#!/bin/bash

ZIP_FUNCTION_FILE="./.deploy.zip"

FUNCTION_NAME=imap-mail
# имя функции

ENTRYPOINT=main.handler
# обработчик, указывается в формате файла с функцией обработчика <имя >.<имя >

RUNTIME=python38
# среда выполнения

MEMORY=128m
# объем RAM

TIMEOUT=60s
# максимальное время выполнения функции до таймаута

# lockbox
function lockbox() { yc lockbox payload get "${1}" --key "${2}"; }

# https://crontab.guru
TIMER_CRONTAB="*/5 * ? * * *"

TELEGRAM_TOKEN=$(lockbox ${FUNCTION_NAME} TELEGRAM_TOKEN)
TELEGRAM_CHAT_ID=$(lockbox ${FUNCTION_NAME} TELEGRAM_CHAT_ID)

IMAP_SERVER=$(lockbox ${FUNCTION_NAME} IMAP_SERVER)
IMAP_USER=$(lockbox ${FUNCTION_NAME} IMAP_USER)
IMAP_PASSWORD=$(lockbox ${FUNCTION_NAME} IMAP_PASSWORD)

rm -rf "${ZIP_FUNCTION_FILE}"

zip -r "${ZIP_FUNCTION_FILE}" ./ -x "deploy.sh" -x "README.md"

yc serverless function create "${FUNCTION_NAME}"
yc serverless function allow-unauthenticated-invoke "${FUNCTION_NAME}"
yc serverless function version create \
    --function-name=${FUNCTION_NAME} \
    --runtime ${RUNTIME} \
    --entrypoint ${ENTRYPOINT} \
    --memory ${MEMORY} \
    --execution-timeout ${TIMEOUT} \
    --environment "TELEGRAM_TOKEN=${TELEGRAM_TOKEN}" \
    --environment "TELEGRAM_CHAT_ID=${TELEGRAM_CHAT_ID}" \
    --environment "IMAP_SERVER=${IMAP_SERVER}" \
    --environment "IMAP_USER=${IMAP_USER}" \
    --environment "IMAP_PASSWORD=${IMAP_PASSWORD}" \
    --source-path "${ZIP_FUNCTION_FILE}" | # zip-архив c кодом функции и всеми необходимыми зависимостями
    sed '1,/environment:/!d'               # очистка environment переменных при выводе

rm -rf "${ZIP_FUNCTION_FILE}"

YC_FUNCTION_ID=$(yc serverless function get "${FUNCTION_NAME}" --format json | jq -r '.id')

yc serverless trigger delete "cron-${FUNCTION_NAME}"
yc serverless trigger create timer "cron-${FUNCTION_NAME}" --cron-expression "${TIMER_CRONTAB}" --invoke-function-id "${YC_FUNCTION_ID}"

if [ ! -z "${YC_FUNCTION_ID}" ]; then
    YC_FUNCTION_ENDPOINT="https://functions.yandexcloud.net/${YC_FUNCTION_ID}"

    curl -s https://api.telegram.org/bot${TELEGRAM_TOKEN}/setWebhook?url=${YC_FUNCTION_ENDPOINT}
fi
