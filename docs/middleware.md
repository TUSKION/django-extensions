# Middleware Extensions

This project includes reusable middleware for security, subdomain management, and more. Below is a summary of each middleware, its configuration, and usage.

## Available Middleware

### 1. AdminIPRestrictionMiddleware

**Purpose:** Restricts Django admin access to a whitelist of IPs or networks.

**Settings:**
- `ADMIN_IP_RESTRICTION_ENABLED` (default: `True`)
- `ADMIN_ALLOWED_IPS` (list of allowed IPs)
- `ADMIN_ALLOWED_NETWORKS` (list of allowed CIDR networks)

**How it works:**
If enabled, only requests from allowed IPs/networks can access `/admin/`. Others receive a 403 error.

**Features:**
- Supports individual IPs and network ranges
- Handles Cloudflare and proxy headers
- Secure by default (blocks all if no IPs configured)
- Detailed logging for debugging

**How to enable:**
Add to your `MIDDLEWARE` in `settings.py`:
```python
MIDDLEWARE = [
    # ...
    'essential_extensions.middleware.AdminIPRestrictionMiddleware',
    # ...
]
```

**Configuration:**
```python
# settings.py
ADMIN_IP_RESTRICTION_ENABLED = True
ADMIN_ALLOWED_IPS = [
    '192.168.1.100',
    '10.0.0.50',
]
ADMIN_ALLOWED_NETWORKS = [
    '192.168.1.0/24',
    '10.0.0.0/8',
]
```

### 2. SubdomainRedirectMiddleware

**Purpose:** Handles subdomain-to-main-domain redirects using the `SubdomainRedirect` model.

**Settings:**
- `MAIN_DOMAIN` (e.g., `'example.com'`)

**How it works:**
If a request comes to a subdomain (e.g., `blog.example.com`), checks for an active redirect and issues a permanent redirect to the main domain, either preserving the path or using a custom path.

**Features:**
- Automatically detects subdomains
- Supports both full and path-preserving redirects
- Uses object URLs when content_object is set
- Configurable main domain via `MAIN_DOMAIN` setting

**How to enable:**
Add to your `MIDDLEWARE` in `settings.py`:
```python
MIDDLEWARE = [
    # ...
    'essential_extensions.middleware.SubdomainRedirectMiddleware',
    # ...
]
```

**Configuration:**
```python
# settings.py
MAIN_DOMAIN = 'example.com'  # Your main domain
```

**Usage:**
The middleware works automatically with the `SubdomainRedirect` model. Configure redirects through the Django admin interface.

## Middleware Order

For optimal functionality, place the middleware in this order:

```python
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    
    # Essential Extensions middleware
    'essential_extensions.middleware.SubdomainRedirectMiddleware',
    'essential_extensions.middleware.AdminIPRestrictionMiddleware',
]
```

## Troubleshooting

### AdminIPRestrictionMiddleware Issues

**Problem:** Can't access admin from allowed IP
- Check if `ADMIN_IP_RESTRICTION_ENABLED` is `True`
- Verify your IP is in `ADMIN_ALLOWED_IPS` or `ADMIN_ALLOWED_NETWORKS`
- Check logs for IP detection issues

**Problem:** IP detection not working behind proxy
- The middleware handles common proxy headers (Cloudflare, X-Forwarded-For, X-Real-IP)
- Check if your proxy is setting the correct headers

### SubdomainRedirectMiddleware Issues

**Problem:** Subdomain redirects not working
- Verify `MAIN_DOMAIN` is set correctly in settings
- Check that `SubdomainRedirect` objects exist and are active
- Ensure the middleware is loaded before other URL processing middleware

**Problem:** Redirect loops
- Check that redirect paths don't create circular references
- Verify the target domain is different from the source subdomain

## Security Considerations

### AdminIPRestrictionMiddleware

- **Whitelist approach**: Only explicitly allowed IPs can access admin
- **Network support**: Can restrict to specific network ranges
- **Proxy handling**: Works with common proxy setups
- **Logging**: Detailed logs for security monitoring

### SubdomainRedirectMiddleware

- **Permanent redirects**: Uses 301 redirects for SEO
- **Path validation**: Validates redirect paths
- **Active status**: Only active redirects are processed

## Performance

Both middleware components are designed for minimal performance impact:

- **AdminIPRestrictionMiddleware**: Only processes admin requests
- **SubdomainRedirectMiddleware**: Only processes subdomain requests
- **Efficient lookups**: Uses database indexes for fast redirect lookups
- **Caching**: Consider caching redirect rules for high-traffic sites

---

For more details, see the [middleware source code](../essential_extensions/middleware.py). 