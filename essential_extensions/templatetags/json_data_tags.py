from django import template
from django.utils.safestring import mark_safe
import json
import re

register = template.Library()


@register.filter
def json_get(obj, key, field_name='extra_data'):
    """Get a value from a JSON field by key"""
    # Handle case where obj is already the JSON data
    if isinstance(obj, dict):
        data = obj
    else:
        # Handle case where obj is the model instance
        if not obj or not hasattr(obj, field_name) or not getattr(obj, field_name):
            return None
        
        field_value = getattr(obj, field_name)
        if isinstance(field_value, str):
            try:
                data = json.loads(field_value)
            except (json.JSONDecodeError, TypeError):
                return None
        else:
            data = field_value
    
    return data.get(key)


@register.filter
def json_has_key(obj, key, field_name='extra_data'):
    """Check if a JSON field has a specific key"""
    # Handle case where obj is already the JSON data
    if isinstance(obj, dict):
        data = obj
    else:
        # Handle case where obj is the model instance
        if not obj or not hasattr(obj, field_name) or not getattr(obj, field_name):
            return False
        
        field_value = getattr(obj, field_name)
        if isinstance(field_value, str):
            try:
                data = json.loads(field_value)
            except (json.JSONDecodeError, TypeError):
                return False
        else:
            data = field_value
    
    return key in data


@register.filter
def json_length(value, key=None, field_name='extra_data'):
    """
    Get the length of a JSON array or object.
    
    Usage:
    {{ project.extra_data|json_length:"features" }}  # Length of features array
    {{ project.extra_data|json_length }}  # Length of root object
    """
    if key:
        value = json_get(value, key, field_name)
    
    if isinstance(value, (list, dict)):
        return len(value)
    return 0


@register.filter
def json_keys(value, key=None, field_name='extra_data'):
    """
    Get all keys from a JSON object.
    
    Usage:
    {{ project.extra_data|json_keys:"tech_stack" }}
    """
    if key:
        value = json_get(value, key, field_name)
    
    if isinstance(value, dict):
        return list(value.keys())
    return []


@register.filter
def json_values(value, key=None, field_name='extra_data'):
    """
    Get all values from a JSON object or array.
    
    Usage:
    {{ project.extra_data|json_values:"features" }}
    """
    if key:
        value = json_get(value, key, field_name)
    
    if isinstance(value, dict):
        return list(value.values())
    elif isinstance(value, list):
        return value
    return []


@register.filter
def json_items(obj, key=None, field_name='extra_data'):
    """Get items from a JSON field, optionally filtered by a key"""
    # Handle case where obj is already the JSON data
    if isinstance(obj, dict):
        data = obj
    else:
        # Handle case where obj is the model instance
        if not obj or not hasattr(obj, field_name) or not getattr(obj, field_name):
            return {}
        
        field_value = getattr(obj, field_name)
        if isinstance(field_value, str):
            try:
                data = json.loads(field_value)
            except (json.JSONDecodeError, TypeError):
                return {}
        else:
            data = field_value
    
    if key:
        data = data.get(key, {})
    
    if isinstance(data, dict):
        return data.items()
    return {}


@register.filter
def json_pretty(value):
    """
    Format JSON with proper indentation for display.
    
    Usage:
    <pre>{{ project.extra_data|json_pretty }}</pre>
    """
    if not value:
        return ""
    
    try:
        if isinstance(value, str):
            parsed = json.loads(value)
        else:
            parsed = value
        return json.dumps(parsed, indent=2, ensure_ascii=False)
    except (json.JSONDecodeError, TypeError):
        return str(value)


@register.filter
def json_type(value):
    """Get the type of a JSON value as a string"""
    if value is None:
        return "null"
    elif isinstance(value, bool):
        return "boolean"
    elif isinstance(value, int):
        return "number"
    elif isinstance(value, float):
        return "number"
    elif isinstance(value, str):
        return "string"
    elif isinstance(value, list):
        return "array"
    elif isinstance(value, dict):
        return "object"
    else:
        return "unknown"


@register.filter
def json_slice(value, key, slice_spec, field_name='extra_data'):
    """
    Slice a JSON array.
    
    Usage:
    {{ project.extra_data|json_slice:"features:0:3" }}  # First 3 items
    {{ project.extra_data|json_slice:"tags:-5:" }}  # Last 5 items
    """
    if not slice_spec or ':' not in slice_spec:
        return []
    
    array_data = json_get(value, key, field_name)
    if not isinstance(array_data, list):
        return []
    
    try:
        parts = slice_spec.split(':')
        if len(parts) == 2:
            start = int(parts[0]) if parts[0] else 0
            end = int(parts[1]) if parts[1] else len(array_data)
        elif len(parts) == 3:
            start = int(parts[0]) if parts[0] else 0
            end = int(parts[1]) if parts[1] else len(array_data)
            step = int(parts[2]) if parts[2] else 1
            return array_data[start:end:step]
        else:
            return []
        
        return array_data[start:end]
    except (ValueError, IndexError):
        return []


