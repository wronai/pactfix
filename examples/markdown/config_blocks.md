# Pactfix Markdown - Config analyzers in fenced blocks

Ten plik testuje config analyzery uruchamiane wewnątrz fenced code blocks.

```docker-compose
version: "3.8"
services:
  web:
    image: nginx:latest
    privileged: true
    environment:
      - PASSWORD=hunter2
    volumes:
      - /var/run/docker.sock:/var/run/docker.sock
  api:
    image: my-api
```

```github-actions
name: CI
on:
  pull_request_target:

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@master
      - name: Leak
        run: echo token=abc123
```

```nginx
server {
  listen 443 ssl;
  server_tokens on;
  ssl_certificate /etc/ssl/cert.pem;
  ssl_protocols TLSv1 TLSv1.1;

  location /static/ {
    root /var/www;
  }
}
```

```ansible
- hosts: all
  become: true
  tasks:
    - name: Install package
      shell: echo installing
    - name: Set password
      debug:
        msg: "set password"
      vars:
        password: hunter2
    - name: Ignore errors
      command: false
      ignore_errors: true
```

```sql
SELECT * FROM users;
CREATE TABLE users(id INT);
DROP TABLE users;
UPDATE users SET role='admin';
```
