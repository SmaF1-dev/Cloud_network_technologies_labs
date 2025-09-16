# Cloud Technologies and Services
## Лабораторная 2, версия со звездочкой.

#### Lyutiy Nick, Mitrofanova Polina, Trikula Artyom, Muldiyarov Arseniy

### Цель работы:
1. Изучить что такое docker-compose
2. Попробовать написать docker-compose без знания best practices 
3. Найти базовые best practices 
4. Написать полностью хороший (вряд ли идеальный) docker-compose

До написания этой лабораторной работы я уже немного знала, что такое docker-compose. Поэтому я думала, что в целом разибираюсь в синтаксисе и основных негласных правилах и практиках написания docker-compose. Как бы не так :(. Для начала я еще раз освежила в памяти что вообще такое docker-compose и чем он отличается от dockerfile, например.

### Docker-compose - это инструмент для создания инфраструктуры. Грубо говоря, он позволяет запускать много контейнеров сразу с помощью одного файла, не прописывая каждый в отельной строке 

### Плохой docker-compose
Итак, опираясь на эти знания и свой опыт я решила сама создать самый страшный, неправильный, плохой и вообще "тебя за такое уволят" docker-compose.

Вот так вот он у меня выглядел в итоге

```yaml 
version: '3.8'
services:
  web:
    image: nginx:latest
    ports:
      - "80:80"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
    environment:
      - DEBUG=true
    networks:
      - default_network

  db:
    image: postgres:latest
    ports:
      - "5432:5432"
    environment:
      - POSTGRES_PASSWORD=password
    networks:
      - default_network

  app:
    image:  python:latest
    volumes:
      - .:/app
    command: python /app/app.py 
    depends_on:
      - db
    networks:
      - default_network 

networks:
  default_network:
    driver: bridge
```
Что происходит в этом файле? Я поднимаю три сервиса ``web``, ``app`` и ``db``. Потом все три сервиса смогут "общаться" между собой через сеть.

Думаю, сейчас можно перейти к перечню основных best practices, чтобы подробнее разобрать все ошибки в "плохом" docker-compose

### Best practices для docker-compose
1. Необходимо соблюдать структуру: сервисы отдельно, инфра - отдельно
2. Надо использовать отдельный ```.env``` файл со всеми переменными для окружения (пароли, порты, названия БДшек)
3. Очень важно прописывать актуальные совместимые версии, прописывать ```latest``` большая ошибка, так как обновление может сломать весь код. 
4. Для хранения надо использовать ```volumes```, чтобы данные не потерялись при пересборке контейнеров.
5. Нужно настраивать проверку состояния через ```healthcheck```(я уточнила об этом у работюащего девопса, он сказал, что эту фичу редко используют, но я все-равно решила ее оставить).
6. Не забываем про логи, логгирование так же очень важно и намного упрощает работу. 
7. Необходимо минимизировать зависимости, использовать оптимальные и "легкие" образы.

Теперь зная все это, можно написать конкретные ошибки из плохого docker-compose

1. Использование ```latest```. Как я уже писала, это в перспективе может сломать вообще все. 
2. У сервиса ```app``` нет сборки в Dockerfile
3. Мы не проверяем, готова ли БД 
4. Ну а так же мы не используем ```volumes```, ```healthcheck```, ```.env``` - файл, логирование и разделение структуры

### Хороший docker-compose
Теперь мой docker-compose выглядит вот так. Я его довольно глобально поменяла,

``` yaml
version: '3.8'

services:
  web:
    image: nginx:1.27-alpine
    container_name: web
    ports:
      - "80:80"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf:ro
    depends_on:
      app:
        condition: service_healthy
    restart: unless-stopped
    networks:
      - app_network

  db:
    image: postgres:16-alpine
    container_name: db
    environment:
      - POSTGRES_USER=${POSTGRES_USER}
      - POSTGRES_PASSWORD=${POSTGRES_PASSWORD}
      - POSTGRES_DB=${POSTGRES_DB}
    volumes:
      - postgres_data:/var/lib/postgresql/data
    restart: unless-stopped
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U $$POSTGRES_USER -d $$POSTGRES_DB"]
      interval: 30s
      timeout: 5s
      retries: 5
    networks:
      - app_network

  app:
    build:
      context: .
      dockerfile: Dockerfile
    container_name: app
    command: gunicorn -b 0.0.0.0:8000 app:app
    environment:
      - DATABASE_URL=postgresql://${POSTGRES_USER}:${POSTGRES_PASSWORD}@db:5432/${POSTGRES_DB}
    depends_on:
      db:
        condition: service_healthy
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 5s
      retries: 3
    networks:
      - app_network

volumes:
  postgres_data:

networks:
  app_network:
    driver: bridge
```

Что хорошего мы добавили?
1. Добавили ```.env``` файлик, в который записали переменные окружения для бд. Теперь пароли и конфиги не находятся в docker-compose
2. ```Healthcheck```. Теперь бд проверяет готовность базы через ```pg_isready```, а app проверяет, что приложение отвечает на ```/health ```
3. Контейнеры теперь автоматически перезапускаются при сбоях, теперь инфра стабильнее и надежнее
``` yaml
restart: unless-stopped
```
4. Добавили ```volume```, поэтому теперь данные базы сохраняются между перезапусками контеййнерами и никакие данные мы не потеряем 
```yaml
volumes:
  postgres_data:
```
5. Все сервисы теперь подключены к одной внутренней сети, контейнеры видят друг друга по имени
```yaml
networks:
  app_network:
    driver: bridge
```
7. Теперь у нас есть свой Dockerfile - отдельный контейнер, в котором мы притянули зависимости ```requirements.txt``` и gunicorn (так мы типа иметируем то, что этот docker-compose и приложение, которое мы "запихиваем" в контейнер в теории реально будут работать, это мне посоветовал подключить великий и ужасный чатгпт)
8. ```nginx``` проксирует к ```app```, можно подключить https, кэши и статические файлы 

Сравнивая с плохим docker-compose можно заметить, что хороший выглядит логичнее и последовательнее

### Вывод по лабораторной работе
Пока я выполняла лабу, я лучше погрузилась в понимание что такое docker-compose и для чего он нужен. Так же я лучше запомнила, как оптимизировать работу с такими задачами, как выстраивать структуру. Так же я нашла большую документацию докера (по первой ссылке в гугле), которая в дальнейшем может мне очень пригодится. Собственно, главный источник - ```docs.docker.com```

Главный вывод: как бы не были полезны docker-compose, Dockerfile в сердечке

upd: Когда я уже хотела сдавать свой отчет на ревью коллегам по команде выяснелось, что я комитнула не из той ветки и получился вот такой прикол :)
![image](images/2025-09-17%2000.02.26.jpg)