# Telegram бот получения почтовый уведомлений по протоколу IMAP

## Настройка бота

1. Зарегистрировать в Yandex Cloud

2. Установить утилиту работы через командную строку `yc`, выполнить инициализацию через `yc init`

3. Завести переменные окружения через сервис секретов `Lockbox` [lockbox](https://cloud.yandex.ru/services/lockbox)

4. Выполнить развертывание через `bash`-скрипт: `deploy.sh`

## Настройка Yandex Почты

Включение доступа по IMAP
https://mail.yandex.ru/?dpda=yes#setup/client

Создание пароля приложения
https://id.yandex.ru/profile/apppasswords-list