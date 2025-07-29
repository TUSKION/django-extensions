from django.db import models
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _


class SubdomainRedirect(models.Model):
    """
    Model for handling subdomain redirects.
    Can be attached to any model that has a subdomain field, or used standalone.
    """
    
    # Redirect types
    REDIRECT_TYPE_FULL = 'full'
    REDIRECT_TYPE_PATH_PRESERVE = 'path_preserve'
    
    REDIRECT_TYPE_CHOICES = [
        (REDIRECT_TYPE_FULL, _('Full Redirect')),
        (REDIRECT_TYPE_PATH_PRESERVE, _('Path Preserving Redirect')),
    ]
    
    # Optional generic foreign key to any model
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE, null=True, blank=True)
    object_id = models.PositiveIntegerField(null=True, blank=True)
    content_object = GenericForeignKey('content_type', 'object_id')
    
    # Subdomain configuration
    subdomain = models.CharField(
        max_length=100,
        unique=True,
        help_text=_("The subdomain (e.g., 'gamex' for gamex.example.com)")
    )
    
    # Redirect configuration
    redirect_type = models.CharField(
        max_length=20,
        choices=REDIRECT_TYPE_CHOICES,
        default=REDIRECT_TYPE_FULL,
        help_text=_("Full: redirect to specific path. Path Preserving: keep the same path on main domain.")
    )
    
    redirect_path = models.CharField(
        max_length=255,
        blank=True,
        help_text=_("For Full Redirect: the path to redirect to (e.g., '/game/game-x/'). For Path Preserving: leave blank.")
    )
    
    # Status
    is_active = models.BooleanField(
        default=True,
        help_text=_("Whether this redirect is active")
    )
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = _("Subdomain Redirect")
        verbose_name_plural = _("Subdomain Redirects")
        ordering = ['subdomain']
        indexes = [
            models.Index(fields=['subdomain']),
            models.Index(fields=['is_active']),
            models.Index(fields=['content_type', 'object_id']),
        ]
    
    def __str__(self):
        if self.redirect_type == self.REDIRECT_TYPE_FULL:
            return f"{self.subdomain} &rarr; {self.redirect_path}"
        else:
            return f"{self.subdomain} &rarr; preserve path"
    
    def clean(self):
        """Validate the subdomain format and redirect configuration"""
        if self.subdomain:
            # Remove any domain parts if accidentally included
            self.subdomain = self.subdomain.split('.')[0].lower()
            
            # Basic validation
            if not self.subdomain.isalnum() and '-' not in self.subdomain:
                raise ValidationError(_("Subdomain can only contain letters, numbers, and hyphens"))
            
            if len(self.subdomain) < 2:
                raise ValidationError(_("Subdomain must be at least 2 characters long"))
        
        # Validate redirect configuration
        if self.redirect_type == self.REDIRECT_TYPE_FULL and not self.redirect_path:
            raise ValidationError(_("Full redirect requires a redirect path"))
        
        if self.redirect_type == self.REDIRECT_TYPE_PATH_PRESERVE and self.redirect_path:
            raise ValidationError(_("Path preserving redirect should not have a redirect path"))
    
    def get_redirect_url(self, request_path='/'):
        """
        Get the redirect URL based on the redirect type and current request path.
        
        Args:
            request_path: The current request path (e.g., '/lol/')
        
        Returns:
            The URL to redirect to
        """
        if self.redirect_type == self.REDIRECT_TYPE_FULL:
            return self.redirect_path
        else:
            # Path preserving: keep the same path on main domain
            return request_path
    
    @classmethod
    def get_redirect_for_subdomain(cls, subdomain):
        """Get the active redirect for a given subdomain"""
        try:
            return cls.objects.get(
                subdomain=subdomain.lower(),
                is_active=True
            )
        except cls.DoesNotExist:
            return None 