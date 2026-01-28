FROM golang:1.21-alpine
WORKDIR /app
COPY go.* ./
RUN go mod download 2>/dev/null || true
COPY . .
RUN go build -o main . 2>/dev/null || true
CMD ["go", "test", "-v", "./...", "||", "./main"]
