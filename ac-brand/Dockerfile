# syntax=docker/dockerfile:1

FROM python:3.10

WORKDIR /ac-brand-docker

COPY ac-main/methods ./methods
COPY ac-brand/methods/database/brand_db_schemas.py ./methods/database/db_schemas.py
COPY ac-brand/methods/database/brand-filter/brand_db_filter.py ./methods/database/db_filter.py
