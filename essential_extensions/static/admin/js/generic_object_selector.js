/**
 * Generic Object Selector for Django Admin
 * 
 * This script handles the dynamic object selection dropdown for any admin
 * interface that uses generic foreign keys with ContentTypes.
 * 
 * Requirements:
 * - Content type field: id_content_type
 * - Object selector field: id_object_selector  
 * - Hidden object ID field: id_object_id
 * - AJAX endpoint: {model-admin-url}/get-objects/
 */

(function() {
    'use strict';

    // Wait for DOM to be ready
    document.addEventListener('DOMContentLoaded', function() {
        initializeObjectSelector();
    });

    function initializeObjectSelector() {
        const contentTypeField = document.getElementById('id_content_type');
        const objectSelectorField = document.getElementById('id_object_selector');
        const objectIdField = document.getElementById('id_object_id');

        if (!contentTypeField || !objectSelectorField || !objectIdField) {
            console.log('Generic object selector: Required fields not found, skipping initialization');
            return;
        }

        console.log('Generic object selector: Initializing...');

        // Add change listener to content type field
        contentTypeField.addEventListener('change', function() {
            const contentTypeId = this.value;
            console.log('Content type changed to:', contentTypeId);
            
            if (contentTypeId) {
                loadObjectsForContentType(contentTypeId, objectSelectorField);
            } else {
                resetObjectSelector(objectSelectorField);
            }
        });

        // Add change listener to object selector field
        objectSelectorField.addEventListener('change', function() {
            const selectedObjectId = this.value;
            console.log('Object selector changed to:', selectedObjectId);
            
            // Update the hidden object_id field
            objectIdField.value = selectedObjectId;
            console.log('Set object_id field to:', selectedObjectId);
        });

        // If content type is already selected (editing existing), load objects
        if (contentTypeField.value) {
            console.log('Content type pre-selected, loading objects...');
            loadObjectsForContentType(contentTypeField.value, objectSelectorField);
        }
    }

    function loadObjectsForContentType(contentTypeId, objectSelectorField) {
        console.log('Loading objects for content type:', contentTypeId);
        
        // Show loading state
        objectSelectorField.innerHTML = '<option value="">Loading...</option>';
        objectSelectorField.disabled = true;

        // Get the current admin URL to build the AJAX endpoint
        const currentPath = window.location.pathname;
        const basePath = currentPath.replace(/\/add\/$|\/\d+\/change\/$/, '');
        const ajaxUrl = basePath + '/get-objects/';
        
        console.log('AJAX URL:', ajaxUrl);

        // Make AJAX request
        fetch(ajaxUrl + '?content_type=' + encodeURIComponent(contentTypeId), {
            method: 'GET',
            headers: {
                'X-Requested-With': 'XMLHttpRequest',
                'X-CSRFToken': getCSRFToken()
            }
        })
        .then(response => {
            if (!response.ok) {
                throw new Error('Network response was not ok: ' + response.statusText);
            }
            return response.json();
        })
        .then(data => {
            console.log('Received objects:', data);
            populateObjectSelector(objectSelectorField, data.objects || []);
        })
        .catch(error => {
            console.error('Error loading objects:', error);
            objectSelectorField.innerHTML = '<option value="">Error loading objects</option>';
        })
        .finally(() => {
            objectSelectorField.disabled = false;
        });
    }

    function populateObjectSelector(objectSelectorField, objects) {
        // Clear existing options
        objectSelectorField.innerHTML = '';

        // Add default option
        const defaultOption = document.createElement('option');
        defaultOption.value = '';
        defaultOption.textContent = objects.length > 0 ? 'Select an object...' : 'No objects available';
        objectSelectorField.appendChild(defaultOption);

        // Add objects as options
        objects.forEach(function(obj) {
            const option = document.createElement('option');
            option.value = obj.id;
            option.textContent = obj.name;
            objectSelectorField.appendChild(option);
        });

        // If this is an edit form and we have a pre-selected value, select it
        const currentValue = objectSelectorField.getAttribute('data-current-value');
        if (currentValue) {
            objectSelectorField.value = currentValue;
            console.log('Pre-selected object:', currentValue);
        }

        console.log('Populated selector with', objects.length, 'objects');
    }

    function resetObjectSelector(objectSelectorField) {
        objectSelectorField.innerHTML = '<option value="">First select a content type above</option>';
        objectSelectorField.disabled = false;
    }

    function getCSRFToken() {
        // Try to get CSRF token from various sources
        const csrfInput = document.querySelector('[name=csrfmiddlewaretoken]');
        if (csrfInput) {
            return csrfInput.value;
        }

        const csrfCookie = document.cookie
            .split('; ')
            .find(row => row.startsWith('csrftoken='));
        if (csrfCookie) {
            return csrfCookie.split('=')[1];
        }

        console.warn('CSRF token not found');
        return '';
    }
})(); 