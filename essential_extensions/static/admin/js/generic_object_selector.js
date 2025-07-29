/**
 * Generic Object Selector JavaScript
 * 
 * This script provides dynamic object selection for generic foreign keys
 * in the Django admin interface. It populates the object selector dropdown
 * based on the selected content type.
 */

(function($) {
    'use strict';

    // Initialize when document is ready
    $(document).ready(function() {
        initializeGenericObjectSelector();
    });

    function initializeGenericObjectSelector() {
        // Find all content type selectors
        $('select[name="content_type"]').each(function() {
            var $contentTypeSelect = $(this);
            var $objectSelector = $contentTypeSelect.closest('form').find('select[name="object_selector"]');
            var $objectIdField = $contentTypeSelect.closest('form').find('input[name="object_id"]');
            
            if ($objectSelector.length && $objectIdField.length) {
                // Bind change event to content type selector
                $contentTypeSelect.on('change', function() {
                    var contentTypeId = $(this).val();
                    updateObjectSelector($objectSelector, $objectIdField, contentTypeId);
                });
                
                // Initialize on page load if content type is already selected
                if ($contentTypeSelect.val()) {
                    updateObjectSelector($objectSelector, $objectIdField, $contentTypeSelect.val());
                }
            }
        });

        // Handle object selector changes
        $('select[name="object_selector"]').on('change', function() {
            var $objectIdField = $(this).closest('form').find('input[name="object_id"]');
            var selectedObjectId = $(this).val();
            
            if (selectedObjectId) {
                $objectIdField.val(selectedObjectId);
            } else {
                $objectIdField.val('');
            }
        });
    }

    function updateObjectSelector($objectSelector, $objectIdField, contentTypeId) {
        if (!contentTypeId) {
            // No content type selected, clear object selector
            $objectSelector.html('<option value="">First select a content type above</option>');
            $objectIdField.val('');
            return;
        }

        // Show loading state
        $objectSelector.html('<option value="">Loading objects...</option>');
        $objectIdField.val('');

        // Get the URL for the AJAX endpoint
        var url = getObjectsUrl($objectSelector);
        
        // Make AJAX request to get objects for this content type
        $.ajax({
            url: url,
            data: {
                'content_type': contentTypeId
            },
            dataType: 'json',
            success: function(data) {
                var options = '<option value="">Select an object...</option>';
                
                if (data.objects && data.objects.length > 0) {
                    $.each(data.objects, function(index, obj) {
                        options += '<option value="' + obj.id + '">' + obj.name + '</option>';
                    });
                } else {
                    options = '<option value="">No objects found for this content type</option>';
                }
                
                $objectSelector.html(options);
            },
            error: function(xhr, status, error) {
                console.error('Error loading objects:', error);
                $objectSelector.html('<option value="">Error loading objects</option>');
            }
        });
    }

    function getObjectsUrl($objectSelector) {
        // Try to get the URL from the form action or construct it
        var form = $objectSelector.closest('form');
        var formAction = form.attr('action') || window.location.pathname;
        
        // Remove any existing query parameters
        var baseUrl = formAction.split('?')[0];
        
        // Construct the objects URL
        // This assumes the URL pattern follows Django's admin URL structure
        var urlParts = baseUrl.split('/');
        var appLabel = '';
        var modelName = '';
        
        // Try to extract app_label and model_name from the URL
        for (var i = 0; i < urlParts.length; i++) {
            if (urlParts[i] === 'admin') {
                if (i + 2 < urlParts.length) {
                    appLabel = urlParts[i + 1];
                    modelName = urlParts[i + 2];
                    break;
                }
            }
        }
        
        if (appLabel && modelName) {
            return baseUrl + 'get-objects/';
        } else {
            // Fallback: try to construct from current page
            return window.location.pathname.replace(/\/change\/.*$/, '/get-objects/');
        }
    }

    // Expose functions for potential external use
    window.GenericObjectSelector = {
        initialize: initializeGenericObjectSelector,
        updateObjectSelector: updateObjectSelector
    };

})(django.jQuery); 