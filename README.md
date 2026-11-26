# django-inventory

[![CI](https://github.com/Wil12Fred/django-inventory/actions/workflows/ci.yml/badge.svg)](https://github.com/Wil12Fred/django-inventory/actions/workflows/ci.yml) [![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

Inventory management web app built with Django by a Scrum team of seven over
several sprints: products, suppliers, warehouses, purchase and sales orders,
and reports up to an ABC analysis of sales. The UI is in Spanish.

## Features

- Login with a rate limit of 5 attempts per minute per IP; every page except
  the login form requires an authenticated user.
- Products, suppliers and supplier–product links: list, register, delete.
- Warehouses with shelves (`AnaquelProducto`).
- Purchase orders (*pedidos*) that are e-mailed to the supplier, with a
  received/pending filter and a lead-time report (on time vs. late).
- Sales orders (*órdenes*) and reports: stock movement per product, products
  by entry date, purchase orders per supplier, a Chart.js sales chart and an
  **ABC analysis** (A ≤ 80 % of cumulative quantity, B ≤ 95 %, C the rest).
- A sample data fixture, `data_sprint3_01` (345 objects: 100 products,
  20 suppliers, 10 warehouses, 15 purchase orders, 25 sales orders, …).

## Requirements

- Python 3.10 or newer (`.python-version` pins 3.12) and
  [uv](https://docs.astral.sh/uv/).
  - Debian/Ubuntu: `sudo apt install python3`, then
    `curl -LsSf https://astral.sh/uv/install.sh | sh` (uv is not packaged).
  - Arch: `sudo pacman -S python uv`
- Optional, for PostgreSQL: a PostgreSQL server
  (`postgresql` on both Debian/Ubuntu and Arch) and `uv sync --extra postgres`.

Configuration comes from environment variables; see `.env.example`
(`DJANGO_SECRET_KEY`, `DJANGO_DEBUG`, `INVENTARIOS_DB_*`, and the
`INVENTARIOS_EMAIL_*` SMTP account that sends purchase orders).

## Build

```bash
uv sync --locked
uv run python manage.py check
```

## Run

SQLite is the default database:

```bash
uv run python manage.py migrate
uv run python manage.py loaddata data_sprint3_01
uv run python manage.py createsuperuser
uv run python manage.py runserver
```

Captured from a real run:

```
$ uv run python manage.py loaddata data_sprint3_01
Installed 345 object(s) from 1 fixture(s)
$ curl -si http://127.0.0.1:8000/ | head -1
HTTP/1.1 302 Found
[26/Nov/2026 05:04:29] "GET / HTTP/1.1" 302 0
[26/Nov/2026 05:04:29] "GET /iniciar_sesion/ HTTP/1.1" 200 1713
```

Open <http://127.0.0.1:8000/>; it redirects to `/iniciar_sesion`.

To use PostgreSQL as originally deployed, run `uv sync --extra postgres` and
set `INVENTARIOS_DB_ENGINE=postgres` plus the `INVENTARIOS_DB_*` variables.
Bootstrap and Chart.js are loaded from public CDNs.

## Tests

```bash
uv run python manage.py test aplicacion
```

21 tests on SQLite, loading the `data_sprint3_01` fixture:

- `aplicacion/tests.py` — login page, login-required redirect, login followed
  by the product list, and that the main report pages render.
- `aplicacion/test_views.py` — each list page returns 200 and shows the fixture
  rows (products, suppliers, warehouses, sales orders, supplier products); the
  supplier report counts every purchase order; the chart API returns twelve
  months; the ABC analysis names the product of each order and puts the
  largest order in class A; anonymous users cannot delete products or open the
  reports; registering a supplier (and rejecting a bad e-mail) and a product;
  deleting a product; registering a purchase order creates it and e-mails the
  supplier (Django's in-memory mail backend).

CI also runs `manage.py check` and `makemigrations --check`.

## Project layout

```
inventarios/        Django project: settings (env-driven), urls
aplicacion/
  models.py         products, suppliers, warehouses, orders
  views.py          all pages and the two JSON endpoints
  gestor.py         order and stock-movement helpers
  fixtures/         data_sprint3_01.json sample data
  tests.py, test_views.py
plantillas/         templates (Bootstrap 3)
```

## Known limitations

- Purchase-order e-mail failures are only printed to the console; the order
  is still saved.
- Forms look products and suppliers up by name, so those fields accept at
  most 20 characters although the model allows 100.
- The ABC analysis is computed per sales order, not aggregated per product,
  and needs window functions (SQLite 3.25+ or PostgreSQL).
- The `verificar_producto` page runs a query whose result it never shows.
- No pagination; the product list renders every row.

## Background

Developed in 2019 for a software engineering course at a university, by a
Scrum team of seven: JonMoll (Jonathan Mollapaza), eyvind1 (Eyvind Osco),
aunesto17 (Alexander Baylon), ltch23 (Luis Tong), joaquingx (Joaquin
Garmendia), darkar5555 (Rodrigo Castro) and Wilber Cutire Sivincha.

## License

MIT — see [LICENSE](LICENSE).
