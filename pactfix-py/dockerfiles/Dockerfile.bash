FROM ubuntu:22.04
RUN apt-get update && apt-get install -y bash shellcheck && rm -rf /var/lib/apt/lists/*
WORKDIR /app
COPY . .
RUN chmod +x *.sh 2>/dev/null || true
CMD ["bash", "-c", "shellcheck *.sh && ./main.sh || ./run.sh || echo 'No entrypoint'"]
