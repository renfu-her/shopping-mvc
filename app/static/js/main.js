// Main JavaScript file for Shopping Cart Application

$(document).ready(function() {
    // Initialize cart summary
    loadCartSummary();
    
    // Initialize tooltips
    $('[data-bs-toggle="tooltip"]').tooltip();
    
    // Initialize popovers
    $('[data-bs-toggle="popover"]').popover();
});

// Load cart summary and update badge
function loadCartSummary() {
    $.ajax({
        url: '/api/cart-summary',
        method: 'GET',
        success: function(response) {
            if (response && response.total_items !== undefined) {
                $('#cart-badge').text(response.total_items);
            }
        },
        error: function(xhr) {
            console.log('Error loading cart summary:', xhr.responseText);
        }
    });
}

// Show alert message
function showAlert(message, type = 'info', duration = 3000) {
    const alertHtml = `
        <div class="alert alert-${type} alert-dismissible fade show" role="alert">
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        </div>
    `;
    
    // Insert alert at the top of the main content
    $('.container').first().prepend(alertHtml);
    
    // Auto-dismiss after specified duration
    if (duration > 0) {
        setTimeout(function() {
            $('.alert').first().alert('close');
        }, duration);
    }
}

// Format currency
function formatCurrency(amount) {
    return new Intl.NumberFormat('en-US', {
        style: 'currency',
        currency: 'USD'
    }).format(amount);
}

// Validate email
function validateEmail(email) {
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return emailRegex.test(email);
}

// Validate phone number
function validatePhone(phone) {
    const phoneRegex = /^[\+]?[1-9][\d]{0,15}$/;
    return phoneRegex.test(phone.replace(/[\s\-\(\)]/g, ''));
}

// Debounce function for search
function debounce(func, wait, immediate) {
    let timeout;
    return function executedFunction() {
        const context = this;
        const args = arguments;
        const later = function() {
            timeout = null;
            if (!immediate) func.apply(context, args);
        };
        const callNow = immediate && !timeout;
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
        if (callNow) func.apply(context, args);
    };
}

// Add to cart with loading state
function addToCart(productId, quantity = 1, buttonElement = null) {
    if (buttonElement) {
        const originalText = buttonElement.html();
        buttonElement.prop('disabled', true);
        buttonElement.html('<i class="fas fa-spinner fa-spin me-1"></i>Adding...');
        
        $.ajax({
            url: '/api/add-to-cart',
            method: 'POST',
            contentType: 'application/json',
            data: JSON.stringify({
                product_id: productId,
                quantity: quantity
            }),
            success: function(response) {
                if (response.success) {
                    // Update cart badge
                    $('#cart-badge').text(response.cart_summary.total_items);
                    
                    // Show success message
                    showAlert('Product added to cart!', 'success');
                    
                    // Update button state
                    buttonElement.html('<i class="fas fa-check me-1"></i>Added!');
                    setTimeout(function() {
                        buttonElement.html(originalText);
                        buttonElement.prop('disabled', false);
                    }, 2000);
                }
            },
            error: function(xhr) {
                const response = xhr.responseJSON;
                showAlert(response.error || 'Error adding product to cart', 'danger');
                
                // Reset button
                buttonElement.html(originalText);
                buttonElement.prop('disabled', false);
            }
        });
    }
}

// Update cart item quantity
function updateCartItem(cartItemId, quantity) {
    return $.ajax({
        url: '/cart/update',
        method: 'POST',
        contentType: 'application/json',
        data: JSON.stringify({
            cart_item_id: cartItemId,
            quantity: quantity
        })
    });
}

// Remove cart item
function removeCartItem(cartItemId) {
    return $.ajax({
        url: '/cart/remove',
        method: 'POST',
        contentType: 'application/json',
        data: JSON.stringify({
            cart_item_id: cartItemId
        })
    });
}

// Clear cart
function clearCart() {
    return $.ajax({
        url: '/cart/clear',
        method: 'POST'
    });
}

// Smooth scroll to element
function smoothScrollTo(element, offset = 0) {
    $('html, body').animate({
        scrollTop: $(element).offset().top - offset
    }, 500);
}

