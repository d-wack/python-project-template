# Deployment Guide

This document outlines the complete deployment process for the logging service infrastructure.

## Prerequisites

- Docker and Docker Compose
- certbot for SSL certificate management
- nginx
- Basic understanding of Docker networking
- Access to the deployment server

## Infrastructure Components

1. Application Services:
   - FastAPI Application (Python)
   - PostgreSQL Database
   - Redis Cache

2. Monitoring Stack:
   - Prometheus (Metrics)
   - Grafana (Visualization)
   - Loki (Log Aggregation)
   - Promtail (Log Collection)

3. Development Tools:
   - PgAdmin (Database Management)
   - Redis Commander (Redis Management)

4. Reverse Proxy:
   - Nginx (SSL termination and routing)

## Deployment Steps

### 1. Initial Setup

```bash
# Clone the repository
git clone [repository-url]
cd logging_service

# Create necessary directories
mkdir -p nginx/certs
mkdir -p logs
mkdir -p prometheus
mkdir -p grafana/provisioning
mkdir -p loki
mkdir -p promtail
```

### 2. SSL Certificate Setup

```bash
# Generate SSL certificates using certbot
sudo certbot certonly --standalone -d loki-dev1.slicedhealth.com

# Copy certificates to nginx directory
sudo cp /etc/letsencrypt/live/loki-dev1.slicedhealth.com/fullchain.pem nginx/certs/fullchain.pem
sudo cp /etc/letsencrypt/live/loki-dev1.slicedhealth.com/privkey.pem nginx/certs/privkey.pem

# Set correct permissions
sudo chown -R $USER:$USER nginx/certs/
chmod 600 nginx/certs/*
```

### 3. Authentication Setup

```bash
# Install apache2-utils for htpasswd
sudo apt-get update && sudo apt-get install -y apache2-utils

# Create initial admin user
htpasswd -c -B nginx/.htpasswd admin

# Add Loki user
htpasswd -B nginx/.htpasswd loki
```

### 4. Environment Configuration

Create `.env.development` with appropriate values:
```ini
# Application Settings
APP_NAME=logging_service
ENVIRONMENT=development
DEBUG=True
LOG_LEVEL=DEBUG

# Server Settings
HOST=0.0.0.0
PORT=8000

# Database Settings
DB_HOST=postgres
DB_PORT=5432
DB_NAME=logging_db
DB_USER=logger
DB_PASSWORD=development_password
DB_POOL_SIZE=5
DB_MAX_OVERFLOW=10
DB_POOL_TIMEOUT=30
DB_ECHO=True

# Redis Settings
REDIS_HOST=redis
REDIS_PORT=6379
REDIS_DB=0
REDIS_PASSWORD=

# Monitoring
ENABLE_METRICS=True
METRICS_PORT=9090
```

### 5. Service Configuration

#### Nginx Configuration
The nginx configuration includes:
- SSL termination
- HTTP/2 support
- Reverse proxy settings
- Basic authentication for protected endpoints
- Rate limiting
- Security headers

Key features:
- Automatic HTTP to HTTPS redirection
- Separate server blocks for each service
- Protected endpoints with basic auth
- Optimized SSL settings
- Gzip compression

#### Loki Configuration
Create `loki/local-config.yaml`:
```yaml
auth_enabled: false

server:
  http_listen_port: 3100

common:
  path_prefix: /loki
  storage:
    filesystem:
      chunks_directory: /loki/chunks
      rules_directory: /loki/rules
  replication_factor: 1
  ring:
    kvstore:
      store: inmemory

schema_config:
  configs:
    - from: 2020-10-24
      store: boltdb-shipper
      object_store: filesystem
      schema: v11
      index:
        prefix: index_
        period: 24h
```

#### Promtail Configuration
Create `promtail/config.yml`:
```yaml
server:
  http_listen_port: 9080
  grpc_listen_port: 0

positions:
  filename: /tmp/positions.yaml

clients:
  - url: http://loki:3100/loki/api/v1/push

scrape_configs:
  - job_name: docker
    static_configs:
      - targets:
          - localhost
        labels:
          job: docker
          __path__: /var/lib/docker/containers/*/*-json.log

  - job_name: system
    static_configs:
      - targets:
          - localhost
        labels:
          job: system
          __path__: /var/log/*log

  - job_name: application
    static_configs:
      - targets:
          - localhost
        labels:
          job: application
          __path__: /var/log/logging_service/*log
```

### 6. Database Initialization

The database initialization scripts are located in `init-scripts/`:
- `01-init.sql`: Creates extensions, schemas, and audit functions
- `02-audit-tables.sql`: Sets up audit logging infrastructure

### 7. Starting the Services

```bash
# Build and start all services
docker compose up -d --build

# Verify all services are running
docker compose ps

# Check logs for any issues
docker compose logs -f
```

### 8. Post-Deployment Verification

1. Access Points (replace with actual domain):
   - Application: https://logging-dev1.slicedhealth.com
   - Grafana: https://grafana-dev1.slicedhealth.com
   - Prometheus: https://prometheus-dev1.slicedhealth.com
   - PgAdmin: https://pgadmin-dev1.slicedhealth.com
   - Redis Commander: https://redis-dev1.slicedhealth.com
   - Loki: https://loki-dev1.slicedhealth.com

2. Health Checks:
   ```bash
   # Check application health
   curl https://logging-dev1.slicedhealth.com/health

   # Verify Prometheus metrics
   curl https://logging-dev1.slicedhealth.com/metrics
   ```

3. Grafana Setup:
   - Default credentials: admin/admin
   - Add Loki as a data source
   - Import dashboards as needed

### 9. Maintenance

#### SSL Certificate Renewal
```bash
# Renew certificates
sudo certbot renew

# Copy new certificates
./scripts/setup_certs.sh

# Restart nginx
docker compose restart nginx
```

#### Backup Procedures
- Database backups are handled through PostgreSQL's native backup tools
- Grafana dashboards should be exported and version controlled
- Configuration files are version controlled in the repository

#### Log Rotation
Log rotation is handled by:
- Docker's built-in log rotation for container logs
- System's logrotate for application logs
- Loki's retention policies for aggregated logs

## Security Considerations

1. Access Control:
   - Basic authentication for admin interfaces
   - Rate limiting on API endpoints
   - SSL/TLS encryption for all services

2. Network Security:
   - Internal services not exposed directly
   - Nginx reverse proxy with security headers
   - Docker network isolation

3. Monitoring:
   - Prometheus metrics for system monitoring
   - Loki for log aggregation
   - Grafana dashboards for visualization

## Troubleshooting

1. Certificate Issues:
   ```bash
   # Check nginx config
   docker compose exec nginx nginx -t
   
   # Verify certificate paths
   ls -la nginx/certs/
   ```

2. Log Access:
   ```bash
   # View service logs
   docker compose logs [service_name]
   
   # Check Loki logs
   docker compose logs loki
   ```

3. Database Issues:
   ```bash
   # Check PostgreSQL logs
   docker compose logs postgres
   
   # Verify database connectivity
   docker compose exec postgres pg_isready -U logger -d logging_db
   ```

## Additional Resources

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Grafana Documentation](https://grafana.com/docs/)
- [Loki Documentation](https://grafana.com/docs/loki/latest/)
- [Prometheus Documentation](https://prometheus.io/docs/introduction/overview/) 