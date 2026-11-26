# django-inventory

Inventory management web app built with Django for the *Ingeniería de
Software II* university course, developed by a Scrum team of seven over several
sprints. UI is in Spanish.

Features: login (rate-limited to 5 attempts/minute per IP), products,
suppliers and supplier–product links, warehouses with shelves, purchase orders
(e-mailing the supplier) and sales orders, plus reports: stock movement,
products, suppliers, order lead times, a Chart.js sales chart and an **ABC
analysis** of sales.

## Run (SQLite)

Requires [uv](https://docs.astral.sh/uv/).

```bash
uv sync
uv run python manage.py migrate
uv run python manage.py loaddata data_sprint3_01     # 345 sample rows
uv run python manage.py createsuperuser
uv run python manage.py runserver
```

Open <http://127.0.0.1:8000/> — it redirects to `/iniciar_sesion`.

To use PostgreSQL as originally deployed, `uv sync --extra postgres` and set
`INVENTARIOS_DB_ENGINE=postgres` plus the `INVENTARIOS_DB_*` variables (see
`.env.example`). Bootstrap and Chart.js are loaded from public CDNs.

## Tests

```bash
uv run python manage.py test aplicacion
```

Smoke tests: login page, login-required redirect, login + product list with
the fixture, and that the main report pages render.

## Layout

```
inventarios/    Django project (settings, urls)
aplicacion/     the app: models, forms, views, gestor/repositorio helpers,
                fixtures/data_sprint3_01.json, tests
plantillas/     templates (Bootstrap 3)
```

Known issues kept as-is: registering a *pedido* looks up the sender with
`User.objects.get(nombre='administrador')`, a field Django's `User` does not
have, so that flow fails before sending the e-mail.

## Team

JonMoll (Jonathan Mollapaza), eyvind1 (Eyvind Osco), aunesto17 (Alexander
Baylon), ltch23 (Luis Tong), joaquingx (Joaquin Garmendia), darkar5555
(Rodrigo Castro), Wilber Cutire Sivincha.
