from django.conf import settings

class SEOMixin:
    """
    Mixin that provides SEO methods for models.
    Uses extra_data JSON field for overrides, with fallback to model fields.
    """
    
    # Map SEO property to a list of model fields to check in order
    SEO_FALLBACKS = {
        "title": ["title", "name"],
        "description": ["summary", "description"],
        "keywords": ["keywords"],
        "image": ["image"],
        "author": ["author"],
        "robots": ["robots"],
        "canonical_url": ["canonical_url"],
    }

    def get_seo_value(self, key, default=None):
        """
        Get SEO value with priority: extra_data > _seo mapping > default
        """
        # 1. Check extra_data JSON first
        if hasattr(self, "extra_data") and self.extra_data:
            value = self.extra_data.get(key)
            if value is not None and value != "":
                return value

        # 2. Check _seo mapping from class
        seo_mapping = getattr(self.__class__, '_seo', {})
        if key in seo_mapping:
            field_name = seo_mapping[key]
            if isinstance(field_name, str):
                # It's a field name, get the value
                value = getattr(self, field_name, None)
                if value is not None and value != "":
                    return value
            else:
                # It's a static value
                return field_name

        # 3. Return default
        return default

    def get_seo_title(self):
        """Get SEO title"""
        return self.get_seo_value("title", "")

    def get_seo_description(self):
        """Get SEO description"""
        return self.get_seo_value("description", getattr(settings, 'SEO_DEFAULTS', {}).get('description', ''))

    def get_seo_keywords(self):
        """Get SEO keywords as list"""
        value = self.get_seo_value("keywords", [])
        if isinstance(value, str):
            keywords = [k.strip() for k in value.split(",") if k.strip()]
        elif isinstance(value, list):
            keywords = value
        else:
            keywords = []
        
        # Get default keywords from settings
        default_keywords = getattr(settings, 'SEO_DEFAULTS', {}).get('keywords', [])
        
        # Add dynamic keywords from _seo mapping
        dynamic_keywords = []
        seo_mapping = getattr(self.__class__, '_seo', {})
        
        # Check for keyword fields in _seo mapping
        for key, field_name in seo_mapping.items():
            if key.startswith('keyword_') and isinstance(field_name, str):
                if hasattr(self, field_name):
                    field_value = getattr(self, field_name)
                    
                    # Handle ManyToMany/ForeignKey fields
                    if hasattr(field_value, 'values_list'):
                        if field_value.exists():
                            # Try to get 'title' field, fallback to string representation
                            try:
                                field_keywords = list(field_value.values_list('title', flat=True))
                            except:
                                field_keywords = [str(item) for item in field_value.all()]
                            dynamic_keywords.extend(field_keywords)
                    
                    # Handle CharField/TextField
                    elif isinstance(field_value, str) and field_value.strip():
                        dynamic_keywords.append(field_value.strip())
        
        # Merge all keywords, avoiding duplicates
        all_keywords = keywords + dynamic_keywords
        all_keywords = all_keywords + [kw for kw in default_keywords if kw not in all_keywords]
        
        return all_keywords

    def get_seo_image(self):
        """Get SEO image URL"""
        return self.get_seo_value("image", getattr(settings, 'SEO_DEFAULTS', {}).get('image', ''))

    def get_seo_author(self):
        """Get SEO author"""
        return self.get_seo_value("author", getattr(settings, 'SEO_DEFAULTS', {}).get('author', ''))

    def get_seo_robots(self):
        """Get SEO robots directive"""
        return self.get_seo_value("robots", getattr(settings, 'SEO_DEFAULTS', {}).get('robots', 'index, follow'))

    def get_seo_canonical_url(self):
        """Get SEO canonical URL"""
        return self.get_seo_value("canonical_url", "") 