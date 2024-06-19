# Admin Movies Panel + API

# Local development
```bash
cp .env.example .env  # edit if necessary
```

### Local development using .venv
```bash
cd app
make venv
source .venv/bin/activate
python manage.py runserver
```

### Local development in container
```bash
docker-compose up
```

### Start on production
```bash
docker-compose -f docker-compose-prod.yml up
```
