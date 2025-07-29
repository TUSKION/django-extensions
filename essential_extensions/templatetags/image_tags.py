from django import template
from django.contrib.contenttypes.models import ContentType
from ..models.ImageExtension import ImageExtension

register = template.Library()

@register.simple_tag
def get_images(obj, image_type, images_cache=None):
    """Get images for an object by type string"""
    if not obj:
        print("No object passed to get_images")
        return ImageExtension.objects.none()
    
    # If we have a cache, use it for optimization
    if images_cache and obj.id in images_cache:
        cached_images = images_cache[obj.id]
        # Filter by image type
        filtered_images = [
            img for img in cached_images 
            if img.image_type == image_type
        ]
        
        # If no images found, try custom type
        if not filtered_images:
            filtered_images = [
                img for img in cached_images 
                if img.image_type == 'other' and img.custom_type == image_type
            ]
        
        # Sort by order and featured status
        filtered_images.sort(key=lambda x: (x.order, -x.is_featured))
        return filtered_images
    
    # Fallback to database query if no cache
    try:
        content_type = ContentType.objects.get_for_model(obj)
        images = ImageExtension.objects.filter(
            object_id=obj.pk,
            image_type=image_type
        ).order_by('order', '-is_featured')

        # If no images found, try to get custom images
        if images.count() == 0:
            images = ImageExtension.objects.filter(
                object_id=obj.pk,
                image_type='other',
                custom_type=image_type
            ).order_by('order', '-is_featured')
        return images

    except Exception as e:
        print(f"Error getting images: {e}")
        return ImageExtension.objects.none()

@register.simple_tag
def get_image(obj, image_type, featured=None, images_cache=None):
    """Get a single image for an object by type string"""
    if not obj:
        return None
    
    # If we have a cache, use it for optimization
    if images_cache is not None and obj.id in images_cache:
        cached_images = images_cache[obj.id]
        # Filter by image type
        filtered_images = [
            img for img in cached_images 
            if img.image_type == image_type
        ]
        # If no images found, try custom type
        if not filtered_images:
            filtered_images = [
                img for img in cached_images 
                if img.image_type == 'other' and img.custom_type == image_type
            ]
        # Filter by featured status if specified
        if featured is not None:
            filtered_images = [
                img for img in filtered_images 
                if img.is_featured == featured
            ]
        # Sort by featured first, then by order, then by ID
        filtered_images.sort(key=lambda x: (-x.is_featured, x.order, x.id))
        # Return the first image or None
        return filtered_images[0] if filtered_images else None
    
    # Fallback to database query ONLY if no cache is provided
    if images_cache is None:
        try:
            content_type = ContentType.objects.get_for_model(obj)
            queryset = ImageExtension.objects.filter(
                object_id=obj.pk,
                image_type=image_type
            )
            # If featured is specified, filter by featured status
            if featured is not None:
                queryset = queryset.filter(is_featured=featured)
            # Order by featured first, then by order, then by ID
            queryset = queryset.order_by('-is_featured', 'order', 'id')
            # Return the first image or None
            return queryset.first()
        except Exception as e:
            return None
    # If cache is provided but no image found, return None without querying DB
    return None

@register.simple_tag
def get_featured_image(obj, image_type, images_cache=None):
    """Get the featured image for an object by type string"""
    return get_image(obj, image_type, featured=True, images_cache=images_cache)

@register.simple_tag
def get_any_image(obj, image_type, images_cache=None):
    """Get any image for an object by type string (featured or not)"""
    return get_image(obj, image_type, featured=None, images_cache=images_cache)
