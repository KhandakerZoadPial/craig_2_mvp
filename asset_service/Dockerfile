# --- Stage 1: The Build Stage ---
FROM golang:1.23-alpine AS builder
WORKDIR /app

COPY go.mod go.sum ./
RUN go mod download

COPY . .

RUN CGO_ENABLED=0 GOOS=linux go build -o /app/asset-server .

# --- Stage 2: The Final, Lean Stage ---
FROM scratch
COPY --from=builder /app/asset-server /asset-server

EXPOSE 8000
ENTRYPOINT ["/asset-server"]