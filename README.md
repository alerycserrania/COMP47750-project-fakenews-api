# Cloud Computing Project - Fake News - Backend

## Requirements

- Python 3.6+
- Hadoop 3+ running at in pseudo or fully distributed mode
- A MySQL Database

## Installation

It's advisable to create a virtual environment with python (optional):

```sh
python -m venv venv
source venv/bin/activate
```

Install all dependencies required to run the project:

```sh
pip install -r requirements.txt
```

Add these three environment variables:

```sh
export FASTAPI_FRONT_URL=# URL of the front application (e.g. http://localhost:3000)
export FASTAPI_DATABASE_URL=# URL string to connect to your database (typically mysql://username:password@host:post/db_name)
export FASTAPI_HADOOP_WEB_URL=# URL of the WEB UI (for Hadoop 3, default is http://localhost:9870)
```

The database `db_name` should already exists prior to execution

Finally, launch the web server with uvicorn
```sh
uvicorn main:app --host="0.0.0.0"
```

Test that everything is okay by navigating to the FastAPI swagger UI `http://localhost:8000/docs`
