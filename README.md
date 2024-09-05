[![ArbuzikAI deploy](https://github.com/seroburomalinoviy/arbuzikAIService/actions/workflows/deploy.yml/badge.svg)](https://github.com/seroburomalinoviy/arbuzikAIService/actions/workflows/deploy.yml)
# ArbuzikAiBot

---

# Развертка проекта в production

# Подготовка сервера

## Создание и настройка пользователя

1. Создаем любого пользователя отличного от root
    
    ```bash
    adduser --gecos "" ubuntu  # sudo adduser ubuntu
    usermod -aG sudo ubuntu
    su ubuntu
    ```
    
2. Закидываем в пользователя свой ssh ключ, на локальной машине выполняем:
    
    ```bash
    ssh-copy-id user@server-ip
    ```
    
3. Даем права чтение+запись+исполнение на ключи и чтение+запись на файл authorized_keys
    
    ```bash
    chmod 700 ~/.ssh/ -R
    chmod 600 ~/.ssh/authorized_keys
    ```
    
4. Изменить владение на текущего юзера
    
    ```bash
    chown -R ubuntu:ubuntu ~/.ssh
    ```
    
5. Создаем пользователя в котором будут хранится данные
    
    ```bash
    adduser --gecos "" postgres
    ```
    
6. Добавляем пользователю postgres группу docker
    
    ```bash
    sudo usermod -aG docker postgres
    ```
    

## Настройка безопасности сервера

1. Закрыть вход в root, открываем ssh config:
    
    ```bash
    sudo vi /etc/ssh/sshd_config
    ```
    
2. Находим настройку разрешения входа в root: PermitRootLogin, выставляем no
    
    ```bash
    PermitRootLogin no
    ```
    
3. Отключение входа на сервер по паролю (только ssh), в том же конфиге (осторожно!!!):
    
    ```bash
    PasswordAuthentication no
    ```
    
4. Изменим стандартный порт для ssh 
    
    ```bash
    Port 921
    ```
    
5. Перезагружаем ssh сервис 
    
    ```bash
    sudo service ssh restart
    ```
    
6. Скачаем браундмер
    
    ```bash
    sudo apt-get install -y ufw
    ```
    
7. Настроим браундмер, включим только следующие порты: 80 (http), 921 (ssh), 443 (https)
    
    ```bash
    sudo ufw allow 921/tcp
    sudo ufw allow http
    sudo ufw allow 443/tcp
    sudo ufw --force enable
    sudo ufw status
    ```
    

**Источники**: [https://habr.com/ru/articles/821757/](https://habr.com/ru/articles/821757/)

[https://habr.com/ru/companies/vdsina/articles/521388/](https://habr.com/ru/companies/vdsina/articles/521388/)

# Подготовка ssh ключей для ci/cd

## Связка Github → Server

1. Создаем пару ssh ключей в пользователе с методом rsa (из-за git actions)
    
    ```bash
    ssh-keygen -t rsa -b 4096 -f ~/.ssh/github-actions
    ```
    
2. Добавляем открыты ключ в `authorized_keys`
    
    ```bash
    cat ~/.ssh/github-actions.pub >> ~/.ssh/authorized_keys
    ```
    
3. Добавляем открытый ssh ключ на гитхаб в настройки проекта в раздел *deploy keys,* даем право write
4. На гитхаб в настройках в  *secrets* добавляем 3 переменных: хост сервера, приватный ssh ключ, имя юзера на сервере, порт где лежит репо
5. Обновляем имена секретов в workflow.yml в репе, если использованы другие

## Связка Репозиторий → Server

1. Добавить “`config`" в папку `.ssh`:
    
    ```bash
    Host github.com
        HostName github.com
        User git
        IdentityFile ~/.ssh/github-actions
        IdentitiesOnly yes
    ```

# Установка пакетов

`sudo apt update`

1. git: `sudo apt install git`
2. ~~git lfs:~~
    
    ```bash
    curl -s [https://packagecloud.io/install/repositories/github/git-lfs/script.deb.sh](https://packagecloud.io/install/repositories/github/git-lfs/script.deb.sh) | sudo bash
    sudo apt-get install git-lfs
    ```
    
3. docker (перед установкой проверить архитектуры ОС): 
    
    ```bash
    sudo apt install apt-transport-https ca-certificates curl software-properties-common
    curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo apt-key add -
    sudo add-apt-repository "deb [arch=amd64] https://download.docker.com/linux/ubuntu focal stable"
    apt-cache policy docker-ce
    sudo apt install docker-ce
    sudo systemctl status docker
    # для запуска docker без sudo (заработает после выхода/входа)
    sudo usermod -aG docker ${USER}
    ```
    
    **Источник**: [https://www.digitalocean.com/community/tutorials/how-to-install-and-use-docker-on-ubuntu-20-04](https://www.digitalocean.com/community/tutorials/how-to-install-and-use-docker-on-ubuntu-20-04)
    


# Загрузка проекта на сервер

1. Склонить проект через ssh
2. Для работы нейронки необходимы следующие файлы (pre-models):
    
    ```
    hubert_base.pt
    
    ./pretrained
    
    ./uvr5_weights
    ```
    
    1. Установить прогу для скачивания данных с huggingface
        
        ```bash
        sudo apt -y install -qq aria2
        ```
        
    2. Установить `make` для запуска скрипта
        
        ```bash
        sudo apt install make
        ```
        
    3. Запустить скрипт для скачки премоделей в `/client`
        
        ```bash
        make basev1
        ```
    
    Эти шаги исправляют ошибку:
    
   ```bash
    _pickle.UnpicklingError: invalid load key, 'v'
    ```

### Загрузка моделей из удаленного хранилища

1 Вариант:

Передача данных по ftp 

2 Вариант:

Github

### Копирование моделей в том

1. Получим наименование томов
    
    ```bash
    docker volume ls
    ```
    
2. Найдем путь до нужного тома с помощью 
    
    ```bash
    docker volume inspect *volume_name*
    ```
    
3. Скопируем содержимое папки с моделями в том
    
    ```bash
    cp -r models-backup/. var/lib/docker.../models-data-volume/_data
    ```
    


# Запуск проекта

1. Заполнить файл `.env`
2. Закинуть `.env` в проект на сервере
3. Склонить репо и создать все ветки в соответсвии с ci/cd.yml
4. Запуск проекта
    
    ```bash
    docker compose build
    docker compose up -d
    ```
    
5. Создать крон для скрипта бекапов бд. 
    1. Скопировать `backup.sh` и `.env` в корень пользователя `postgres` (делать с sudo, чтобы владельцем скрипта был root)
        
        ```bash
        sudo cp backup.sh .env /home/postgres
        ```
        
    2. Дать пользователю `postgres` владение дерикторией с бекапами: `backups/`
        
        ```bash
        chown postgres:postgres backups
        ```
    
    3. Открыть редактор крона из под `postgres`
    
       ```bash
       crontab -e -u postgres
       ```
    
    4. Создать расписание 
    
       ```bash
       3 0 * * * /home/postgres/backup.sh
       ```
    
    5. Логи выполненных задч
    
       ```bash
       sudo grep CRON /var/log/syslog
       ```
    

**Источники:** [https://www.dmosk.ru/miniinstruktions.php?mini=postgresql-dump&ysclid=lzmx2lecin857022537](https://www.dmosk.ru/miniinstruktions.php?mini=postgresql-dump&ysclid=lzmx2lecin857022537)

1. Создать администратора в админке
    1. На хосте:
        
        ```bash
        docker compose exec django bash
        ```
        
    2. В контейнере
        
        ```bash
        python manage.py createsuperuser
        ```
        

1. Скопировать все модели в вольюм `media-data-volume`
   1. Путь к volume
   ```bash
   docker volume inspect media-data-volume
   ```
2. Склонить демки в `media-data-volume`