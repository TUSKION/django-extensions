from django import forms
from django.core.exceptions import ValidationError
from django.utils.safestring import mark_safe
import json


class DynamicJSONEditorWidget(forms.Widget):
    """Dynamic JSON editor that automatically generates form fields for any JSON structure"""
    
    def __init__(self, attrs=None):
        super().__init__(attrs)
    
    def format_value(self, value):
        """Format the JSON value for display"""
        if value is None or value == '':
            return '{}'
        if isinstance(value, str):
            try:
                parsed = json.loads(value)
                return json.dumps(parsed, indent=2)
            except json.JSONDecodeError:
                return value
        return json.dumps(value, indent=2)
    
    def render(self, name, value, attrs=None, renderer=None):
        """Render the dynamic JSON editor"""
        formatted_value = self.format_value(value)
        
        html = f"""
        <div class="dynamic-json-editor" data-field-name="{name}">
            <div class="json-editor-header">
                <div class="json-controls">
                    <button type="button" class="btn btn-primary add-field-btn">+ Add Field</button>
                    <button type="button" class="btn btn-secondary expand-all-btn">Expand All</button>
                    <button type="button" class="btn btn-secondary collapse-all-btn">Collapse All</button>
                    <button type="button" class="btn btn-info paste-json-btn">Paste JSON</button>
                    <button type="button" class="btn btn-warning clear-all-btn">Clear All</button>
                </div>
                <div class="json-tabs">
                    <button type="button" class="json-tab active" data-tab="tree">Tree View</button>
                    <button type="button" class="json-tab" data-tab="json">Raw JSON</button>
                </div>
            </div>
            
            <div class="json-editor-content">
                <!-- Tree View Tab -->
                <div class="json-tab-content active" data-tab="tree">
                    <div class="json-tree" data-path="">
                        <div class="json-tree-content"></div>
                    </div>
                </div>
                
                <!-- Raw JSON Tab -->
                <div class="json-tab-content" data-tab="json">
                    <textarea class="json-textarea" rows="20" cols="80">{formatted_value}</textarea>
                </div>
            </div>
            
            <!-- Hidden input for form submission -->
            <input type="hidden" name="{name}" value='{formatted_value}' class="json-hidden-input">
        </div>
        
        <style>
        .dynamic-json-editor {{
            border: 1px solid #ddd;
            border-radius: 4px;
            margin: 10px 0;
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
        }}
        
        .dynamic-json-editor .json-editor-header {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 15px;
            border-bottom: 1px solid #ddd;
            background: #f8f9fa;
        }}
        
        .dynamic-json-editor .json-controls {{
            display: flex;
            gap: 10px;
        }}
        
        .dynamic-json-editor .btn {{
            padding: 8px 16px;
            border: 1px solid #ddd;
            border-radius: 4px;
            background: white;
            cursor: pointer;
            font-size: 14px;
            transition: all 0.2s;
        }}
        
        .dynamic-json-editor .btn:hover {{
            background: #f8f9fa;
        }}
        
        .dynamic-json-editor .btn-primary {{
            background: #007cba;
            color: white;
            border-color: #007cba;
        }}
        
        .dynamic-json-editor .btn-primary:hover {{
            background: #005a87;
        }}
        
        .dynamic-json-editor .btn-secondary {{
            background: #6c757d;
            color: white;
            border-color: #6c757d;
        }}
        
        .dynamic-json-editor .btn-secondary:hover {{
            background: #545b62;
        }}
        
        .dynamic-json-editor .btn-info {{
            background: #17a2b8;
            color: white;
            border-color: #17a2b8;
        }}
        
        .dynamic-json-editor .btn-info:hover {{
            background: #138496;
        }}
        
        .dynamic-json-editor .btn-warning {{
            background: #ffc107;
            color: #212529;
            border-color: #ffc107;
        }}
        
        .dynamic-json-editor .btn-warning:hover {{
            background: #e0a800;
        }}
        
        .dynamic-json-editor .json-tabs {{
            display: flex;
            gap: 5px;
        }}
        
        .dynamic-json-editor .json-tab {{
            padding: 8px 16px;
            border: 1px solid #ddd;
            background: white;
            cursor: pointer;
            border-radius: 4px 4px 0 0;
            margin-bottom: -1px;
        }}
        
        .dynamic-json-editor .json-tab.active {{
            background: white;
            border-bottom-color: white;
        }}
        
        .dynamic-json-editor .json-tab-content {{
            display: none !important;
            padding: 20px;
        }}
        
        .dynamic-json-editor .json-tab-content.active {{
            display: block !important;
        }}
        
        .dynamic-json-editor .json-tree-content {{
            min-height: 200px;
        }}
        
        .dynamic-json-editor .json-item {{
            margin: 3px 0;
            padding: 8px;
            border: 1px solid #e9ecef;
            border-radius: 4px;
            background: white;
        }}
        
        .dynamic-json-editor .json-item-header {{
            display: flex;
            align-items: center;
            gap: 8px;
            margin-bottom: 8px;
        }}
        
        .dynamic-json-editor .collapse-btn {{
            background: none;
            border: none;
            cursor: pointer;
            padding: 2px 4px;
            border-radius: 3px;
            transition: all 0.2s;
            min-width: 20px;
            height: 20px;
            display: flex;
            align-items: center;
            justify-content: center;
        }}
        
        .dynamic-json-editor .collapse-btn:hover {{
            background: #e9ecef;
        }}
        
        .dynamic-json-editor .collapse-btn.hidden {{
            display: none;
        }}
        
        .dynamic-json-editor .collapse-icon {{
            font-size: 12px;
            transition: transform 0.2s;
        }}
        
        .dynamic-json-editor .collapse-btn[data-collapsed="true"] .collapse-icon {{
            transform: rotate(-90deg);
        }}
        
        .dynamic-json-editor .json-item-content.collapsible {{
            transition: all 0.3s ease;
            overflow: hidden;
        }}
        
        .dynamic-json-editor .json-item-content.collapsible.collapsed {{
            max-height: 0;
            padding: 0;
            margin: 0;
            opacity: 0;
        }}
        
        .dynamic-json-editor .json-item-key {{
            font-weight: 600;
            color: #495057;
            min-width: 100px;
            font-size: 13px;
        }}
        
        .dynamic-json-editor .json-item-type {{
            font-size: 11px;
            color: #6c757d;
            background: #e9ecef;
            padding: 2px 5px;
            border-radius: 3px;
            font-weight: 500;
        }}
        
        .dynamic-json-editor .json-item-controls {{
            margin-left: auto;
            display: flex;
            gap: 4px;
        }}
        
        .dynamic-json-editor .json-item-controls button {{
            padding: 3px 6px;
            border: 1px solid #ddd;
            background: white;
            border-radius: 3px;
            cursor: pointer;
            font-size: 11px;
            transition: all 0.2s;
        }}
        
        .dynamic-json-editor .json-item-controls button:hover {{
            background: #f8f9fa;
            transform: translateY(-1px);
        }}
        
        .dynamic-json-editor .json-item-controls .remove-btn {{
            background: #dc3545;
            color: white;
            border-color: #dc3545;
        }}
        
        .dynamic-json-editor .json-item-controls .remove-btn:hover {{
            background: #c82333;
        }}
        
        .dynamic-json-editor .json-item-controls .change-type-btn {{
            background: #6c757d;
            color: white;
            border-color: #6c757d;
        }}
        
        .dynamic-json-editor .json-item-controls .change-type-btn:hover {{
            background: #545b62;
        }}
        
        .dynamic-json-editor .json-item-content {{
            margin-left: 16px;
            padding-top: 4px;
        }}
        
        .dynamic-json-editor .json-input {{
            width: 200px;
            max-width: 100%;
            padding: 6px 10px;
            border: 1px solid #ced4da;
            border-radius: 4px;
            font-size: 13px;
            margin: 3px 0;
            background: #fff;
            transition: all 0.2s;
        }}
        
        .dynamic-json-editor .json-input:focus {{
            outline: none;
            border-color: #007cba;
            box-shadow: 0 0 0 2px rgba(0,124,186,0.2);
            background: #fff;
        }}
        
        .dynamic-json-editor .json-input:hover {{
            border-color: #adb5bd;
        }}
        
        .dynamic-json-editor .json-textarea {{
            width: 100%;
            border: 1px solid #ced4da;
            border-radius: 4px;
            padding: 10px;
            font-family: 'Monaco', 'Menlo', 'Ubuntu Mono', monospace;
            font-size: 13px;
            line-height: 1.4;
        }}
        
        .dynamic-json-editor .json-array-item {{
            border: 1px solid #dee2e6;
            border-radius: 4px;
            padding: 6px;
            margin: 3px 0;
            background: #f8f9fa;
        }}
        
        .dynamic-json-editor .json-object-item {{
            border: 1px solid #dee2e6;
            border-radius: 4px;
            padding: 6px;
            margin: 3px 0;
            background: #f8f9fa;
        }}
        
        .dynamic-json-editor .add-item-btn {{
            background: #28a745;
            color: white;
            border: none;
            padding: 6px 12px;
            border-radius: 4px;
            cursor: pointer;
            font-size: 12px;
            margin: 6px 0;
            transition: all 0.2s;
        }}
        
        .dynamic-json-editor .add-item-btn:hover {{
            background: #218838;
            transform: translateY(-1px);
        }}
        
        .dynamic-json-editor .inline-form {{
            background: #f8f9fa;
            border: 1px solid #dee2e6;
            border-radius: 4px;
            padding: 12px;
            margin: 8px 0;
        }}
        
        .dynamic-json-editor .form-row {{
            display: flex;
            align-items: center;
            gap: 8px;
            flex-wrap: wrap;
        }}
        
        .dynamic-json-editor .form-row label {{
            font-size: 13px;
            font-weight: 500;
            color: #495057;
            margin: 0;
            white-space: nowrap;
        }}
        
        .dynamic-json-editor .form-input {{
            width: 150px;
            max-width: 100%;
            padding: 6px 10px;
            border: 1px solid #ced4da;
            border-radius: 4px;
            font-size: 13px;
            background: #fff;
            transition: all 0.2s;
        }}
        
        .dynamic-json-editor .form-input:focus {{
            outline: none;
            border-color: #007cba;
            box-shadow: 0 0 0 2px rgba(0,124,186,0.2);
        }}
        
        .dynamic-json-editor .form-select {{
            width: 120px;
            max-width: 100%;
            padding: 6px 10px;
            border: 1px solid #ced4da;
            border-radius: 4px;
            font-size: 13px;
            background: #fff;
            transition: all 0.2s;
        }}
        
        .dynamic-json-editor .form-select:focus {{
            outline: none;
            border-color: #007cba;
            box-shadow: 0 0 0 2px rgba(0,124,186,0.2);
        }}
        
        .dynamic-json-editor .btn-success {{
            background: #28a745;
            color: white;
            border-color: #28a745;
        }}
        
        .dynamic-json-editor .btn-success:hover {{
            background: #218838;
        }}
        
        .dynamic-json-editor .json-feedback {{
            padding: 10px 15px;
            margin: 10px 0;
            border-radius: 4px;
            font-size: 14px;
            font-weight: 500;
            animation: slideIn 0.3s ease-out;
        }}
        
        .dynamic-json-editor .json-feedback-success {{
            background: #d4edda;
            color: #155724;
            border: 1px solid #c3e6cb;
        }}
        
        .dynamic-json-editor .json-feedback-error {{
            background: #f8d7da;
            color: #721c24;
            border: 1px solid #f5c6cb;
        }}
        
        @keyframes slideIn {{
            from {{
                opacity: 0;
                transform: translateY(-10px);
            }}
            to {{
                opacity: 1;
                transform: translateY(0);
            }}
        }}
        </style>
        
        <script>
        document.addEventListener('DOMContentLoaded', function() {{
            const container = document.querySelector('.dynamic-json-editor[data-field-name="{name}"]');
            if (!container) return;
            
            const hiddenInput = container.querySelector('.json-hidden-input');
            const textarea = container.querySelector('.json-textarea');
            const treeContent = container.querySelector('.json-tree-content');
            let currentData = {{}};
            
            // Get storage key for this specific editor instance
            const storageKey = 'json-editor-expanded-' + name;
            
            // Initialize data
            try {{
                currentData = JSON.parse(hiddenInput.value || '{{}}');
            }} catch (e) {{
                currentData = {{}};
            }}
            
            // Update hidden input
            function updateHiddenInput() {{
                hiddenInput.value = JSON.stringify(currentData, null, 2);
            }}
            
            // Save expanded state to localStorage
            function saveExpandedState(path, isExpanded) {{
                try {{
                    let expandedStates = {{}};
                    const stored = localStorage.getItem(storageKey);
                    if (stored) {{
                        expandedStates = JSON.parse(stored);
                    }}
                    expandedStates[path] = isExpanded;
                    localStorage.setItem(storageKey, JSON.stringify(expandedStates));
                }} catch (e) {{
                    // localStorage might be disabled, ignore
                }}
            }}
            
            // Render tree view
            function renderTree(data, parentElement, path = '') {{
                // Store current expanded states before clearing
                if (parentElement.children.length > 0) {{
                    // Capture states from ALL nested levels, not just direct children
                    const allContentElements = parentElement.querySelectorAll('.json-item-content');
                    const currentStates = {{}};
                    allContentElements.forEach(content => {{
                        const itemPath = content.dataset.path;
                        if (itemPath) {{
                            currentStates[itemPath] = !content.classList.contains('collapsed');
                        }}
                    }});
                    // Save to localStorage
                    try {{
                        localStorage.setItem(storageKey, JSON.stringify(currentStates));
                    }} catch (e) {{
                        // localStorage might be disabled, ignore
                    }}
                }}
                
                parentElement.innerHTML = '';
                
                if (Object.keys(data).length === 0) {{
                    parentElement.innerHTML = '<div class="json-item"><em>No data. Click "Add Field" to get started.</em></div>';
                    return;
                }}
                
                Object.entries(data).forEach(([key, value]) => {{
                    const itemDiv = document.createElement('div');
                    itemDiv.className = 'json-item';
                    
                    const currentPath = path ? path + '.' + key : key;
                    const valueType = Array.isArray(value) ? 'array' : typeof value;
                    const isComplex = valueType === 'object' || valueType === 'array';
                    
                    // Load expanded states from localStorage
                    let expandedStates = {{}};
                    try {{
                        const stored = localStorage.getItem(storageKey);
                        if (stored) {{
                            expandedStates = JSON.parse(stored);
                        }}
                    }} catch (e) {{
                        // localStorage might be disabled, ignore
                    }}
                    
                    // Check if this item was previously expanded
                    const wasExpanded = expandedStates[currentPath];
                    
                    // For nested items, also check if parent was expanded
                    let parentWasExpanded = false;
                    if (path && currentPath !== path) {{
                        parentWasExpanded = expandedStates[path];
                    }}
                    
                    // Default behavior: expand arrays/objects unless explicitly collapsed
                    // Only collapse if it was explicitly saved as collapsed in localStorage
                    const shouldBeExpanded = wasExpanded !== false; // true if expanded, undefined, or not in storage
                    
                    itemDiv.innerHTML = 
                        '<div class="json-item-header">' +
                            '<button type="button" class="collapse-btn ' + (isComplex ? '' : 'hidden') + '" data-collapsed="' + (shouldBeExpanded ? 'false' : 'true') + '">' +
                                '<span class="collapse-icon">' + (shouldBeExpanded ? '▼' : '▶') + '</span>' +
                            '</button>' +
                            '<span class="json-item-key">' + key + '</span>' +
                            '<span class="json-item-type">' + valueType + '</span>' +
                            '<div class="json-item-controls">' +
                                '<button type="button" class="edit-key-btn" data-path="' + currentPath + '">Edit Key</button>' +
                                '<button type="button" class="change-type-btn" data-path="' + currentPath + '">Change Type</button>' +
                                '<button type="button" class="remove-btn" data-path="' + currentPath + '">Remove</button>' +
                            '</div>' +
                        '</div>' +
                        '<div class="json-item-content ' + (isComplex ? 'collapsible' : '') + (shouldBeExpanded ? '' : ' collapsed') + '" data-path="' + currentPath + '"></div>';
                    
                    parentElement.appendChild(itemDiv);
                    
                    const contentDiv = itemDiv.querySelector('.json-item-content');
                    renderValue(value, contentDiv, currentPath);
                    
                    // Add event listeners
                    itemDiv.querySelector('.remove-btn').addEventListener('click', function() {{
                        const pathParts = currentPath.split('.');
                        let obj = currentData;
                        for (let i = 0; i < pathParts.length - 1; i++) {{
                            obj = obj[pathParts[i]];
                        }}
                        delete obj[pathParts[pathParts.length - 1]];
                        renderTree(currentData, treeContent);
                        updateHiddenInput();
                    }});
                    
                    // Add change type functionality
                    itemDiv.querySelector('.change-type-btn').addEventListener('click', function() {{
                        // Create inline form for changing type
                        const formDiv = document.createElement('div');
                        formDiv.className = 'inline-form change-type-form';
                        formDiv.innerHTML = 
                            '<div class="form-row">' +
                                '<label>Change type to:</label>' +
                                '<select class="form-select" id="new-type-select">' +
                                    '<option value="string"' + (valueType === 'string' ? ' selected' : '') + '>String</option>' +
                                    '<option value="number"' + (valueType === 'number' ? ' selected' : '') + '>Number</option>' +
                                    '<option value="boolean"' + (valueType === 'boolean' ? ' selected' : '') + '>Boolean</option>' +
                                    '<option value="object"' + (valueType === 'object' ? ' selected' : '') + '>Object</option>' +
                                    '<option value="array"' + (valueType === 'array' ? ' selected' : '') + '>Array</option>' +
                                '</select>' +
                                '<button type="button" class="btn btn-success save-btn">Change</button>' +
                                '<button type="button" class="btn btn-secondary cancel-btn">Cancel</button>' +
                            '</div>';
                        
                        // Insert form after the header
                        const header = itemDiv.querySelector('.json-item-header');
                        header.parentNode.insertBefore(formDiv, header.nextSibling);
                        
                        // Focus on the select
                        formDiv.querySelector('#new-type-select').focus();
                        
                        // Handle save
                        formDiv.querySelector('.save-btn').addEventListener('click', function() {{
                            const newType = formDiv.querySelector('#new-type-select').value;
                            
                            let newValue;
                            switch (newType) {{
                                case 'string': newValue = ''; break;
                                case 'number': newValue = 0; break;
                                case 'boolean': newValue = false; break;
                                case 'object': newValue = {{}}; break;
                                case 'array': newValue = []; break;
                            }}
                            
                            const pathParts = currentPath.split('.');
                            let obj = currentData;
                            for (let i = 0; i < pathParts.length - 1; i++) {{
                                obj = obj[pathParts[i]];
                            }}
                            obj[pathParts[pathParts.length - 1]] = newValue;
                            
                            renderTree(currentData, treeContent);
                            updateHiddenInput();
                            formDiv.remove();
                        }});
                        
                        // Handle cancel
                        formDiv.querySelector('.cancel-btn').addEventListener('click', function() {{
                            formDiv.remove();
                        }});
                        
                        // Handle Enter key
                        formDiv.querySelector('#new-type-select').addEventListener('keydown', function(e) {{
                            if (e.key === 'Enter') {{
                                formDiv.querySelector('.save-btn').click();
                            }} else if (e.key === 'Escape') {{
                                formDiv.querySelector('.cancel-btn').click();
                            }}
                        }});
                    }});
                    
                    // Add edit key functionality
                    itemDiv.querySelector('.edit-key-btn').addEventListener('click', function() {{
                        const oldKey = key;
                        
                        // Create inline form for editing key
                        const formDiv = document.createElement('div');
                        formDiv.className = 'inline-form edit-key-form';
                        formDiv.innerHTML = 
                            '<div class="form-row">' +
                                '<label>Rename to:</label>' +
                                '<input type="text" class="form-input" value="' + oldKey + '" id="new-key-input">' +
                                '<button type="button" class="btn btn-success save-btn">Rename</button>' +
                                '<button type="button" class="btn btn-secondary cancel-btn">Cancel</button>' +
                            '</div>';
                        
                        // Insert form after the header
                        const header = itemDiv.querySelector('.json-item-header');
                        header.parentNode.insertBefore(formDiv, header.nextSibling);
                        
                        // Focus and select the input
                        const input = formDiv.querySelector('#new-key-input');
                        input.focus();
                        input.select();
                        
                        // Handle save
                        formDiv.querySelector('.save-btn').addEventListener('click', function() {{
                            const newKey = formDiv.querySelector('#new-key-input').value.trim();
                            
                            if (newKey && newKey !== oldKey) {{
                                const pathParts = currentPath.split('.');
                                let obj = currentData;
                                for (let i = 0; i < pathParts.length - 1; i++) {{
                                    obj = obj[pathParts[i]];
                                }}
                                
                                // Rename the key
                                obj[newKey] = obj[oldKey];
                                delete obj[oldKey];
                                
                                renderTree(currentData, treeContent);
                                updateHiddenInput();
                            }}
                            formDiv.remove();
                        }});
                        
                        // Handle cancel
                        formDiv.querySelector('.cancel-btn').addEventListener('click', function() {{
                            formDiv.remove();
                        }});
                        
                        // Handle Enter key
                        formDiv.querySelector('#new-key-input').addEventListener('keydown', function(e) {{
                            if (e.key === 'Enter') {{
                                formDiv.querySelector('.save-btn').click();
                            }} else if (e.key === 'Escape') {{
                                formDiv.querySelector('.cancel-btn').click();
                            }}
                        }});
                    }});
                    
                    // Add collapse functionality
                    const collapseBtn = itemDiv.querySelector('.collapse-btn');
                    if (collapseBtn) {{
                        collapseBtn.addEventListener('click', function() {{
                            const contentDiv = itemDiv.querySelector('.json-item-content');
                            const isCollapsed = this.dataset.collapsed === 'true';
                            
                            if (isCollapsed) {{
                                // Expand
                                this.dataset.collapsed = 'false';
                                contentDiv.classList.remove('collapsed');
                                this.querySelector('.collapse-icon').textContent = '▼';
                                saveExpandedState(currentPath, true);
                            }} else {{
                                // Collapse
                                this.dataset.collapsed = 'true';
                                contentDiv.classList.add('collapsed');
                                this.querySelector('.collapse-icon').textContent = '▶';
                                saveExpandedState(currentPath, false);
                            }}
                        }});
                    }}
                }});
            }}
            
            // Render value based on type
            function renderValue(value, container, path) {{
                container.innerHTML = '';
                
                if (typeof value === 'string') {{
                    const input = document.createElement('input');
                    input.type = 'text';
                    input.className = 'json-input';
                    input.value = value;
                    input.placeholder = 'Enter string value';
                    input.addEventListener('input', function() {{
                        setValueAtPath(path, this.value);
                    }});
                    container.appendChild(input);
                }} else if (typeof value === 'number') {{
                    const input = document.createElement('input');
                    input.type = 'number';
                    input.className = 'json-input';
                    input.value = value;
                    input.placeholder = 'Enter number value';
                    input.addEventListener('input', function() {{
                        setValueAtPath(path, parseFloat(this.value) || 0);
                    }});
                    container.appendChild(input);
                }} else if (typeof value === 'boolean') {{
                    const select = document.createElement('select');
                    select.className = 'json-input';
                    select.innerHTML = 
                        '<option value="true"' + (value ? ' selected' : '') + '>True</option>' +
                        '<option value="false"' + (!value ? ' selected' : '') + '>False</option>';
                    select.addEventListener('change', function() {{
                        setValueAtPath(path, this.value === 'true');
                    }});
                    container.appendChild(select);
                }} else if (Array.isArray(value)) {{
                    const addBtn = document.createElement('button');
                    addBtn.type = 'button';
                    addBtn.className = 'add-item-btn';
                    addBtn.textContent = '+ Add Array Item';
                    addBtn.addEventListener('click', function() {{
                        // Create inline form for adding array item
                        const formDiv = document.createElement('div');
                        formDiv.className = 'inline-form add-array-item-form';
                        formDiv.innerHTML = 
                            '<div class="form-row">' +
                                '<label>Add item type:</label>' +
                                '<select class="form-select" id="array-item-type">' +
                                    '<option value="string">String</option>' +
                                    '<option value="number">Number</option>' +
                                    '<option value="boolean">Boolean</option>' +
                                    '<option value="object">Object</option>' +
                                '</select>' +
                                '<button type="button" class="btn btn-success save-btn">Add</button>' +
                                '<button type="button" class="btn btn-secondary cancel-btn">Cancel</button>' +
                            '</div>';
                        
                        // Insert form before the add button
                        addBtn.parentNode.insertBefore(formDiv, addBtn);
                        
                        // Focus on the select
                        formDiv.querySelector('#array-item-type').focus();
                        
                        // Handle save
                        formDiv.querySelector('.save-btn').addEventListener('click', function() {{
                            const itemType = formDiv.querySelector('#array-item-type').value;
                            
                            let newItem;
                            switch (itemType) {{
                                case 'string': newItem = ''; break;
                                case 'number': newItem = 0; break;
                                case 'boolean': newItem = false; break;
                                case 'object': newItem = {{}}; break;
                            }}
                            value.push(newItem);
                            renderTree(currentData, treeContent);
                            updateHiddenInput();
                            formDiv.remove();
                        }});
                        
                        // Handle cancel
                        formDiv.querySelector('.cancel-btn').addEventListener('click', function() {{
                            formDiv.remove();
                        }});
                        
                        // Handle Enter key
                        formDiv.querySelector('#array-item-type').addEventListener('keydown', function(e) {{
                            if (e.key === 'Enter') {{
                                formDiv.querySelector('.save-btn').click();
                            }} else if (e.key === 'Escape') {{
                                formDiv.querySelector('.cancel-btn').click();
                            }}
                        }});
                    }});
                    container.appendChild(addBtn);
                    
                    value.forEach((item, index) => {{
                        const itemDiv = document.createElement('div');
                        itemDiv.className = 'json-array-item';
                        
                        const itemType = typeof item;
                        const isComplex = itemType === 'object' || Array.isArray(item);
                        
                        itemDiv.innerHTML = 
                            '<div class="json-item-header">' +
                                '<button type="button" class="collapse-btn ' + (isComplex ? '' : 'hidden') + '" data-collapsed="true">' +
                                    '<span class="collapse-icon">▶</span>' +
                                '</button>' +
                                '<span class="json-item-key">[' + index + ']</span>' +
                                '<span class="json-item-type">' + itemType + '</span>' +
                                '<div class="json-item-controls">' +
                                    '<button type="button" class="remove-btn" data-index="' + index + '" data-path="' + path + '">Remove</button>' +
                                '</div>' +
                            '</div>';
                        container.appendChild(itemDiv);
                        
                        const contentDiv = document.createElement('div');
                        contentDiv.className = 'json-item-content ' + (isComplex ? 'collapsible collapsed' : '');
                        itemDiv.appendChild(contentDiv);
                        
                        const itemPath = path + '[' + index + ']';
                        renderValue(item, contentDiv, itemPath);
                        
                        itemDiv.querySelector('.remove-btn').addEventListener('click', function() {{
                            value.splice(index, 1);
                            renderTree(currentData, treeContent);
                            updateHiddenInput();
                        }});
                        
                        // Add collapse functionality for array items
                        const collapseBtn = itemDiv.querySelector('.collapse-btn');
                        if (collapseBtn) {{
                            collapseBtn.addEventListener('click', function() {{
                                const contentDiv = itemDiv.querySelector('.json-item-content');
                                const isCollapsed = this.dataset.collapsed === 'true';
                                
                                if (isCollapsed) {{
                                    // Expand
                                    this.dataset.collapsed = 'false';
                                    contentDiv.classList.remove('collapsed');
                                    this.querySelector('.collapse-icon').textContent = '▼';
                                    saveExpandedState(itemPath, true);
                                }} else {{
                                    // Collapse
                                    this.dataset.collapsed = 'true';
                                    contentDiv.classList.add('collapsed');
                                    this.querySelector('.collapse-icon').textContent = '▶';
                                    saveExpandedState(itemPath, false);
                                }}
                            }});
                        }}
                    }});
                }} else if (typeof value === 'object' && value !== null) {{
                    const addBtn = document.createElement('button');
                    addBtn.type = 'button';
                    addBtn.className = 'add-item-btn';
                    addBtn.textContent = '+ Add Object Property';
                    addBtn.addEventListener('click', function() {{
                        // Create inline form for adding object property
                        const formDiv = document.createElement('div');
                        formDiv.className = 'inline-form add-object-property-form';
                        formDiv.innerHTML = 
                            '<div class="form-row">' +
                                '<input type="text" class="form-input" placeholder="Property name" id="new-property-name">' +
                                '<select class="form-select" id="new-property-type">' +
                                    '<option value="string">String</option>' +
                                    '<option value="number">Number</option>' +
                                    '<option value="boolean">Boolean</option>' +
                                    '<option value="object">Object</option>' +
                                    '<option value="array">Array</option>' +
                                '</select>' +
                                '<button type="button" class="btn btn-success save-btn">Add</button>' +
                                '<button type="button" class="btn btn-secondary cancel-btn">Cancel</button>' +
                            '</div>';
                        
                        // Insert form before the add button
                        addBtn.parentNode.insertBefore(formDiv, addBtn);
                        
                        // Focus on the name input
                        formDiv.querySelector('#new-property-name').focus();
                        
                        // Handle save
                        formDiv.querySelector('.save-btn').addEventListener('click', function() {{
                            const key = formDiv.querySelector('#new-property-name').value.trim();
                            const itemType = formDiv.querySelector('#new-property-type').value;
                            
                            if (key) {{
                                let newValue;
                                switch (itemType) {{
                                    case 'string': newValue = ''; break;
                                    case 'number': newValue = 0; break;
                                    case 'boolean': newValue = false; break;
                                    case 'object': newValue = {{}}; break;
                                    case 'array': newValue = []; break;
                                }}
                                value[key] = newValue;
                                renderTree(currentData, treeContent);
                                updateHiddenInput();
                            }}
                            formDiv.remove();
                        }});
                        
                        // Handle cancel
                        formDiv.querySelector('.cancel-btn').addEventListener('click', function() {{
                            formDiv.remove();
                        }});
                        
                        // Handle Enter key
                        formDiv.querySelector('#new-property-name').addEventListener('keydown', function(e) {{
                            if (e.key === 'Enter') {{
                                formDiv.querySelector('.save-btn').click();
                            }} else if (e.key === 'Escape') {{
                                formDiv.querySelector('.cancel-btn').click();
                            }}
                        }});
                    }});
                    container.appendChild(addBtn);
                    
                    Object.entries(value).forEach(([key, val]) => {{
                        const itemDiv = document.createElement('div');
                        itemDiv.className = 'json-object-item';
                        
                        const valType = Array.isArray(val) ? 'array' : typeof val;
                        const isComplex = valType === 'object' || valType === 'array';
                        
                        itemDiv.innerHTML = 
                            '<div class="json-item-header">' +
                                '<button type="button" class="collapse-btn ' + (isComplex ? '' : 'hidden') + '" data-collapsed="true">' +
                                    '<span class="collapse-icon">▶</span>' +
                                '</button>' +
                                '<span class="json-item-key">' + key + '</span>' +
                                '<span class="json-item-type">' + valType + '</span>' +
                                '<div class="json-item-controls">' +
                                    '<button type="button" class="remove-btn" data-key="' + key + '" data-path="' + path + '">Remove</button>' +
                                '</div>' +
                            '</div>';
                        container.appendChild(itemDiv);
                        
                        const contentDiv = document.createElement('div');
                        contentDiv.className = 'json-item-content ' + (isComplex ? 'collapsible collapsed' : '');
                        itemDiv.appendChild(contentDiv);
                        renderValue(val, contentDiv, path + '.' + key);
                        
                        itemDiv.querySelector('.remove-btn').addEventListener('click', function() {{
                            delete value[key];
                            renderTree(currentData, treeContent);
                            updateHiddenInput();
                        }});
                        
                        // Add collapse functionality for object items
                        const collapseBtn = itemDiv.querySelector('.collapse-btn');
                        if (collapseBtn) {{
                            collapseBtn.addEventListener('click', function() {{
                                const contentDiv = itemDiv.querySelector('.json-item-content');
                                const isCollapsed = this.dataset.collapsed === 'true';
                                const itemPath = path + '.' + key;
                                
                                if (isCollapsed) {{
                                    // Expand
                                    this.dataset.collapsed = 'false';
                                    contentDiv.classList.remove('collapsed');
                                    this.querySelector('.collapse-icon').textContent = '▼';
                                    saveExpandedState(itemPath, true);
                                }} else {{
                                    // Collapse
                                    this.dataset.collapsed = 'true';
                                    contentDiv.classList.add('collapsed');
                                    this.querySelector('.collapse-icon').textContent = '▶';
                                    saveExpandedState(itemPath, false);
                                }}
                            }});
                        }}
                    }});
                }}
            }}
            
            // Set value at path
            function setValueAtPath(path, value) {{
                const pathParts = path.split('.');
                let obj = currentData;
                
                for (let i = 0; i < pathParts.length - 1; i++) {{
                    const part = pathParts[i];
                    if (part.includes('[')) {{
                        const arrayMatch = part.match(/(.+)\\\[(\d+)\\\]/);
                        if (arrayMatch) {{
                            const arrayPath = arrayMatch[1];
                            const index = parseInt(arrayMatch[2]);
                            if (!obj[arrayPath]) obj[arrayPath] = [];
                            obj = obj[arrayPath];
                            obj[index] = value;
                            updateHiddenInput();
                            return;
                        }}
                    }}
                    if (!obj[part]) obj[part] = {{}};
                    obj = obj[part];
                }}
                
                const lastPart = pathParts[pathParts.length - 1];
                if (lastPart.includes('[')) {{
                    const arrayMatch = lastPart.match(/(.+)\\\[(\d+)\\\]/);
                    if (arrayMatch) {{
                        const arrayPath = arrayMatch[1];
                        const index = parseInt(arrayMatch[2]);
                        if (!obj[arrayPath]) obj[arrayPath] = [];
                        obj[arrayPath][index] = value;
                        updateHiddenInput();
                        return;
                    }}
                }}
                
                obj[lastPart] = value;
                updateHiddenInput();
            }}
            
            // Add field button
            container.querySelector('.add-field-btn').addEventListener('click', function() {{
                // Create inline form for adding new field
                const formDiv = document.createElement('div');
                formDiv.className = 'inline-form add-field-form';
                formDiv.innerHTML = 
                    '<div class="form-row">' +
                        '<input type="text" class="form-input" placeholder="Field name" id="new-field-name">' +
                        '<select class="form-select" id="new-field-type">' +
                            '<option value="string">String</option>' +
                            '<option value="number">Number</option>' +
                            '<option value="boolean">Boolean</option>' +
                            '<option value="object">Object</option>' +
                            '<option value="array">Array</option>' +
                        '</select>' +
                        '<button type="button" class="btn btn-success save-btn">Add</button>' +
                        '<button type="button" class="btn btn-secondary cancel-btn">Cancel</button>' +
                    '</div>';
                
                // Insert form at the top of tree content
                treeContent.insertBefore(formDiv, treeContent.firstChild);
                
                // Focus on the name input
                formDiv.querySelector('#new-field-name').focus();
                
                // Handle save
                formDiv.querySelector('.save-btn').addEventListener('click', function() {{
                    const key = formDiv.querySelector('#new-field-name').value.trim();
                    const type = formDiv.querySelector('#new-field-type').value;
                    
                    if (key) {{
                        let value;
                        switch (type) {{
                            case 'string': value = ''; break;
                            case 'number': value = 0; break;
                            case 'boolean': value = false; break;
                            case 'object': value = {{}}; break;
                            case 'array': value = []; break;
                        }}
                        currentData[key] = value;
                        renderTree(currentData, treeContent);
                        updateHiddenInput();
                    }}
                    formDiv.remove();
                }});
                
                // Handle cancel
                formDiv.querySelector('.cancel-btn').addEventListener('click', function() {{
                    formDiv.remove();
                }});
                
                // Handle Enter key
                formDiv.querySelector('#new-field-name').addEventListener('keydown', function(e) {{
                    if (e.key === 'Enter') {{
                        formDiv.querySelector('.save-btn').click();
                    }} else if (e.key === 'Escape') {{
                        formDiv.querySelector('.cancel-btn').click();
                    }}
                }});
            }});
            
            // Expand all button
            container.querySelector('.expand-all-btn').addEventListener('click', function() {{
                const collapseBtns = container.querySelectorAll('.collapse-btn');
                collapseBtns.forEach(btn => {{
                    const contentDiv = btn.closest('.json-item, .json-array-item, .json-object-item').querySelector('.json-item-content');
                    if (contentDiv && contentDiv.classList.contains('collapsible')) {{
                        btn.dataset.collapsed = 'false';
                        contentDiv.classList.remove('collapsed');
                        btn.querySelector('.collapse-icon').textContent = '▼';
                    }}
                }});
            }});
            
            // Collapse all button
            container.querySelector('.collapse-all-btn').addEventListener('click', function() {{
                const collapseBtns = container.querySelectorAll('.collapse-btn');
                collapseBtns.forEach(btn => {{
                    const contentDiv = btn.closest('.json-item, .json-array-item, .json-object-item').querySelector('.json-item-content');
                    if (contentDiv && contentDiv.classList.contains('collapsible')) {{
                        btn.dataset.collapsed = 'true';
                        contentDiv.classList.add('collapsed');
                        btn.querySelector('.collapse-icon').textContent = '▶';
                    }}
                }});
            }});
            
            // Paste JSON button
            container.querySelector('.paste-json-btn').addEventListener('click', function() {{
                // Use modern Clipboard API
                if (navigator.clipboard && navigator.clipboard.readText) {{
                    navigator.clipboard.readText()
                        .then(pastedContent => {{
                            if (pastedContent.trim()) {{
                                try {{
                                    const pastedData = JSON.parse(pastedContent);
                                    currentData = pastedData;
                                    updateHiddenInput();
                                    
                                    // Re-render the tree view with new data
                                    renderTree(currentData, treeContent);
                                    
                                    // Switch to tree view to show the updated structure
                                    const treeTab = container.querySelector('.json-tab[data-tab="tree"]');
                                    if (treeTab) {{
                                        treeTab.click();
                                    }}
                                    
                                    // Update textarea content
                                    textarea.value = JSON.stringify(currentData, null, 2);
                                    
                                    showFeedback('JSON pasted successfully! Tree view updated.', 'success');
                                }} catch (e) {{
                                    showFeedback('Invalid JSON format. Please check your clipboard data.', 'error');
                                    console.log('Paste error:', e.message);
                                }}
                            }} else {{
                                showFeedback('No content found in clipboard.', 'error');
                            }}
                        }})
                        .catch(err => {{
                            console.log('Clipboard API error:', err);
                            showFeedback('Clipboard access denied. Please paste manually into the JSON tab.', 'error');
                        }});
                }} else {{
                    // Fallback for older browsers
                    showFeedback('Clipboard API not supported. Please paste manually into the JSON tab.', 'error');
                }}
            }});
            
            // Clear All button
            container.querySelector('.clear-all-btn').addEventListener('click', function() {{
                if (confirm('Are you sure you want to clear all data? This action cannot be undone.')) {{
                    currentData = {{}};
                    updateHiddenInput();
                    renderTree(currentData, treeContent);
                    textarea.value = '{{}}';
                    showFeedback('All data cleared successfully.', 'success');
                }}
            }});
            
            // Tab switching
            const tabs = container.querySelectorAll('.json-tab');
            tabs.forEach(tab => {{
                tab.addEventListener('click', function(e) {{
                    e.preventDefault();
                    e.stopPropagation();
                    const tabName = this.dataset.tab;
                    
                    // Remove active class from all tabs and content
                    container.querySelectorAll('.json-tab').forEach(t => t.classList.remove('active'));
                    container.querySelectorAll('.json-tab-content').forEach(c => c.classList.remove('active'));
                    
                    // Add active class to clicked tab
                    this.classList.add('active');
                    
                    // Find and activate corresponding content
                    const contentElement = container.querySelector('.json-tab-content[data-tab="' + tabName + '"]');
                    if (contentElement) {{
                        contentElement.classList.add('active');
                    }}
                    
                    // Update textarea if switching to JSON tab
                    if (tabName === 'json') {{
                        textarea.value = JSON.stringify(currentData, null, 2);
                    }}
                }});
            }});
            
            // Textarea changes with enhanced paste support
            let inputTimeout;
            textarea.addEventListener('input', function() {{
                // Clear previous timeout
                clearTimeout(inputTimeout);
                
                // Set a new timeout to process the input
                inputTimeout = setTimeout(() => {{
                    try {{
                        const newData = JSON.parse(this.value);
                        currentData = newData;
                        updateHiddenInput();
                        
                        // Re-render the tree view with new data
                        renderTree(currentData, treeContent);
                        
                        // Update tree view if we're on the JSON tab
                        const activeTab = container.querySelector('.json-tab.active');
                        if (activeTab && activeTab.dataset.tab === 'json') {{
                            // Switch to tree view to show the updated structure
                            const treeTab = container.querySelector('.json-tab[data-tab="tree"]');
                            if (treeTab) {{
                                treeTab.click();
                            }}
                        }}
                    }} catch (e) {{
                        // Invalid JSON, don't update
                        console.log('Invalid JSON:', e.message);
                    }}
                }}, 300); // Wait 300ms after user stops typing
            }});
            
            // Enhanced paste handling for better UX
            textarea.addEventListener('paste', function(e) {{
                // Let the paste happen first, then process
                setTimeout(() => {{
                    try {{
                        const pastedData = JSON.parse(this.value);
                        currentData = pastedData;
                        updateHiddenInput();
                        
                        // Re-render the tree view with new data
                        renderTree(currentData, treeContent);
                        
                        // Always switch to tree view after successful paste
                        const treeTab = container.querySelector('.json-tab[data-tab="tree"]');
                        if (treeTab) {{
                            treeTab.click();
                        }}
                        
                        // Show success feedback
                        showFeedback('JSON pasted successfully! Tree view updated.', 'success');
                    }} catch (e) {{
                        // Don't show error on every keystroke, only on paste
                        console.log('Paste validation error:', e.message);
                    }}
                }}, 50);
            }});
            
            // Add feedback system
            function showFeedback(message, type) {{
                // Remove existing feedback
                const existingFeedback = container.querySelector('.json-feedback');
                if (existingFeedback) {{
                    existingFeedback.remove();
                }}
                
                const feedback = document.createElement('div');
                feedback.className = 'json-feedback json-feedback-' + type;
                feedback.textContent = message;
                
                // Insert after the header
                const header = container.querySelector('.json-editor-header');
                header.parentNode.insertBefore(feedback, header.nextSibling);
                
                // Auto-remove after 3 seconds
                setTimeout(() => {{
                    if (feedback.parentNode) {{
                        feedback.remove();
                    }}
                }}, 3000);
            }}
            
            // Keyboard shortcuts
            document.addEventListener('keydown', function(e) {{
                // Ctrl+V to paste JSON (when not in a form input)
                if (e.ctrlKey && e.key === 'v' && !e.target.matches('input, textarea, select')) {{
                    e.preventDefault();
                    container.querySelector('.paste-json-btn').click();
                }}
            }});
            
            // Initial render
            renderTree(currentData, treeContent);
        }});
        </script>
        """
        
        return mark_safe(html)


class JSONField(forms.JSONField):
    """Custom JSON field with dynamic editor"""
    
    def __init__(self, *args, **kwargs):
        kwargs.setdefault('widget', DynamicJSONEditorWidget())
        super().__init__(*args, **kwargs)
    
    def clean(self, value):
        """Clean and validate JSON data"""
        if not value:
            return {}
        
        try:
            if isinstance(value, str):
                return json.loads(value)
            return value
        except json.JSONDecodeError as e:
            raise ValidationError(f'Invalid JSON format: {e.msg} at line {e.lineno}, column {e.colno}') 