// Format date
function formatDate(dateString) {
    const date = new Date(dateString);
    return date.toLocaleDateString('en-US', {
        year: 'numeric',
        month: 'long',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
    });
}

// Copy to clipboard
function copyToClipboard(text) {
    if (navigator.clipboard) {
        navigator.clipboard.writeText(text).then(function() {
            showAlert('Copied to clipboard!', 'success', 2000);
        });
    } else {
        // Fallback for older browsers
        const textArea = document.createElement('textarea');
        textArea.value = text;
        document.body.appendChild(textArea);
        textArea.select();
        document.execCommand('copy');
        document.body.removeChild(textArea);
        showAlert('Copied to clipboard!', 'success', 2000);
    }
}

// Confirm dialog
function confirmAction(message, callback) {
    if (confirm(message)) {
        callback();
    }
}

// Loading overlay
function showLoadingOverlay() {
    if ($('#loading-overlay').length === 0) {
        $('body').append(`
            <div id="loading-overlay" class="position-fixed top-0 start-0 w-100 h-100 d-flex align-items-center justify-content-center" 
                 style="background-color: rgba(0,0,0,0.5); z-index: 9999;">
                <div class="spinner-border text-light" role="status">
                    <span class="visually-hidden">Loading...</span>
                </div>
            </div>
        `);
    }
}

function hideLoadingOverlay() {
    $('#loading-overlay').remove();
}

// Form validation helpers
function validateForm(formSelector) {
    let isValid = true;
    const form = $(formSelector);
    
    // Clear previous validation
    form.find('.is-invalid').removeClass('is-invalid');
    form.find('.invalid-feedback').remove();
    
    // Validate required fields
    form.find('[required]').each(function() {
        const field = $(this);
        const value = field.val().trim();
        
        if (!value) {
            field.addClass('is-invalid');
            field.after('<div class="invalid-feedback">This field is required.</div>');
            isValid = false;
        }
    });
    
    // Validate email fields
    form.find('input[type="email"]').each(function() {
        const field = $(this);
        const value = field.val().trim();
        
        if (value && !validateEmail(value)) {
            field.addClass('is-invalid');
            field.after('<div class="invalid-feedback">Please enter a valid email address.</div>');
            isValid = false;
        }
    });
    
    return isValid;
}

// Auto-save form data to localStorage
function autoSaveForm(formSelector, key) {
    const form = $(formSelector);
    
    // Load saved data
    const savedData = localStorage.getItem(key);
    if (savedData) {
        const data = JSON.parse(savedData);
        Object.keys(data).forEach(function(name) {
            form.find(`[name="${name}"]`).val(data[name]);
        });
    }
    
    // Save data on change
    form.on('change input', 'input, select, textarea', function() {
        const formData = {};
        form.find('input, select, textarea').each(function() {
            const field = $(this);
            if (field.attr('name')) {
                formData[field.attr('name')] = field.val();
            }
        });
        localStorage.setItem(key, JSON.stringify(formData));
    });
}

// Clear saved form data
function clearSavedForm(key) {
    localStorage.removeItem(key);
}

// Initialize common functionality
$(document).ready(function() {
    // Auto-save checkout form
    autoSaveForm('#checkout-form', 'checkout-form-data');
    
    // Clear saved form data on successful order
    if (window.location.pathname.includes('order-confirmation')) {
        clearSavedForm('checkout-form-data');
    }
    
    // Add fade-in animation to cards
    $('.card').addClass('fade-in');
    
    // Initialize quantity controls
    $('.quantity-btn').click(function() {
        const action = $(this).data('action');
        const input = $(this).siblings('.quantity-input');
        const currentValue = parseInt(input.val());
        const minValue = parseInt(input.attr('min')) || 1;
        const maxValue = parseInt(input.attr('max')) || 999;
        
        let newValue = currentValue;
        if (action === 'increase' && currentValue < maxValue) {
            newValue = currentValue + 1;
        } else if (action === 'decrease' && currentValue > minValue) {
            newValue = currentValue - 1;
        }
        
        if (newValue !== currentValue) {
            input.val(newValue).trigger('change');
        }
    });
});