@register.filter
def json_search(value, search_term, key=None, field_name='extra_data'):
    """
    Search for values in JSON that contain the search term.
    
    Usage:
    {{ project.extra_data|json_search:"Unity" }}  # Search all values
    {{ project.extra_data|json_search:"C#" "tech_stack.languages" }}  # Search specific array
    """
    if key:
        value = json_get(value, key, field_name)
    
    if not value:
        return []
    
    results = []
    
    def search_recursive(obj, path=""):
        if isinstance(obj, dict):
            for k, v in obj.items():
                current_path = f"{path}.{k}" if path else k
                search_recursive(v, current_path)
        elif isinstance(obj, list):
            for i, v in enumerate(obj):
                current_path = f"{path}[{i}]"
                search_recursive(v, current_path)
        elif isinstance(obj, str) and search_term.lower() in obj.lower():
            results.append({
                'value': obj,
                'path': path,
                'type': 'string'
            })
        elif isinstance(obj, (int, float)) and str(search_term) in str(obj):
            results.append({
                'value': obj,
                'path': path,
                'type': 'number'
            })
    
    search_recursive(value)
    return results


@register.filter
def json_to_table(value, key=None, field_name='extra_data'):
    """
    Convert JSON object to HTML table.
    
    Usage:
    {{ project.extra_data|json_to_table:"tech_stack" }}
    """
    if key:
        value = json_get(value, key, field_name)
    
    if not isinstance(value, dict):
        return ""
    
    html = '<table class="json-table">'
    html += '<thead><tr><th>Key</th><th>Value</th><th>Type</th></tr></thead>'
    html += '<tbody>'
    
    for k, v in value.items():
        html += f'<tr>'
        html += f'<td><strong>{k}</strong></td>'
        
        if isinstance(v, (dict, list)):
            html += f'<td><code>{json.dumps(v, ensure_ascii=False)}</code></td>'
        else:
            html += f'<td>{v}</td>'
        
        html += f'<td><span class="json-type">{json_type(v)}</span></td>'
        html += f'</tr>'
    
    html += '</tbody></table>'
    
    # Add some basic CSS
    html += '''
    <style>
    .json-table {
        border-collapse: collapse;
        width: 100%;
        margin: 10px 0;
        font-size: 14px;
    }
    .json-table th, .json-table td {
        border: 1px solid #ddd;
        padding: 8px 12px;
        text-align: left;
    }
    .json-table th {
        background-color: #f8f9fa;
        font-weight: 600;
    }
    .json-table code {
        background: #f8f9fa;
        padding: 2px 4px;
        border-radius: 3px;
        font-size: 12px;
    }
    .json-type {
        background: #e9ecef;
        padding: 2px 6px;
        border-radius: 3px;
        font-size: 11px;
        font-weight: 500;
        color: #6c757d;
    }
    </style>
    '''
    
    return mark_safe(html)


@register.filter
def json_to_list(value, key=None, field_name='extra_data'):
    """
    Convert JSON array to HTML list.
    
    Usage:
    {{ project.extra_data|json_to_list:"features" }}
    """
    if key:
        value = json_get(value, key, field_name)
    
    if not isinstance(value, list):
        return ""
    
    html = '<ul class="json-list">'
    
    for item in value:
        if isinstance(item, dict):
            html += '<li><code>' + json.dumps(item, ensure_ascii=False) + '</code></li>'
        else:
            html += f'<li>{item}</li>'
    
    html += '</ul>'
    
    # Add some basic CSS
    html += '''
    <style>
    .json-list {
        margin: 10px 0;
        padding-left: 20px;
    }
    .json-list li {
        margin: 5px 0;
    }
    .json-list code {
        background: #f8f9fa;
        padding: 2px 4px;
        border-radius: 3px;
        font-size: 12px;
    }
    </style>
    '''
    
    return mark_safe(html)


@register.simple_tag
def json_default(value, default_value=""):
    """
    Provide a default value if JSON value is None or empty.
    
    Usage:
    {% json_default project.extra_data|json_get:"tech_stack.engine" "Not specified" %}
    """
    if value is None or value == "":
        return default_value
    return value


@register.filter
def json_join(value, separator=", "):
    """Join array values with a separator"""
    if isinstance(value, list):
        return separator.join(str(item) for item in value)
    return str(value)


