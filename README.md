---

## Requirements

- Docker
- Docker Compose

---

## Setup and Run

### 1. Clone the repository

```bash
git clone https://github.com/mollah2022/vacation-rental-platform-sajib_ahmed-.git
cd vacation-rental-platform-sajib_ahmed-
```

### 2. Create environment file

```bash
cp .env.example .env
```

### 3. Build Docker images and start containers

```bash
docker compose up --build -d
```

First build takes around 10-15 minutes. The database image compiles pgvector from source and the web image installs all Python packages including sentence-transformers.

### 4. Run migrations

```bash
docker compose run --rm web python manage.py migrate
```

### 5. Create admin user

```bash
docker compose run --rm web python manage.py createsuperuser
```

### 6. Import sample property data

```bash
docker compose run --rm web python data/import_properties.py
```

### 7. Set GPS coordinates for locations

```bash
docker compose run --rm web python manage.py set_location_points
```

---

## Available URLs

| URL | Description |
|---|---|
| http://localhost:8000 | Homepage with search |
| http://localhost:8000/properties/ | Property listing with filters |
| http://localhost:8000/admin/ | Django Admin panel |
| http://localhost:8000/api/locations/autocomplete/?q=beach | Autocomplete API |

---

## How Semantic Search Works

Each location name is converted into a 384-dimension vector using the all-MiniLM-L6-v2 model and stored in PostgreSQL via pgvector. An HNSW index is created on the embedding field for fast similarity search. When a user searches, the query is also converted to a vector and the most similar locations are found using cosine distance. Text search and semantic search results are combined for better accuracy.

---

## Docker Commands

```bash
# Start containers
docker compose up -d

# Stop containers
docker compose down

# View logs
docker compose logs web --tail=20

# Restart web container
docker compose restart web
```

---

## Day by Day Progress

| Day | Work Done |
|---|---|
| Day 1 | Docker + PostgreSQL + PostGIS + pgvector setup, Django project, models, CSV import, Django Admin |
| Day 2 | Homepage, property listing page, property detail page, search and filters |
| Day 3 | Sentence Transformers integration, location embeddings, HNSW index, semantic search, autocomplete API |

---

## Author

Sajib Ahmed