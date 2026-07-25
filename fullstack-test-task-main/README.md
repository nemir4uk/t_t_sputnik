## Тестовое задание на позицию Fullstack разработчика (Python + React)

**Вводные:**
1. Здесь представлен MVP проект файлообменника. Он позволяет загружать файлы, проверяет их на подозрительный контент и отправляет алерты;
2. Репозиторий содержит в себе бэкенд и фронтенд части;
3. В обоих частях присутствуют баги, неоптимизированный код, неудачные архитектурные решения.

**Задачи:**
1. Проведите рефакторинг бэкенда, не ломая бизнес-логики: предложите свое видение архитектуры и реализуйте его;
2. (Дополнительно) На бэкенде есть возможность неочевидной оптимизации - выполните ее;
3. (Дополнительно) Разбейте логику фронтенда на слои;

**Запуск:**
заполняем .env и frontend/.env или оставляем по дефолту как в example

```docker compose -f docker-compose.dev.yml up```


```mermaid
flowchart LR
Frontend([Frontend App])
    Frontend -->|HTTP| FastAPI
    subgraph FastAPI_Service [FastAPI Service]
        FastAPI[FastAPI]
    end
FastAPI  -->|Insert| Files
FastAPI  -->|Streaming| MinIO
FastAPI  -->|Insert| Outbox
subgraph Postgres service
        Files[(Files Table)]
        Alerts[(Alerts Table)]
        Outbox[(Outbox Table)]
end

subgraph MinIO service
MinIO 
end

    Worker --> |Select| Outbox
         Status_worker -->|Update status| Files
         Alert_worker-->|Insert| Alerts
     subgraph Outbox processor
Worker
Status_worker 
Alert_worker
     end
 alerts_queue -->|push| Alert_worker
            status_queue -->|push| Status_worker 
Worker -->|publish paylod| new_files_queue
subgraph RabbitMQ
new_files_queue
status_queue
check_metadata_queue
alerts_queue
end
             new_files_queue -->|push| Scan_Consumer 
         Scan_Consumer -->|publish| status_queue
Scan_Consumer -->|publish| check_metadata_queue
check_metadata_queue -->|push| Check_metadata_Consumer
     subgraph Consumer Service
Scan_Consumer
Check_metadata_Consumer
     end
    Check_metadata_Consumer -->|publish| alerts_queue
Check_metadata_Consumer -->|publish| status_queue
Check_metadata_Consumer -->|check_metadata| MinIO
     Scan_Consumer  -.->|fail after retries| DLQ[(Dead Letter Queue)]
Check_metadata_Consumer-.->|fail after retries| DLQ[(Dead Letter Queue)]

```