@register.simple_tag
def get_json_displays(obj, context='', field_name='extra_data'):
    """Get display elements from JSON field (replaces get_displays)"""
    if not obj or not hasattr(obj, field_name) or not getattr(obj, field_name):
        return []
    
    field_value = getattr(obj, field_name)
    if isinstance(field_value, str):
        try:
            data = json.loads(field_value)
        except (json.JSONDecodeError, TypeError):
            return []
    else:
        data = field_value
    
    # Look for displays in the JSON structure
    displays = []
    
    # Check for direct 'displays' key
    if 'displays' in data:
        display_data = data['displays']
        if isinstance(display_data, list):
            for item in display_data:
                if isinstance(item, dict) and item.get('is_active', True):
                    if not context or item.get('context') == context:
                        displays.append(item)
        elif isinstance(display_data, dict):
            for key, item in display_data.items():
                if isinstance(item, dict) and item.get('is_active', True):
                    if not context or item.get('context') == context:
                        item['key'] = key  # Add key for consistency
                        displays.append(item)
    
    # Check for context-specific keys (e.g., 'featured_media')
    if context and context in data:
        context_data = data[context]
        if isinstance(context_data, list):
            for item in context_data:
                if isinstance(item, dict) and item.get('is_active', True):
                    displays.append(item)
        elif isinstance(context_data, dict):
            for key, item in context_data.items():
                if isinstance(item, dict) and item.get('is_active', True):
                    item['key'] = key
                    displays.append(item)
    
    # Sort by order if available
    displays.sort(key=lambda x: x.get('order', 0))
    return displays


@register.simple_tag
def get_json_display(obj, key, context='', field_name='extra_data'):
    """Get a specific display element from JSON field (replaces get_display)"""
    displays = get_json_displays(obj, context, field_name)
    for display in displays:
        if display.get('key') == key:
            return display
    return None


@register.simple_tag
def get_json_url(obj, key, context='', field_name='extra_data'):
    """Get URL from a JSON display element (replaces get_url)"""
    display = get_json_display(obj, key, context, field_name)
    if display:
        return display.get('url') or display.get('value')
    return None


@register.simple_tag
def get_json_text(obj, key, context='', default='', field_name='extra_data'):
    """Get text from a JSON display element (replaces get_text)"""
    display = get_json_display(obj, key, context, field_name)
    if display:
        return display.get('text') or display.get('value', default)
    return default


@register.filter
def json_friendly_name(value, key=None):
    """Get a friendly name for a JSON value, with fallback to key name"""
    if key:
        # If we have a key, try to get the friendly_name from the value
        if isinstance(value, dict) and 'friendly_name' in value:
            return value['friendly_name']
        # Fallback to the key name, formatted nicely
        return key.replace('_', ' ').title()
    else:
        # If no key provided, return the value itself
        return str(value)


@register.filter
def json_display_value(value, key=None):
    """Get the display value from JSON, handling friendly_name and value fields"""
    if isinstance(value, dict):
        # If it's an object, look for display fields in order of preference
        if 'value' in value:
            display_value = value['value']
            # If the value is an array, join it with commas
            if isinstance(display_value, list):
                return ', '.join(str(item) for item in display_value)
            return display_value
        elif 'text' in value:
            return value['text']
        elif 'display_value' in value:
            display_value = value['display_value']
            # If the value is an array, join it with commas
            if isinstance(display_value, list):
                return ', '.join(str(item) for item in display_value)
            return display_value
        else:
            # If no display field, return the first non-metadata field
            metadata_fields = {'friendly_name', 'display_type', 'order', 'is_active', 'context'}
            for k, v in value.items():
                if k not in metadata_fields:
                    if isinstance(v, list):
                        return ', '.join(str(item) for item in v)
                    return v
            return str(value)
    elif isinstance(value, list):
        # If it's a list, join with commas
        return ', '.join(str(item) for item in value)
    else:
        # If it's a simple value, return it directly
        return value


@register.filter
def json_metadata(value, key=None):
    """Get metadata fields from JSON (friendly_name, display_type, etc.)"""
    if isinstance(value, dict):
        metadata = {}
        metadata_fields = {'friendly_name', 'display_type', 'order', 'is_active', 'context', 'description'}
        for field in metadata_fields:
            if field in value:
                metadata[field] = value[field]
        return metadata
    return {}


@register.filter
def youtube_embed_url(url):
    """Convert YouTube URL to embed URL (moved from display_tags)"""
    if not url:
        return None
    
    import re
    
    # YouTube video ID patterns
    patterns = [
        r'(?:youtube\.com\/watch\?v=|youtu\.be\/|youtube\.com\/embed\/)([^&\n?#]+)',
    ]
    
    for pattern in patterns:
        match = re.search(pattern, url)
        if match:
            video_id = match.group(1)
            # Clean the video ID (remove any remaining parameters)
            video_id = video_id.split('&')[0].split('?')[0]
            return f'https://www.youtube.com/embed/{video_id}?autoplay=0&rel=0&modestbranding=1&enablejsapi=1'
    
    return url
