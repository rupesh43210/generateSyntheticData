# Docker Setup for PII Generator

This document provides detailed instructions for running the PII Generator using Docker.

> **Note**: The full Dockerfile with SQL Server ODBC drivers may have build issues on some systems. Use the lightweight version (`docker-compose.lite.yml`) for file-based output, or connect to an external database.

## 🐳 Prerequisites

- Docker Engine 20.10 or higher
- Docker Compose v2.0 or higher
- 8GB RAM minimum (for SQL Server container)
- 20GB free disk space

## 🚀 Quick Start

```bash
# Clone the repository
git clone https://github.com/rupesh43210/generateSyntheticData.git
cd generateSyntheticData

# Start all services
docker-compose up -d

# Wait for services to be ready (about 30 seconds)
docker-compose logs -f pii-generator

# Access the web interface
open http://localhost:5001
```

## 📦 Available Services

### 1. PII Generator Web App
- **URL**: http://localhost:5001
- **Description**: Web interface for generating synthetic data
- **Container**: `pii-generator-app`

### 2. SQL Server Database
- **Port**: 1433
- **Credentials**: 
  - Username: `sa`
  - Password: `YourStrong@Password123`
- **Container**: `pii-sqlserver`

### 3. CLI Interface (Optional)
Run batch jobs using the CLI container:

```bash
# Generate 10,000 records to CSV
docker-compose run --rm pii-cli python pii_gen.py generate --count 10000 --output /app/output/data.csv

# Stream data at 100 records/second
docker-compose run --rm pii-cli python pii_gen.py stream --rate 100 --duration 3600

# Access CLI shell
docker-compose --profile cli run --rm pii-cli cli
```

## 🛠️ Configuration

### Environment Variables

Create a `.env` file in the project root:

```env
# Database Configuration
DB_SERVER=sqlserver
DB_DATABASE=TestDatabase
DB_USERNAME=sa
DB_PASSWORD=YourStrong@Password123
DB_PORT=1433

# Application Settings
FLASK_ENV=production
BATCH_SIZE=5000
MAX_WORKERS=4
LOG_LEVEL=INFO

# Performance Tuning
MEMORY_LIMIT_MB=4096
ERROR_RATE=0.02
DUPLICATE_RATE=0.05
```

### Custom Configuration

Mount your custom configuration files:

```yaml
# docker-compose.override.yml
services:
  pii-generator:
    volumes:
      - ./my-configs:/app/configs:ro
```

## 📊 Docker Compose Profiles

The setup includes optional services that can be enabled using profiles:

```bash
# Start with PgAdmin for database management
docker-compose --profile tools up -d

# Start with Redis caching
docker-compose --profile cache up -d

# Start CLI container
docker-compose --profile cli up -d
```

## 🔧 Common Operations

### Build and Rebuild

```bash
# Build images
docker-compose build

# Force rebuild
docker-compose build --no-cache

# Build specific service
docker-compose build pii-generator
```

### Container Management

```bash
# Start services
docker-compose up -d

# Stop services
docker-compose down

# Stop and remove volumes (WARNING: Deletes data)
docker-compose down -v

# View logs
docker-compose logs -f pii-generator

# Execute commands in running container
docker-compose exec pii-generator python pii_gen.py --help
```

### Database Operations

```bash
# Connect to SQL Server
docker-compose exec sqlserver /opt/mssql-tools/bin/sqlcmd -S localhost -U sa -P YourStrong@Password123

# Backup database
docker-compose exec sqlserver /opt/mssql-tools/bin/sqlcmd -S localhost -U sa -P YourStrong@Password123 \
  -Q "BACKUP DATABASE TestDatabase TO DISK = '/var/opt/mssql/backup/TestDatabase.bak'"

# View database logs
docker-compose logs sqlserver
```

## 🚨 Troubleshooting

### Container Won't Start

```bash
# Check logs
docker-compose logs pii-generator

# Check container status
docker-compose ps

# Rebuild and restart
docker-compose down
docker-compose build --no-cache
docker-compose up -d
```

### Database Connection Issues

1. Ensure SQL Server is healthy:
```bash
docker-compose ps sqlserver
docker-compose exec sqlserver /opt/mssql-tools/bin/sqlcmd -S localhost -U sa -P YourStrong@Password123 -Q "SELECT 1"
```

2. Check environment variables:
```bash
docker-compose config
```

3. Verify network connectivity:
```bash
docker-compose exec pii-generator ping sqlserver
```

### Performance Issues

1. Increase Docker resources:
   - Docker Desktop: Preferences → Resources
   - Allocate at least 4 CPUs and 8GB RAM

2. Optimize batch size:
```env
BATCH_SIZE=10000
MAX_WORKERS=8
```

3. Monitor resource usage:
```bash
docker stats
```

## 🏗️ Production Deployment

### Using Docker Swarm

```bash
# Initialize swarm
docker swarm init

# Deploy stack
docker stack deploy -c docker-compose.yml pii-generator

# Scale services
docker service scale pii-generator_pii-generator=3
```

### Using Kubernetes

See `kubernetes/` directory for Kubernetes manifests (if available).

### Security Considerations

1. **Change default passwords** in production
2. **Use secrets management** for sensitive data:
```yaml
services:
  pii-generator:
    secrets:
      - db_password
secrets:
  db_password:
    external: true
```

3. **Enable TLS** for SQL Server connections
4. **Use non-root user** (already configured)
5. **Limit network exposure** using custom networks

## 📈 Monitoring

### Health Checks

The application includes health checks:

```bash
# Check application health
curl http://localhost:5001/api/system/status

# Check via Docker
docker-compose ps
```

### Logs

All logs are stored in the `./logs` directory:

```bash
# Application logs
tail -f logs/pii_generator.log

# Web server logs
docker-compose logs -f pii-generator
```

## 🔄 Updates

```bash
# Pull latest changes
git pull

# Rebuild containers
docker-compose build --pull

# Restart services
docker-compose up -d
```

## 🆘 Support

For Docker-specific issues:
1. Check Docker logs: `docker-compose logs`
2. Verify Docker version: `docker --version`
3. Ensure sufficient resources
4. Check [Docker documentation](https://docs.docker.com/)

For application issues, see the main [README.md](README.md).