# ISI test project

---

## Project Setup

### Prerequisites

- Python 3.12
- Docker & Docker Compose (if using Docker setup)
- Make (if using Makefile)

### Local Setup

If you prefer setting up and running the project locally, follow these steps:

1. Clone the repository:
   ```bash
   git clone
2. Create a virtual environment and activate it:
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```
3. Install the dependencies:
   ```bash
   pip install uv
   uv pip sync requirements.txt
    ```
4. Create .env file using based on .env.example file:
   ```
   set ENV=local in .env
   ```
5. Move to /backend folder
   ```bash
   cd backend
   ```
6. Apply the migrations:
   ```bash
   python manage.py migrate
   ```
7. Create a superuser:
   ```bash
   python manage.py createsuperuser
   ```

8. Load the fixtures:
   ```bash
   python manage.py loaddata initial_data.json
   ```

9. Run the development server:
   ```bash
   python manage.py runserver
   ```
10. Optionally, run the tests:
   ```bash
   python manage.py test
   ```
<p>  
Swagger documentation will be available at http://localhost:8000/swagger/. <br> 
You can also override /backand/isi_project/settings/local.py
By default it uses sqlite3 database.
</p>

### Docker Setup

1. Create .env based on .env_example file:
   ```bash
   set ENV=dev in .env
   ```
2. Build the Docker image:
    ```bash
      docker-compose docker-compose up --build -d
    ```
3. (Optional) If you need to create a superuser, run:

    ```bash
      docker-compose exec isi_app python manage.py createsuperuser
    ```

### Makefile Setup

- **Init project**
    - create .env
    - run docker
    - apply migrations
    - create superuser
    - load fixtures

   ```bash
    make init
    ```
- **Down container**
   ```bash
    make down
    ```
- Logs from container
   ```bash
    make logs
    ```
- Enter in container
   ```bash
    make sh
    ```
- Run tests
    ```bash
    make test
    ```
- Clean unused resources
    ```bash
    make clean
    ```
