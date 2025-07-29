from django.shortcuts import redirect
from django.http import Http404
from django.conf import settings
from .models.SubdomainRedirect import SubdomainRedirect
from django.core.exceptions import PermissionDenied
import ipaddress

class AdminIPRestrictionMiddleware:
    """
    Middleware to restrict Django admin access to specific IP addresses.
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
        
        # Get allowed IPs from settings, with fallbacks
        self.allowed_ips = getattr(settings, 'ADMIN_ALLOWED_IPS', [])
        self.allowed_networks = getattr(settings, 'ADMIN_ALLOWED_NETWORKS', [])
        
        # Convert IP strings to ipaddress objects for efficient checking
        self.allowed_ip_objects = []
        for ip in self.allowed_ips:
            try:
                self.allowed_ip_objects.append(ipaddress.ip_address(ip))
            except ValueError:
                pass  # Skip invalid IPs
                
        self.allowed_network_objects = []
        for network in self.allowed_networks:
            try:
                self.allowed_network_objects.append(ipaddress.ip_network(network, strict=False))
            except ValueError:
                pass  # Skip invalid networks

    def __call__(self, request):
        # Check if this is an admin request
        if request.path.startswith('/admin/'):
            # Check if IP restriction is enabled
            if not getattr(settings, 'ADMIN_IP_RESTRICTION_ENABLED', True):
                return self.get_response(request)
            
            client_ip = self.get_client_ip(request)
            
            # Block if no IP restrictions are configured (secure by default)
            if not self.allowed_ips and not self.allowed_networks:
                raise PermissionDenied(
                    f"Admin access is restricted by IP. Your IP address ({client_ip}) is not authorized. "
                )
            
            # Check if client IP is allowed
            if not self.is_ip_allowed(client_ip):
                raise PermissionDenied(
                    f"Your IP address ({client_ip}) is not authorized to access the admin interface."
                )
        
        return self.get_response(request)
    
    def get_client_ip(self, request):
        """Get the real client IP address, handling proxies and Cloudflare."""
        # Prefer Cloudflare's header if present
        cf_ip = request.META.get('HTTP_CF_CONNECTING_IP')
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        real_ip = request.META.get('HTTP_X_REAL_IP')
        remote_addr = request.META.get('REMOTE_ADDR')

        # Debug logging to admin_debug.log
        import logging
        logger = logging.getLogger('admin_debug')
        logger.info(f"Admin IP Check - CF-Connecting-IP: {cf_ip}, X-Forwarded-For: {x_forwarded_for}, X-Real-IP: {real_ip}, REMOTE_ADDR: {remote_addr}")
        logger.info(f"All META keys: {list(request.META.keys())}")

        if cf_ip:
            return cf_ip
        if x_forwarded_for:
            return x_forwarded_for.split(',')[0].strip()
        if real_ip:
            return real_ip
        return remote_addr
    
    def is_ip_allowed(self, client_ip):
        """Check if the client IP is in the allowed list."""
        try:
            client_ip_obj = ipaddress.ip_address(client_ip)
        except ValueError:
            return False  # Invalid IP address
        
        # Check exact IP matches
        if client_ip_obj in self.allowed_ip_objects:
            return True
        
        # Check network matches
        for network in self.allowed_network_objects:
            if client_ip_obj in network:
                return True
        
        return False 

class SubdomainRedirectMiddleware:
    """
    Clean middleware for handling subdomain redirects.
    Uses the SubdomainRedirect model from the extensions app.
    Supports both full redirects and path-preserving redirects.
    """
    
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Get the hostname from the request
        hostname = request.get_host().split(':')[0].lower()
        
        # Get the main domain from settings
        main_domain = getattr(settings, 'MAIN_DOMAIN', 'example.com')
        
        # Only redirect if this is a subdomain of the main domain
        if hostname.endswith('.' + main_domain):
            subdomain = hostname.rsplit('.' + main_domain, 1)[0]
            
            # Skip if it's the main domain itself or www
            if subdomain and subdomain not in ['', 'www']:
                # Look for a redirect for this subdomain
                redirect_obj = SubdomainRedirect.get_redirect_for_subdomain(subdomain)
                
                if redirect_obj:
                    # Determine the redirect path
                    if redirect_obj.redirect_type == SubdomainRedirect.REDIRECT_TYPE_FULL:
                        # For full redirects, use object's absolute URL if available, otherwise use redirect_path
                        if redirect_obj.content_object and hasattr(redirect_obj.content_object, 'get_absolute_url'):
                            redirect_path = redirect_obj.content_object.get_absolute_url()
                        else:
                            redirect_path = redirect_obj.redirect_path
                    else:
                        # For path-preserving redirects, keep the same path
                        redirect_path = request.path
                    
                    # Build the full redirect URL to the main domain
                    protocol = 'https' if request.is_secure() else 'http'
                    redirect_url = f"{protocol}://{main_domain}{redirect_path}"
                    
                    # Perform the redirect
                    return redirect(redirect_url, permanent=True)
        
        # No redirect found, continue with normal response
        return self.get_response(request) 