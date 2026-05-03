# Production Deployment Guide: EduCore Multi-Tenant

To support subdomains like `greenhood.educore.com` in production, you need a combination of **Wildcard DNS** and a properly configured **Nginx** reverse proxy.

## 1. Wildcard DNS Setup
You must point all subdomains of your domain to your server's IP address.
- **Provider**: Go to your DNS provider (Cloudflare, Namecheap, etc.).
- **Record**: Add an `A` record.
- **Host**: `*` (This is the wildcard).
- **Value**: Your server's public IP address.
- **Verification**: `ping anything.yourdomain.com` should return your server's IP.

## 2. Nginx Configuration
Nginx acts as the entry point. It receives the request for `school.educore.com` and passes the `Host` header to Django.

### Example Nginx Config (`/etc/nginx/sites-available/educore`)
```nginx
server {
    listen 80;
    server_name .educore.com; # The dot before the domain handles the wildcard

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host; # CRITICAL: Passes the subdomain to Django
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    location /static/ {
        alias /home/brandon/Documents/educore_full/staticfiles/;
    }

    location /media/ {
        alias /home/brandon/Documents/educore_full/media/;
    }
}
```

## 3. SSL (HTTPS) with Let's Encrypt
For multi-tenant subdomains, you need a **Wildcard SSL Certificate**.
```bash
sudo certbot certonly --manual --preferred-challenges dns -d "*.educore.com" -d "educore.com"
```
*Note: Wildcard certificates usually require DNS-01 challenge (adding a TXT record to your DNS).*

## 4. Rate Limiting in Production
We have implemented a dual-layer rate limiting strategy:

### A. Nginx Layer (IP-Based)
Best for blocking DDoS and aggressive bots.
```nginx
limit_req_zone $binary_remote_addr zone=ip_limit:10m rate=5r/s;
server {
    ...
    location / {
        limit_req zone=ip_limit burst=10 nodelay;
        ...
    }
}
```

### B. Django Layer (School & User Based)
Implemented via custom middleware in `core/middleware.py`.
- **Per IP**: Limits unauthenticated requests.
- **Per User**: Limits logged-in users regardless of IP.
- **Per School**: Limits total traffic to a specific school tenant to protect server resources.

## 5. Deployment Checklist
1. Set `DEBUG = False` in `settings.py`.
2. Update `ALLOWED_HOSTS = ['.educore.com', 'your-ip']`.
3. Run `python manage.py collectstatic`.
4. Use `gunicorn` to serve the application:
   ```bash
   gunicorn --workers 3 --bind 127.0.0.1:8000 educore_project.wsgi:application
   ```
