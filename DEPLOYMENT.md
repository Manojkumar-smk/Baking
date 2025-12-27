# Deployment Checklist and Documentation

## Production Deployment Guide for Baking E-Commerce Platform

This comprehensive guide covers deployment of the full-stack cookie shop e-commerce application.

---

## Table of Contents
1. [Pre-Deployment Checklist](#pre-deployment-checklist)
2. [Environment Configuration](#environment-configuration)
3. [Database Setup](#database-setup)
4. [Backend Deployment](#backend-deployment)
5. [Frontend Deployment](#frontend-deployment)
6. [Post-Deployment Verification](#post-deployment-verification)
7. [Monitoring and Maintenance](#monitoring-and-maintenance)

---

## Pre-Deployment Checklist

### Code Quality
- [ ] All tests passing (backend and frontend)
- [ ] No console errors or warnings
- [ ] Code linted and formatted
- [ ] Security vulnerabilities checked (`npm audit`, `pip check`)
- [ ] Dependencies updated to latest stable versions

### Configuration
- [ ] Environment variables configured for production
- [ ] Secrets and API keys secured (not in repository)
- [ ] CORS settings configured for production domain
- [ ] Rate limiting enabled
- [ ] SSL/TLS certificates obtained

### Database
- [ ] Database migrations ready
- [ ] Database backups configured
- [ ] Initial data/seed data prepared
- [ ] Database indexes optimized

### Third-Party Services
- [ ] Stripe account set up (production keys)
- [ ] Email service configured (if applicable)
- [ ] CDN configured for static assets
- [ ] Error tracking service set up (e.g., Sentry)

---

## Environment Configuration

### Backend Environment Variables

Create a `.env` file in the `backend/` directory:

```bash
# Flask Configuration
FLASK_ENV=production
SECRET_KEY=<your-secure-secret-key>
DEBUG=False

# Database Configuration
DATABASE_URL=postgresql://username:password@host:port/database_name

# JWT Configuration
JWT_SECRET_KEY=<your-jwt-secret-key>
JWT_ACCESS_TOKEN_EXPIRES=3600  # 1 hour
JWT_REFRESH_TOKEN_EXPIRES=2592000  # 30 days

# Stripe Configuration
STRIPE_SECRET_KEY=sk_live_your_stripe_secret_key
STRIPE_PUBLISHABLE_KEY=pk_live_your_stripe_publishable_key
STRIPE_WEBHOOK_SECRET=whsec_your_webhook_secret

# CORS Configuration
CORS_ORIGINS=https://yourdomain.com,https://www.yourdomain.com

# Email Configuration (if using)
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USE_TLS=True
MAIL_USERNAME=your-email@gmail.com
MAIL_PASSWORD=your-app-password

# File Upload
UPLOAD_FOLDER=uploads
MAX_CONTENT_LENGTH=16777216  # 16MB

# Redis (if using for caching/sessions)
REDIS_URL=redis://localhost:6379/0
```

### Frontend Environment Variables

Create a `.env.production` file in the `frontend/` directory:

```bash
# API Configuration
VITE_API_URL=https://api.yourdomain.com/api/v1

# Stripe Configuration
VITE_STRIPE_PUBLISHABLE_KEY=pk_live_your_stripe_publishable_key

# App Configuration
VITE_APP_NAME=Cookie Shop
VITE_APP_URL=https://yourdomain.com
```

---

## Database Setup

### PostgreSQL Production Setup

1. **Create Production Database**
```sql
CREATE DATABASE cookie_shop_production;
CREATE USER cookie_shop_user WITH PASSWORD 'secure_password';
GRANT ALL PRIVILEGES ON DATABASE cookie_shop_production TO cookie_shop_user;
```

2. **Run Migrations**
```bash
cd backend
flask db upgrade
```

3. **Seed Initial Data (Optional)**
```bash
python scripts/seed_categories.py
python scripts/seed_initial_products.py
```

4. **Configure Backups**
```bash
# Set up automated backups using pg_dump
0 2 * * * pg_dump cookie_shop_production | gzip > /backups/cookie_shop_$(date +\%Y\%m\%d).sql.gz
```

---

## Backend Deployment

### Option 1: Deploy with Gunicorn (Recommended)

1. **Install Production Dependencies**
```bash
cd backend
pip install gunicorn
```

2. **Create Gunicorn Configuration** (`gunicorn.conf.py`):
```python
bind = "0.0.0.0:8000"
workers = 4
worker_class = "sync"
max_requests = 1000
max_requests_jitter = 50
timeout = 30
keepalive = 5
errorlog = "/var/log/gunicorn/error.log"
accesslog = "/var/log/gunicorn/access.log"
loglevel = "info"
```

3. **Run with Gunicorn**
```bash
gunicorn -c gunicorn.conf.py "app:create_app()"
```

4. **Set up Systemd Service** (`/etc/systemd/system/cookie-shop-api.service`):
```ini
[Unit]
Description=Cookie Shop API
After=network.target

[Service]
User=www-data
Group=www-data
WorkingDirectory=/var/www/cookie-shop/backend
Environment="PATH=/var/www/cookie-shop/backend/venv/bin"
ExecStart=/var/www/cookie-shop/backend/venv/bin/gunicorn -c gunicorn.conf.py "app:create_app()"
Restart=always

[Install]
WantedBy=multi-user.target
```

5. **Enable and Start Service**
```bash
sudo systemctl enable cookie-shop-api
sudo systemctl start cookie-shop-api
```

### Option 2: Deploy with Docker

1. **Build Docker Image**
```bash
cd backend
docker build -t cookie-shop-api:latest .
```

2. **Run Container**
```bash
docker run -d \
  --name cookie-shop-api \
  -p 8000:8000 \
  --env-file .env \
  cookie-shop-api:latest
```

### Nginx Reverse Proxy Configuration

Create `/etc/nginx/sites-available/cookie-shop-api`:

```nginx
server {
    listen 80;
    server_name api.yourdomain.com;

    # Redirect to HTTPS
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name api.yourdomain.com;

    ssl_certificate /etc/letsencrypt/live/api.yourdomain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/api.yourdomain.com/privkey.pem;

    # Security headers
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;

    location / {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # Increase timeout for payment processing
    location /api/v1/payments {
        proxy_pass http://localhost:8000;
        proxy_read_timeout 90s;
        proxy_connect_timeout 90s;
    }
}
```

---

## Frontend Deployment

### Build Production Bundle

```bash
cd frontend
npm run build
```

### Option 1: Deploy to Netlify/Vercel

1. **Netlify Deployment**
```bash
# Install Netlify CLI
npm install -g netlify-cli

# Deploy
cd frontend
netlify deploy --prod
```

2. **Configure Netlify** (`netlify.toml`):
```toml
[build]
  command = "npm run build"
  publish = "dist"

[[redirects]]
  from = "/*"
  to = "/index.html"
  status = 200
```

### Option 2: Deploy to Nginx

1. **Copy Build Files**
```bash
sudo cp -r frontend/dist/* /var/www/cookie-shop/
```

2. **Nginx Configuration** (`/etc/nginx/sites-available/cookie-shop`):
```nginx
server {
    listen 80;
    server_name yourdomain.com www.yourdomain.com;
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name yourdomain.com www.yourdomain.com;

    root /var/www/cookie-shop;
    index index.html;

    ssl_certificate /etc/letsencrypt/live/yourdomain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/yourdomain.com/privkey.pem;

    # Security headers
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;

    # Gzip compression
    gzip on;
    gzip_vary on;
    gzip_min_length 1024;
    gzip_types text/plain text/css text/xml text/javascript application/x-javascript application/xml+rss application/javascript application/json;

    # Cache static assets
    location ~* \.(js|css|png|jpg|jpeg|gif|ico|svg|woff|woff2|ttf|eot)$ {
        expires 1y;
        add_header Cache-Control "public, immutable";
    }

    # SPA routing
    location / {
        try_files $uri $uri/ /index.html;
    }
}
```

3. **Enable Site**
```bash
sudo ln -s /etc/nginx/sites-available/cookie-shop /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

---

## Post-Deployment Verification

### Health Checks

1. **Backend API Health**
```bash
curl https://api.yourdomain.com/health
# Expected: {"status": "healthy"}
```

2. **Frontend Loading**
```bash
curl -I https://yourdomain.com
# Expected: HTTP/2 200
```

3. **Database Connection**
```bash
# Check database connections
psql -U cookie_shop_user -d cookie_shop_production -c "SELECT 1;"
```

### Functional Testing

- [ ] User registration works
- [ ] User login works
- [ ] Product browsing works
- [ ] Add to cart functionality works
- [ ] Checkout process completes
- [ ] Stripe payment processes successfully
- [ ] Order confirmation email sent
- [ ] Admin dashboard loads
- [ ] Admin can update order status
- [ ] Protected routes require authentication

### Performance Testing

```bash
# Test API response time
curl -w "@curl-format.txt" -o /dev/null -s https://api.yourdomain.com/api/v1/products

# Load testing with Apache Bench
ab -n 1000 -c 10 https://yourdomain.com/
```

### Security Verification

- [ ] SSL/TLS certificate valid
- [ ] Security headers present
- [ ] CORS configured correctly
- [ ] SQL injection protection verified
- [ ] XSS protection verified
- [ ] CSRF protection enabled
- [ ] Rate limiting working
- [ ] Sensitive data not exposed in logs

---

## Monitoring and Maintenance

### Logging

1. **Backend Logs**
```bash
# View application logs
sudo journalctl -u cookie-shop-api -f

# Gunicorn logs
tail -f /var/log/gunicorn/error.log
```

2. **Nginx Logs**
```bash
tail -f /var/log/nginx/access.log
tail -f /var/log/nginx/error.log
```

### Monitoring Tools

**Recommended Services:**
- **Application Performance**: New Relic, Datadog
- **Error Tracking**: Sentry
- **Uptime Monitoring**: UptimeRobot, Pingdom
- **Log Management**: Loggly, Papertrail

**Basic Monitoring Script** (`monitor.sh`):
```bash
#!/bin/bash

# Check if API is responding
if curl -f -s https://api.yourdomain.com/health > /dev/null; then
    echo "API is healthy"
else
    echo "API is down!" | mail -s "API Alert" admin@yourdomain.com
fi

# Check disk space
df -h | grep -vE '^Filesystem|tmpfs|cdrom' | awk '{ print $5 " " $1 }' | while read output;
do
  usep=$(echo $output | awk '{ print $1}' | cut -d'%' -f1)
  if [ $usep -ge 90 ]; then
    echo "Disk usage critical: $output" | mail -s "Disk Alert" admin@yourdomain.com
  fi
done
```

### Backup Strategy

1. **Database Backups** (Daily)
```bash
0 2 * * * /usr/local/bin/backup-database.sh
```

2. **File Uploads Backup** (Daily)
```bash
0 3 * * * rsync -avz /var/www/cookie-shop/uploads/ /backups/uploads/
```

3. **Retention Policy**
- Daily backups: Keep for 7 days
- Weekly backups: Keep for 4 weeks
- Monthly backups: Keep for 12 months

### Maintenance Tasks

**Weekly:**
- [ ] Review error logs
- [ ] Check disk space
- [ ] Monitor database performance
- [ ] Review security alerts

**Monthly:**
- [ ] Update dependencies
- [ ] Review and rotate logs
- [ ] Test backup restoration
- [ ] Security audit

**Quarterly:**
- [ ] Performance optimization
- [ ] Code review and refactoring
- [ ] Update SSL certificates (if needed)
- [ ] Disaster recovery drill

---

## Rollback Procedure

If deployment issues occur:

1. **Backend Rollback**
```bash
# Stop current version
sudo systemctl stop cookie-shop-api

# Restore previous version from backup
cd /var/www/cookie-shop/backend
git checkout <previous-commit-hash>

# Rollback database migrations (if needed)
flask db downgrade

# Restart service
sudo systemctl start cookie-shop-api
```

2. **Frontend Rollback**
```bash
# Restore previous build
sudo cp -r /backups/frontend-previous/* /var/www/cookie-shop/
sudo systemctl reload nginx
```

---

## Support and Troubleshooting

### Common Issues

**Issue: 502 Bad Gateway**
- Check if Gunicorn is running: `sudo systemctl status cookie-shop-api`
- Check Gunicorn logs: `tail -f /var/log/gunicorn/error.log`
- Verify database connection

**Issue: CORS Errors**
- Verify CORS_ORIGINS in backend .env
- Check Nginx proxy headers

**Issue: Payment Processing Fails**
- Verify Stripe keys are correct (live mode)
- Check webhook endpoint is accessible
- Review Stripe dashboard for errors

### Getting Help

- Documentation: [Project README](README.md)
- Issues: [GitHub Issues](https://github.com/yourusername/cookie-shop/issues)
- Support: support@yourdomain.com

---

## Conclusion

This deployment guide ensures a production-ready deployment of the Baking E-Commerce Platform. Follow each step carefully and verify all checklistsafter deployment.

**Last Updated:** 2025-12-27
