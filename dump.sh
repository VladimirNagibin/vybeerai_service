#!/bin/bash

FILENAME="dump-$(date +"%Y-%m-%d").zip"
FILEPATH="/home/bob140/Dev/vybeerai_service/$FILENAME"
TOKEN='y0_AgAAAABxfcwdAAzevwAAAAEagRmaAAA_6r43ge9PDq806PXsaTtWASxuEQ'
FILE="dump.sql"
POSTGRES_USER='django_user'
POSTGRES_PASSWORD='mysecretpassword'
POSTGRES_DB='django'

sudo docker exec -i vybeerai_service-db-1 /bin/bash -c "PGPASSWORD=$POSTGRES_PASSWORD pg_dump --username $POSTGRES_USER $POSTGRES_DB" > "/home/bob140/Dev/vybeerai_service/$FILE"
zip -r $FILENAME "/home/bob140/Dev/vybeerai_service/$FILE"

# Простая функция для парсинга свойств из JSON
function parseJson()
{
    local output
    regex="(\"$1\":[\"]?)([^\",\}]+)([\"]?)"
    [[ $2 =~ $regex ]] && output=${BASH_REMATCH[2]}
    echo $output
}

# Функция для отправки файла
function sendFile
{
    echo "Start sending a file: $1"

    # Получаем URL для загрузки файла
    sendUrlResponse=`curl -s -H "Authorization: OAuth $TOKEN" https://cloud-api.yandex.net:443/v1/disk/resources/upload/?path=app:/$FILENAME&overwrite=true`
    sendUrl=$(parseJson 'href' $sendUrlResponse)

    # Отправляем файл
    sendFileResponse=`curl -s -T $FILEPATH -H "Authorization: OAuth $TOKEN" $sendUrl`

    echo "Completing a file upload: $1"
}

sendFile $FILEPATH

rm "/home/bob140/Dev/vybeerai_service/$FILE"
rm $FILEPATH

