# Dremio Cloner API

A Flask REST API for cloning Dremio resources (spaces, folders, virtual datasets, reflections, wikis, and tags) from a **source** Dremio instance to a **target** Dremio instance.

All inputs are provided through the **Swagger UI**.

## Features

| Endpoint | Description |
|---|---|
| `POST /api/clone/spaces` | Clone spaces and their folder structures |
| `POST /api/clone/vds` | Clone virtual datasets (SQL views) |
| `POST /api/clone/reflections` | Clone reflections |
| `POST /api/clone/wikis-tags` | Clone wiki content and tags |
| `POST /api/clone/all` | Full clone (spaces → folders → VDS → reflections → wikis & tags) |
| `POST /api/catalog/browse` | Browse a Dremio catalog |
| `GET  /api/health` | Health check |

## Quick Start

### 1. Install dependencies

```bash
pip install -r requirements.txt
```

### 2. Run the application

```bash
python run.py
```

The API starts on `http://localhost:5000`.

### 3. Open Swagger UI

Navigate to **http://localhost:5000/swagger** in your browser to interact with all endpoints.

## Authentication

Each request accepts connection details for both the **source** and **target** Dremio instances. You can authenticate using either:

- **Personal Access Token (PAT)** – set the `pat` field
- **Username / Password** – set the `username` and `password` fields

## Project Structure

```
├── app/
│   ├── __init__.py          # Flask app factory & API setup
│   ├── config.py            # Environment-based configuration
│   ├── dremio_client.py     # Dremio REST API client
│   ├── models/
│   │   └── schemas.py       # Swagger request models
│   └── routes/
│       ├── health.py        # Health check endpoint
│       ├── catalog.py       # Catalog browsing endpoint
│       └── clone.py         # Clone endpoints
├── requirements.txt
├── run.py                   # Application entry point
└── README.md
```

## Production Deployment

Use Gunicorn for production:

```bash
gunicorn -w 4 -b 0.0.0.0:5000 run:app
```
