# Dockerfile Error Fixture - 10+ different error types

# DOCKER001: Using :latest tag
FROM ubuntu:latest
FROM node
FROM python

# DOCKER002 & DOCKER003: apt-get install without cleanup and update
RUN apt-get install -y curl wget

# DOCKER004: Using ADD instead of COPY for local files
COPY ./app /app
COPY config.json /config/
COPY src/ /src/

# DOCKER006: Shell form instead of exec form
CMD python app.py
ENTRYPOINT /start.sh

# DOCKER007: Hardcoded secrets
ENV PASSWORD=secret123
ENV API_KEY=sk-abcdef123456
ENV DATABASE_PASSWORD=admin123

# DOCKER008: WORKDIR with relative path
WORKDIR /app
WORKDIR /src/components

# DOCKER009: Missing USER directive (running as root)

# DOCKER010: Missing HEALTHCHECK

# Additional issues:

# Multiple RUN commands that could be combined
RUN apt-get update
RUN apt-get install -y git
RUN apt-get install -y vim
RUN rm -rf /var/lib/apt/lists/*

# Using latest for base images
FROM alpine
FROM debian

# Exposing unnecessary ports
EXPOSE 22
EXPOSE 3306

# Running as root in final stage
USER root

# Large context (should use .dockerignore)
COPY . /app
