// Post Accreditation System - Main JavaScript

document.addEventListener('DOMContentLoaded', function() {
    
    // Initialize tooltips
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });

    // Initialize popovers
    var popoverTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="popover"]'));
    var popoverList = popoverTriggerList.map(function (popoverTriggerEl) {
        return new bootstrap.Popover(popoverTriggerEl);
    });

    // Auto-hide alerts after 5 seconds
    setTimeout(function() {
        var alerts = document.querySelectorAll('.alert:not(.alert-important)');
        alerts.forEach(function(alert) {
            var bsAlert = new bootstrap.Alert(alert);
            bsAlert.close();
        });
    }, 5000);

    // Form validation enhancements
    var forms = document.querySelectorAll('.needs-validation');
    Array.prototype.slice.call(forms).forEach(function(form) {
        form.addEventListener('submit', function(event) {
            if (!form.checkValidity()) {
                event.preventDefault();
                event.stopPropagation();
            }
            form.classList.add('was-validated');
        }, false);
    });

    // File upload enhancements
    initializeFileUploads();
    
    // Dynamic form sections
    initializeDynamicForms();
    
    // Initialize data tables
    initializeDataTables();
    
    // AJAX form handlers
    initializeAjaxForms();
    
    // Real-time validation
    initializeRealTimeValidation();
    
    // Initialize auto-save
    initializeAutoSave();
});

// File Upload Functions
function initializeFileUploads() {
    var fileInputs = document.querySelectorAll('input[type="file"]');
    
    fileInputs.forEach(function(input) {
        var dropArea = input.closest('.file-upload-area');
        
        if (dropArea) {
            ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
                dropArea.addEventListener(eventName, preventDefaults, false);
            });
            
            ['dragenter', 'dragover'].forEach(eventName => {
                dropArea.addEventListener(eventName, highlight, false);
            });
            
            ['dragleave', 'drop'].forEach(eventName => {
                dropArea.addEventListener(eventName, unhighlight, false);
            });
            
            dropArea.addEventListener('drop', handleDrop, false);
            dropArea.addEventListener('click', () => input.click());
        }
        
        input.addEventListener('change', function() {
            handleFiles(this.files, input);
        });
    });
}

function preventDefaults(e) {
    e.preventDefault();
    e.stopPropagation();
}

function highlight(e) {
    e.currentTarget.classList.add('dragover');
}

function unhighlight(e) {
    e.currentTarget.classList.remove('dragover');
}

function handleDrop(e) {
    var dt = e.dataTransfer;
    var files = dt.files;
    var input = e.currentTarget.querySelector('input[type="file"]');
    handleFiles(files, input);
}

function handleFiles(files, input) {
    if (files.length > 0) {
        var file = files[0];
        var maxSize = 16 * 1024 * 1024; // 16MB
        
        if (file.size > maxSize) {
            showAlert('File size exceeds 16MB limit', 'danger');
            return;
        }
        
        // Update UI to show selected file
        var fileName = file.name;
        var fileInfo = input.closest('.file-upload-area')?.querySelector('.file-info');
        if (fileInfo) {
            fileInfo.innerHTML = `<i class="bi bi-file-check me-2"></i>${fileName}`;
            fileInfo.classList.remove('d-none');
        }
        
        // If it's an image, show preview
        if (file.type.startsWith('image/')) {
            showImagePreview(file, input);
        }
    }
}

function showImagePreview(file, input) {
    var reader = new FileReader();
    reader.onload = function(e) {
        var preview = input.closest('.file-upload-area')?.querySelector('.image-preview');
        if (preview) {
            preview.innerHTML = `<img src="${e.target.result}" class="img-thumbnail mt-2" style="max-width: 200px;">`;
            preview.classList.remove('d-none');
        }
    };
    reader.readAsDataURL(file);
}

// Dynamic Form Functions
function initializeDynamicForms() {
    // Services offered conditional sections
    var servicesCheckboxes = document.querySelectorAll('input[name="services_offered"]');
    servicesCheckboxes.forEach(function(checkbox) {
        checkbox.addEventListener('change', toggleConditionalSections);
    });
    
    // Workstation count dynamic fields
    var workstationCountInput = document.getElementById('total_workstations');
    if (workstationCountInput) {
        workstationCountInput.addEventListener('change', generateWorkstationFields);
    }
    
    // Software sections
    initializeSoftwareSections();
    
    // Initial check
    toggleConditionalSections();
}

function toggleConditionalSections() {
    var selectedServices = Array.from(document.querySelectorAll('input[name="services_offered"]:checked'))
                               .map(cb => cb.value);
    
    // Audio software section
    var audioServices = ['adr', 'musical_scoring', 'sound_design', 'audio_editing', 'music_research', 'music_clearance', 'music_creation'];
    var showAudio = audioServices.some(service => selectedServices.includes(service));
    toggleSection('audio-software-section', showAudio);
    
    // Editing software section
    var editingServices = ['video_editing', 'color_correction', 'compositing'];
    var showEditing = editingServices.some(service => selectedServices.includes(service));
    toggleSection('editing-software-section', showEditing);
    
    // Graphics software section
    var graphicsServices = ['2d_animation', '3d_animation', 'special_effects'];
    var showGraphics = graphicsServices.some(service => selectedServices.includes(service));
    toggleSection('graphics-software-section', showGraphics);
    
    // Staff sections
    toggleSection('audio-staff-section', showAudio);
    toggleSection('editing-staff-section', showEditing);
    toggleSection('graphics-staff-section', showGraphics);
}

function toggleSection(sectionId, show) {
    var section = document.getElementById(sectionId);
    if (section) {
        if (show) {
            section.classList.remove('d-none');
            section.style.display = 'block';
        } else {
            section.classList.add('d-none');
            section.style.display = 'none';
        }
    }
}

function generateWorkstationFields() {
    var count = parseInt(this.value) || 0;
    var container = document.getElementById('workstations-container');
    
    if (!container) return;
    
    container.innerHTML = '';
    
    for (var i = 1; i <= count; i++) {
        var workstationHtml = generateWorkstationHtml(i);
        container.insertAdjacentHTML('beforeend', workstationHtml);
    }
}

function generateWorkstationHtml(number) {
    return `
        <div class="card mb-3">
            <div class="card-header">
                <h6 class="mb-0">Workstation ${number}</h6>
            </div>
            <div class="card-body">
                <div class="row">
                    <div class="col-md-6 mb-3">
                        <label class="form-label">Machine Name</label>
                        <input type="text" class="form-control" name="workstation${number}_machine_name" required>
                    </div>
                    <div class="col-md-6 mb-3">
                        <label class="form-label">Functions</label>
                        <div>
                            <div class="form-check form-check-inline">
                                <input class="form-check-input" type="checkbox" name="workstation${number}_functions" value="audio_editing">
                                <label class="form-check-label">Audio Editing</label>
                            </div>
                            <div class="form-check form-check-inline">
                                <input class="form-check-input" type="checkbox" name="workstation${number}_functions" value="video_editing">
                                <label class="form-check-label">Video Editing</label>
                            </div>
                            <div class="form-check form-check-inline">
                                <input class="form-check-input" type="checkbox" name="workstation${number}_functions" value="graphics">
                                <label class="form-check-label">Graphics</label>
                            </div>
                        </div>
                    </div>
                </div>
                <div class="row">
                    <div class="col-md-6 mb-3">
                        <label class="form-label">Device Model</label>
                        <input type="text" class="form-control" name="workstation${number}_device_model" required>
                    </div>
                    <div class="col-md-6 mb-3">
                        <label class="form-label">Operating System</label>
                        <input type="text" class="form-control" name="workstation${number}_operating_system" required>
                    </div>
                </div>
                <div class="row">
                    <div class="col-md-6 mb-3">
                        <label class="form-label">Processor</label>
                        <input type="text" class="form-control" name="workstation${number}_processor" required>
                    </div>
                    <div class="col-md-6 mb-3">
                        <label class="form-label">Graphics Card Model</label>
                        <input type="text" class="form-control" name="workstation${number}_graphics_card">
                        <div class="form-text">Disregard for Mac</div>
                    </div>
                </div>
                <div class="row">
                    <div class="col-md-6 mb-3">
                        <label class="form-label">Memory</label>
                        <input type="text" class="form-control" name="workstation${number}_memory" required>
                    </div>
                    <div class="col-md-6 mb-3">
                        <label class="form-label">Monitor</label>
                        <input type="text" class="form-control" name="workstation${number}_monitor" required>
                    </div>
                </div>
                <div class="row">
                    <div class="col-md-6 mb-3">
                        <label class="form-label">Monitor Professionally Calibrated?</label>
                        <select class="form-select" name="workstation${number}_monitor_calibrated">
                            <option value="">Select...</option>
                            <option value="yes">Yes</option>
                            <option value="no">No</option>
                        </select>
                    </div>
                    <div class="col-md-6 mb-3">
                        <div class="form-check mt-4">
                            <input class="form-check-input" type="checkbox" name="workstation${number}_io_devices" value="1">
                            <label class="form-check-label">Has IO Devices (AJA/BlackMagic/Matrox)</label>
                        </div>
                    </div>
                </div>
                <div class="row">
                    <div class="col-md-6 mb-3">
                        <label class="form-label">Speaker Model</label>
                        <input type="text" class="form-control" name="workstation${number}_speaker_model">
                    </div>
                    <div class="col-md-6 mb-3">
                        <label class="form-label">Headphone/Headset Model</label>
                        <input type="text" class="form-control" name="workstation${number}_headphone_model">
                    </div>
                </div>
            </div>
        </div>
    `;
}

function initializeSoftwareSections() {
    // Handle software checkbox changes
    var softwareCheckboxes = document.querySelectorAll('.software-checkbox');
    softwareCheckboxes.forEach(function(checkbox) {
        checkbox.addEventListener('change', function() {
            var softwareRow = this.closest('.software-row');
            var inputs = softwareRow.querySelectorAll('input:not([type="checkbox"]), select');
            
            inputs.forEach(function(input) {
                input.disabled = !checkbox.checked;
                if (!checkbox.checked) {
                    input.value = '';
                }
            });
        });
    });
    
    // Handle free version checkboxes
    var freeCheckboxes = document.querySelectorAll('.free-version-checkbox');
    freeCheckboxes.forEach(function(checkbox) {
        checkbox.addEventListener('change', function() {
            var fileInput = this.closest('.software-row').querySelector('input[type="file"]');
            if (fileInput) {
                fileInput.disabled = this.checked;
                if (this.checked) {
                    fileInput.value = '';
                }
            }
        });
    });
}

// Data Tables
function initializeDataTables() {
    var tables = document.querySelectorAll('.data-table');
    tables.forEach(function(table) {
        // Add sorting functionality
        var headers = table.querySelectorAll('th[data-sort]');
        headers.forEach(function(header) {
            header.style.cursor = 'pointer';
            header.addEventListener('click', function() {
                sortTable(table, this.cellIndex, this.dataset.sort);
            });
        });
    });
}

function sortTable(table, columnIndex, sortType) {
    var tbody = table.querySelector('tbody');
    var rows = Array.from(tbody.querySelectorAll('tr'));
    var isAscending = table.dataset.sortOrder !== 'asc';
    
    rows.sort(function(a, b) {
        var aValue = a.cells[columnIndex].textContent.trim();
        var bValue = b.cells[columnIndex].textContent.trim();
        
        if (sortType === 'number') {
            aValue = parseFloat(aValue) || 0;
            bValue = parseFloat(bValue) || 0;
        } else if (sortType === 'date') {
            aValue = new Date(aValue);
            bValue = new Date(bValue);
        }
        
        if (aValue < bValue) return isAscending ? -1 : 1;
        if (aValue > bValue) return isAscending ? 1 : -1;
        return 0;
    });
    
    rows.forEach(function(row) {
        tbody.appendChild(row);
    });
    
    table.dataset.sortOrder = isAscending ? 'asc' : 'desc';
    
    // Update sort indicators
    table.querySelectorAll('th').forEach(function(th) {
        th.classList.remove('sort-asc', 'sort-desc');
    });
    table.querySelectorAll('th')[columnIndex].classList.add(isAscending ? 'sort-asc' : 'sort-desc');
}

// AJAX Functions
function initializeAjaxForms() {
    var ajaxForms = document.querySelectorAll('.ajax-form');
    ajaxForms.forEach(function(form) {
        form.addEventListener('submit', handleAjaxForm);
    });
}

function handleAjaxForm(e) {
    e.preventDefault();
    var form = e.target;
    var formData = new FormData(form);
    var url = form.action || window.location.href;
    var method = form.method || 'POST';
    
    // Show loading state
    var submitBtn = form.querySelector('button[type="submit"]');
    var originalText = submitBtn.textContent;
    submitBtn.disabled = true;
    submitBtn.innerHTML = '<span class="spinner-border spinner-border-sm me-2"></span>Processing...';
    
    fetch(url, {
        method: method,
        body: formData,
        headers: {
            'X-Requested-With': 'XMLHttpRequest'
        }
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            showAlert(data.message || 'Operation completed successfully', 'success');
            if (data.redirect) {
                setTimeout(() => window.location.href = data.redirect, 1500);
            }
        } else {
            showAlert(data.message || 'An error occurred', 'danger');
        }
    })
    .catch(error => {
        console.error('Error:', error);
        showAlert('An error occurred while processing your request', 'danger');
    })
    .finally(() => {
        // Restore button state
        submitBtn.disabled = false;
        submitBtn.textContent = originalText;
    });
}

// Real-time Validation
function initializeRealTimeValidation() {
    // Username availability check
    var usernameInput = document.getElementById('username');
    if (usernameInput) {
        var usernameTimeout;
        usernameInput.addEventListener('input', function() {
            clearTimeout(usernameTimeout);
            usernameTimeout = setTimeout(() => checkUsernameAvailability(this.value), 500);
        });
    }
    
    // Email availability check
    var emailInput = document.getElementById('email');
    if (emailInput) {
        var emailTimeout;
        emailInput.addEventListener('input', function() {
            clearTimeout(emailTimeout);
            emailTimeout = setTimeout(() => checkEmailAvailability(this.value), 500);
        });
    }
    
    // Password strength indicator
    var passwordInput = document.getElementById('password');
    if (passwordInput) {
        passwordInput.addEventListener('input', function() {
            updatePasswordStrength(this.value);
        });
    }
}

function checkUsernameAvailability(username) {
    if (username.length < 3) return;
    
    fetch('/auth/api/check-username', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({username: username})
    })
    .then(response => response.json())
    .then(data => {
        var input = document.getElementById('username');
        var feedback = input.parentNode.querySelector('.username-feedback') || 
                      createFeedbackElement(input, 'username-feedback');
        
        if (data.available) {
            input.classList.remove('is-invalid');
            input.classList.add('is-valid');
            feedback.className = 'username-feedback valid-feedback';
            feedback.textContent = 'Username is available';
        } else {
            input.classList.remove('is-valid');
            input.classList.add('is-invalid');
            feedback.className = 'username-feedback invalid-feedback';
            feedback.textContent = data.message;
        }
    });
}

function checkEmailAvailability(email) {
    if (!isValidEmail(email)) return;
    
    fetch('/auth/api/check-email', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({email: email})
    })
    .then(response => response.json())
    .then(data => {
        var input = document.getElementById('email');
        var feedback = input.parentNode.querySelector('.email-feedback') || 
                      createFeedbackElement(input, 'email-feedback');
        
        if (data.available) {
            input.classList.remove('is-invalid');
            input.classList.add('is-valid');
            feedback.className = 'email-feedback valid-feedback';
            feedback.textContent = 'Email is available';
        } else {
            input.classList.remove('is-valid');
            input.classList.add('is-invalid');
            feedback.className = 'email-feedback invalid-feedback';
            feedback.textContent = data.message;
        }
    });
}

function updatePasswordStrength(password) {
    var strengthBar = document.querySelector('.password-strength') || 
                     createPasswordStrengthIndicator();
    
    var strength = calculatePasswordStrength(password);
    var strengthText = ['Very Weak', 'Weak', 'Fair', 'Good', 'Strong'];
    var strengthColors = ['danger', 'warning', 'info', 'primary', 'success'];
    
    strengthBar.className = `progress-bar bg-${strengthColors[strength]}`;
    strengthBar.style.width = `${(strength + 1) * 20}%`;
    strengthBar.textContent = strengthText[strength];
}

function calculatePasswordStrength(password) {
    var score = 0;
    if (password.length >= 8) score++;
    if (/[a-z]/.test(password)) score++;
    if (/[A-Z]/.test(password)) score++;
    if (/[0-9]/.test(password)) score++;
    if (/[^A-Za-z0-9]/.test(password)) score++;
    return Math.min(score - 1, 4);
}

function createFeedbackElement(input, className) {
    var feedback = document.createElement('div');
    feedback.className = className;
    input.parentNode.appendChild(feedback);
    return feedback;
}

function createPasswordStrengthIndicator() {
    var passwordInput = document.getElementById('password');
    var container = document.createElement('div');
    container.className = 'progress mt-2';
    container.style.height = '4px';
    
    var bar = document.createElement('div');
    bar.className = 'progress-bar password-strength';
    bar.style.width = '0%';
    
    container.appendChild(bar);
    passwordInput.parentNode.appendChild(container);
    
    return bar;
}

// Form Auto-save (for external forms)
function initializeAutoSave() {
    var form = document.querySelector('.auto-save-form');
    if (!form) return;
    
    var inputs = form.querySelectorAll('input, select, textarea');
    var saveTimeout;
    
    inputs.forEach(function(input) {
        input.addEventListener('change', function() {
            clearTimeout(saveTimeout);
            saveTimeout = setTimeout(autoSaveForm, 2000);
        });
    });
}

function autoSaveForm() {
    var form = document.querySelector('.auto-save-form');
    if (!form) return;
    
    var formData = new FormData(form);
    
    fetch(form.action + '?auto_save=1', {
        method: 'POST',
        body: formData
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            showAutoSaveIndicator();
        }
    })
    .catch(error => {
        console.log('Auto-save failed:', error);
    });
}

function showAutoSaveIndicator() {
    var indicator = document.querySelector('.auto-save-indicator');
    if (!indicator) {
        indicator = document.createElement('div');
        indicator.className = 'auto-save-indicator position-fixed bottom-0 end-0 p-3';
        indicator.innerHTML = '<small class="text-muted"><i class="bi bi-check-circle me-1"></i>Auto-saved</small>';
        document.body.appendChild(indicator);
    }
    
    indicator.style.display = 'block';
    setTimeout(() => {
        indicator.style.display = 'none';
    }, 2000);
}

// Utility Functions
function showAlert(message, type = 'info') {
    var alertDiv = document.createElement('div');
    alertDiv.className = `alert alert-${type} alert-dismissible fade show`;
    alertDiv.innerHTML = `
        <i class="bi bi-${getAlertIcon(type)} me-2"></i>
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;
    
    var container = document.querySelector('.container');
    if (container) {
        container.insertBefore(alertDiv, container.firstChild);
    }
    
    // Auto-dismiss after 5 seconds
    setTimeout(() => {
        var alert = new bootstrap.Alert(alertDiv);
        alert.close();
    }, 5000);
}

function getAlertIcon(type) {
    var icons = {
        'success': 'check-circle',
        'danger': 'exclamation-triangle',
        'warning': 'exclamation-circle',
        'info': 'info-circle'
    };
    return icons[type] || 'info-circle';
}

function isValidEmail(email) {
    var re = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return re.test(email);
}

function showLoading() {
    var overlay = document.createElement('div');
    overlay.className = 'spinner-overlay';
    overlay.innerHTML = `
        <div class="spinner-border spinner-border-lg text-light" role="status">
            <span class="visually-hidden">Loading...</span>
        </div>
    `;
    document.body.appendChild(overlay);
}

function hideLoading() {
    var overlay = document.querySelector('.spinner-overlay');
    if (overlay) {
        overlay.remove();
    }
}

function confirmAction(message, callback) {
    if (confirm(message)) {
        callback();
    }
}

// QR Code Display (for 2FA setup)
function displayQRCode(qrCodeData) {
    var modal = new bootstrap.Modal(document.getElementById('qrCodeModal'));
    var qrCodeContainer = document.getElementById('qrCodeContainer');
    qrCodeContainer.innerHTML = `<img src="data:image/png;base64,${qrCodeData}" class="img-fluid">`;
    modal.show();
}

// Copy to Clipboard
function copyToClipboard(text, element) {
    navigator.clipboard.writeText(text).then(function() {
        var originalText = element.textContent;
        element.textContent = 'Copied!';
        element.classList.add('btn-success');
        
        setTimeout(function() {
            element.textContent = originalText;
            element.classList.remove('btn-success');
        }, 2000);
    });
}

// Chart initialization (if charts are present)
function initializeCharts() {
    // This would integrate with Chart.js or similar library
    // for dashboard statistics display
    if (typeof Chart !== 'undefined') {
        // Charts are already initialized in individual templates
        console.log('Charts library loaded');
    }
}

// Search functionality
function initializeSearch() {
    var searchInputs = document.querySelectorAll('.search-input');
    searchInputs.forEach(function(input) {
        var searchTimeout;
        input.addEventListener('input', function() {
            clearTimeout(searchTimeout);
            searchTimeout = setTimeout(() => {
                performSearch(this.value, this.dataset.target);
            }, 300);
        });
    });
}

function performSearch(query, target) {
    if (!target) return;
    
    var rows = document.querySelectorAll(`${target} tbody tr`);
    rows.forEach(function(row) {
        var text = row.textContent.toLowerCase();
        var matches = text.includes(query.toLowerCase());
        row.style.display = matches ? '' : 'none';
    });
}

// Form progress tracking
function initializeFormProgress() {
    var form = document.querySelector('.progress-form');
    if (!form) return;
    
    var sections = form.querySelectorAll('.form-section');
    var progressBar = document.querySelector('.form-progress');
    
    if (!progressBar) return;
    
    function updateProgress() {
        var completedSections = 0;
        
        sections.forEach(function(section) {
            var requiredFields = section.querySelectorAll('input[required], select[required], textarea[required]');
            var filledFields = 0;
            
            requiredFields.forEach(function(field) {
                if (field.value.trim() !== '') {
                    filledFields++;
                }
            });
            
            if (filledFields === requiredFields.length && requiredFields.length > 0) {
                completedSections++;
            }
        });
        
        var progress = (completedSections / sections.length) * 100;
        progressBar.style.width = progress + '%';
        progressBar.setAttribute('aria-valuenow', progress);
    }
    
    // Update progress on field changes
    form.addEventListener('input', updateProgress);
    form.addEventListener('change', updateProgress);
    
    // Initial progress calculation
    updateProgress();
}

// Keyboard shortcuts
function initializeKeyboardShortcuts() {
    document.addEventListener('keydown', function(e) {
        // Ctrl/Cmd + S for save
        if ((e.ctrlKey || e.metaKey) && e.key === 's') {
            e.preventDefault();
            var saveBtn = document.querySelector('.btn-save, button[type="submit"]');
            if (saveBtn) {
                saveBtn.click();
            }
        }
        
        // Escape to close modals
        if (e.key === 'Escape') {
            var openModal = document.querySelector('.modal.show');
            if (openModal) {
                var modal = bootstrap.Modal.getInstance(openModal);
                if (modal) {
                    modal.hide();
                }
            }
        }
    });
}

// Initialize all features when DOM is ready
document.addEventListener('DOMContentLoaded', function() {
    initializeSearch();
    initializeFormProgress();
    initializeKeyboardShortcuts();
    initializeCharts();
});

// Export functions for global access
window.PostAccreditation = {
    showAlert,
    showLoading,
    hideLoading,
    confirmAction,
    copyToClipboard,
    displayQRCode,
    autoSaveForm,
    showAutoSaveIndicator,
    updatePasswordStrength,
    checkUsernameAvailability,
    checkEmailAvailability
};
});

// File Upload Functions
function initializeFileUploads() {
    var fileInputs = document.querySelectorAll('input[type="file"]');
    
    fileInputs.forEach(function(input) {
        var dropArea = input.closest('.file-upload-area');
        
        if (dropArea) {
            ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
                dropArea.addEventListener(eventName, preventDefaults, false);
            });
            
            ['dragenter', 'dragover'].forEach(eventName => {
                dropArea.addEventListener(eventName, highlight, false);
            });
            
            ['dragleave', 'drop'].forEach(eventName => {
                dropArea.addEventListener(eventName, unhighlight, false);
            });
            
            dropArea.addEventListener('drop', handleDrop, false);
            dropArea.addEventListener('click', () => input.click());
        }
        
        input.addEventListener('change', function() {
            handleFiles(this.files, input);
        });
    });
}

function preventDefaults(e) {
    e.preventDefault();
    e.stopPropagation();
}

function highlight(e) {
    e.currentTarget.classList.add('dragover');
}

function unhighlight(e) {
    e.currentTarget.classList.remove('dragover');
}

function handleDrop(e) {
    var dt = e.dataTransfer;
    var files = dt.files;
    var input = e.currentTarget.querySelector('input[type="file"]');
    handleFiles(files, input);
}

function handleFiles(files, input) {
    if (files.length > 0) {
        var file = files[0];
        var maxSize = 16 * 1024 * 1024; // 16MB
        
        if (file.size > maxSize) {
            showAlert('File size exceeds 16MB limit', 'danger');
            return;
        }
        
        // Update UI to show selected file
        var fileName = file.name;
        var fileInfo = input.closest('.file-upload-area')?.querySelector('.file-info');
        if (fileInfo) {
            fileInfo.innerHTML = `<i class="bi bi-file-check me-2"></i>${fileName}`;
            fileInfo.classList.remove('d-none');
        }
        
        // If it's an image, show preview
        if (file.type.startsWith('image/')) {
            showImagePreview(file, input);
        }
    }
}

function showImagePreview(file, input) {
    var reader = new FileReader();
    reader.onload = function(e) {
        var preview = input.closest('.file-upload-area')?.querySelector('.image-preview');
        if (preview) {
            preview.innerHTML = `<img src="${e.target.result}" class="img-thumbnail mt-2" style="max-width: 200px;">`;
            preview.classList.remove('d-none');
        }
    };
    reader.readAsDataURL(file);
}

// Dynamic Form Functions
function initializeDynamicForms() {
    // Services offered conditional sections
    var servicesCheckboxes = document.querySelectorAll('input[name="services_offered"]');
    servicesCheckboxes.forEach(function(checkbox) {
        checkbox.addEventListener('change', toggleConditionalSections);
    });
    
    // Workstation count dynamic fields
    var workstationCountInput = document.getElementById('total_workstations');
    if (workstationCountInput) {
        workstationCountInput.addEventListener('change', generateWorkstationFields);
    }
    
    // Software sections
    initializeSoftwareSections();
    
    // Initial check
    toggleConditionalSections();
}

function toggleConditionalSections() {
    var selectedServices = Array.from(document.querySelectorAll('input[name="services_offered"]:checked'))
                               .map(cb => cb.value);
    
    // Audio software section
    var audioServices = ['adr', 'musical_scoring', 'sound_design', 'audio_editing', 'music_research', 'music_clearance', 'music_creation'];
    var showAudio = audioServices.some(service => selectedServices.includes(service));
    toggleSection('audio-software-section', showAudio);
    
    // Editing software section
    var editingServices = ['video_editing', 'color_correction', 'compositing'];
    var showEditing = editingServices.some(service => selectedServices.includes(service));
    toggleSection('editing-software-section', showEditing);
    
    // Graphics software section
    var graphicsServices = ['2d_animation', '3d_animation', 'special_effects'];
    var showGraphics = graphicsServices.some(service => selectedServices.includes(service));
    toggleSection('graphics-software-section', showGraphics);
    
    // Staff sections
    toggleSection('audio-staff-section', showAudio);
    toggleSection('editing-staff-section', showEditing);
    toggleSection('graphics-staff-section', showGraphics);
}

function toggleSection(sectionId, show) {
    var section = document.getElementById(sectionId);
    if (section) {
        if (show) {
            section.classList.remove('d-none');
            section.style.display = 'block';
        } else {
            section.classList.add('d-none');
            section.style.display = 'none';
        }
    }
}

function generateWorkstationFields() {
    var count = parseInt(this.value) || 0;
    var container = document.getElementById('workstations-container');
    
    if (!container) return;
    
    container.innerHTML = '';
    
    for (var i = 1; i <= count; i++) {
        var workstationHtml = generateWorkstationHtml(i);
        container.insertAdjacentHTML('beforeend', workstationHtml);
    }
}

function generateWorkstationHtml(number) {
    return `
        <div class="card mb-3">
            <div class="card-header">
                <h6 class="mb-0">Workstation ${number}</h6>
            </div>
            <div class="card-body">
                <div class="row">
                    <div class="col-md-6 mb-3">
                        <label class="form-label">Machine Name</label>
                        <input type="text" class="form-control" name="workstation${number}_machine_name" required>
                    </div>
                    <div class="col-md-6 mb-3">
                        <label class="form-label">Functions</label>
                        <div>
                            <div class="form-check form-check-inline">
                                <input class="form-check-input" type="checkbox" name="workstation${number}_functions" value="audio_editing">
                                <label class="form-check-label">Audio Editing</label>
                            </div>
                            <div class="form-check form-check-inline">
                                <input class="form-check-input" type="checkbox" name="workstation${number}_functions" value="video_editing">
                                <label class="form-check-label">Video Editing</label>
                            </div>
                            <div class="form-check form-check-inline">
                                <input class="form-check-input" type="checkbox" name="workstation${number}_functions" value="graphics">
                                <label class="form-check-label">Graphics</label>
                            </div>
                        </div>
                    </div>
                </div>
                <div class="row">
                    <div class="col-md-6 mb-3">
                        <label class="form-label">Device Model</label>
                        <input type="text" class="form-control" name="workstation${number}_device_model" required>
                    </div>
                    <div class="col-md-6 mb-3">
                        <label class="form-label">Operating System</label>
                        <input type="text" class="form-control" name="workstation${number}_operating_system" required>
                    </div>
                </div>
                <div class="row">
                    <div class="col-md-6 mb-3">
                        <label class="form-label">Processor</label>
                        <input type="text" class="form-control" name="workstation${number}_processor" required>
                    </div>
                    <div class="col-md-6 mb-3">
                        <label class="form-label">Graphics Card Model</label>
                        <input type="text" class="form-control" name="workstation${number}_graphics_card">
                        <div class="form-text">Disregard for Mac</div>
                    </div>
                </div>
                <div class="row">
                    <div class="col-md-6 mb-3">
                        <label class="form-label">Memory</label>
                        <input type="text" class="form-control" name="workstation${number}_memory" required>
                    </div>
                    <div class="col-md-6 mb-3">
                        <label class="form-label">Monitor</label>
                        <input type="text" class="form-control" name="workstation${number}_monitor" required>
                    </div>
                </div>
                <div class="row">
                    <div class="col-md-6 mb-3">
                        <label class="form-label">Monitor Professionally Calibrated?</label>
                        <select class="form-select" name="workstation${number}_monitor_calibrated">
                            <option value="">Select...</option>
                            <option value="yes">Yes</option>
                            <option value="no">No</option>
                        </select>
                    </div>
                    <div class="col-md-6 mb-3">
                        <div class="form-check mt-4">
                            <input class="form-check-input" type="checkbox" name="workstation${number}_io_devices" value="1">
                            <label class="form-check-label">Has IO Devices (AJA/BlackMagic/Matrox)</label>
                        </div>
                    </div>
                </div>
                <div class="row">
                    <div class="col-md-6 mb-3">
                        <label class="form-label">Speaker Model</label>
                        <input type="text" class="form-control" name="workstation${number}_speaker_model">
                    </div>
                    <div class="col-md-6 mb-3">
                        <label class="form-label">Headphone/Headset Model</label>
                        <input type="text" class="form-control" name="workstation${number}_headphone_model">
                    </div>
                </div>
            </div>
        </div>
    `;
}

function initializeSoftwareSections() {
    // Handle software checkbox changes
    var softwareCheckboxes = document.querySelectorAll('.software-checkbox');
    softwareCheckboxes.forEach(function(checkbox) {
        checkbox.addEventListener('change', function() {
            var softwareRow = this.closest('.software-row');
            var inputs = softwareRow.querySelectorAll('input:not([type="checkbox"]), select');
            
            inputs.forEach(function(input) {
                input.disabled = !checkbox.checked;
                if (!checkbox.checked) {
                    input.value = '';
                }
            });
        });
    });
    
    // Handle free version checkboxes
    var freeCheckboxes = document.querySelectorAll('.free-version-checkbox');
    freeCheckboxes.forEach(function(checkbox) {
        checkbox.addEventListener('change', function() {
            var fileInput = this.closest('.software-row').querySelector('input[type="file"]');
            if (fileInput) {
                fileInput.disabled = this.checked;
                if (this.checked) {
                    fileInput.value = '';
                }
            }
        });
    });
}

// Data Tables
function initializeDataTables() {
    var tables = document.querySelectorAll('.data-table');
    tables.forEach(function(table) {
        // Add sorting functionality
        var headers = table.querySelectorAll('th[data-sort]');
        headers.forEach(function(header) {
            header.style.cursor = 'pointer';
            header.addEventListener('click', function() {
                sortTable(table, this.cellIndex, this.dataset.sort);
            });
        });
    });
}

function sortTable(table, columnIndex, sortType) {
    var tbody = table.querySelector('tbody');
    var rows = Array.from(tbody.querySelectorAll('tr'));
    var isAscending = table.dataset.sortOrder !== 'asc';
    
    rows.sort(function(a, b) {
        var aValue = a.cells[columnIndex].textContent.trim();
        var bValue = b.cells[columnIndex].textContent.trim();
        
        if (sortType === 'number') {
            aValue = parseFloat(aValue) || 0;
            bValue = parseFloat(bValue) || 0;
        } else if (sortType === 'date') {
            aValue = new Date(aValue);
            bValue = new Date(bValue);
        }
        
        if (aValue < bValue) return isAscending ? -1 : 1;
        if (aValue > bValue) return isAscending ? 1 : -1;
        return 0;
    });
    
    rows.forEach(function(row) {
        tbody.appendChild(row);
    });
    
    table.dataset.sortOrder = isAscending ? 'asc' : 'desc';
    
    // Update sort indicators
    table.querySelectorAll('th').forEach(function(th) {
        th.classList.remove('sort-asc', 'sort-desc');
    });
    table.querySelectorAll('th')[columnIndex].classList.add(isAscending ? 'sort-asc' : 'sort-desc');
}

// AJAX Functions
function initializeAjaxForms() {
    var ajaxForms = document.querySelectorAll('.ajax-form');
    ajaxForms.forEach(function(form) {
        form.addEventListener('submit', handleAjaxForm);
    });
}

function handleAjaxForm(e) {
    e.preventDefault();
    var form = e.target;
    var formData = new FormData(form);
    var url = form.action || window.location.href;
    var method = form.method || 'POST';
    
    // Show loading state
    var submitBtn = form.querySelector('button[type="submit"]');
    var originalText = submitBtn.textContent;
    submitBtn.disabled = true;
    submitBtn.innerHTML = '<span class="spinner-border spinner-border-sm me-2"></span>Processing...';
    
    fetch(url, {
        method: method,
        body: formData,
        headers: {
            'X-Requested-With': 'XMLHttpRequest'
        }
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            showAlert(data.message || 'Operation completed successfully', 'success');
            if (data.redirect) {
                setTimeout(() => window.location.href = data.redirect, 1500);
            }
        } else {
            showAlert(data.message || 'An error occurred', 'danger');
        }
    })
    .catch(error => {
        console.error('Error:', error);
        showAlert('An error occurred while processing your request', 'danger');
    })
    .finally(() => {
        // Restore button state
        submitBtn.disabled = false;
        submitBtn.textContent = originalText;
    });
}

// Real-time Validation
function initializeRealTimeValidation() {
    // Username availability check
    var usernameInput = document.getElementById('username');
    if (usernameInput) {
        var usernameTimeout;
        usernameInput.addEventListener('input', function() {
            clearTimeout(usernameTimeout);
            usernameTimeout = setTimeout(() => checkUsernameAvailability(this.value), 500);
        });
    }
    
    // Email availability check
    var emailInput = document.getElementById('email');
    if (emailInput) {
        var emailTimeout;
        emailInput.addEventListener('input', function() {
            clearTimeout(emailTimeout);
            emailTimeout = setTimeout(() => checkEmailAvailability(this.value), 500);
        });
    }
    
    // Password strength indicator
    var passwordInput = document.getElementById('password');
    if (passwordInput) {
        passwordInput.addEventListener('input', function() {
            updatePasswordStrength(this.value);
        });
    }
}

function checkUsernameAvailability(username) {
    if (username.length < 3) return;
    
    fetch('/auth/api/check-username', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({username: username})
    })
    .then(response => response.json())
    .then(data => {
        var input = document.getElementById('username');
        var feedback = input.parentNode.querySelector('.username-feedback') || 
                      createFeedbackElement(input, 'username-feedback');
        
        if (data.available) {
            input.classList.remove('is-invalid');
            input.classList.add('is-valid');
            feedback.className = 'username-feedback valid-feedback';
            feedback.textContent = 'Username is available';
        } else {
            input.classList.remove('is-valid');
            input.classList.add('is-invalid');
            feedback.className = 'username-feedback invalid-feedback';
            feedback.textContent = data.message;
        }
    });
}

function checkEmailAvailability(email) {
    if (!isValidEmail(email)) return;
    
    fetch('/auth/api/check-email', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({email: email})
    })
    .then(response => response.json())
    .then(data => {
        var input = document.getElementById('email');
        var feedback = input.parentNode.querySelector('.email-feedback') || 
                      createFeedbackElement(input, 'email-feedback');
        
        if (data.available) {
            input.classList.remove('is-invalid');
            input.classList.add('is-valid');
            feedback.className = 'email-feedback valid-feedback';
            feedback.textContent = 'Email is available';
        } else {
            input.classList.remove('is-valid');
            input.classList.add('is-invalid');
            feedback.className = 'email-feedback invalid-feedback';
            feedback.textContent = data.message;
        }
    });
}

function updatePasswordStrength(password) {
    var strengthBar = document.querySelector('.password-strength') || 
                     createPasswordStrengthIndicator();
    
    var strength = calculatePasswordStrength(password);
    var strengthText = ['Very Weak', 'Weak', 'Fair', 'Good', 'Strong'];
    var strengthColors = ['danger', 'warning', 'info', 'primary', 'success'];
    
    strengthBar.className = `progress-bar bg-${strengthColors[strength]}`;
    strengthBar.style.width = `${(strength + 1) * 20}%`;
    strengthBar.textContent = strengthText[strength];
}

function calculatePasswordStrength(password) {
    var score = 0;
    if (password.length >= 8) score++;
    if (/[a-z]/.test(password)) score++;
    if (/[A-Z]/.test(password)) score++;
    if (/[0-9]/.test(password)) score++;
    if (/[^A-Za-z0-9]/.test(password)) score++;
    return Math.min(score - 1, 4);
}

function createFeedbackElement(input, className) {
    var feedback = document.createElement('div');
    feedback.className = className;
    input.parentNode.appendChild(feedback);
    return feedback;
}

function createPasswordStrengthIndicator() {
    var passwordInput = document.getElementById('password');
    var container = document.createElement('div');
    container.className = 'progress mt-2';
    container.style.height = '4px';
    
    var bar = document.createElement('div');
    bar.className = 'progress-bar password-strength';
    bar.style.width = '0%';
    
    container.appendChild(bar);
    passwordInput.parentNode.appendChild(container);
    
    return bar;
}

// Form Auto-save (for external forms)
function initializeAutoSave() {
    var form = document.querySelector('.auto-save-form');
    if (!form) return;
    
    var inputs = form.querySelectorAll('input, select, textarea');
    var saveTimeout;
    
    inputs.forEach(function(input) {
        input.addEventListener('change', function() {
            clearTimeout(saveTimeout);
            saveTimeout = setTimeout(autoSaveForm, 2000);
        });
    });
}

function autoSaveForm() {
    var form = document.querySelector('.auto-save-form');
    if (!form) return;
    
    var formData = new FormData(form);
    
    fetch(form.action + '?auto_save=1', {
        method: 'POST',
        body: formData
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            showAutoSaveIndicator();
        }
    })
    .catch(error => {
        console.log('Auto-save failed:', error);
    });
}

function showAutoSaveIndicator() {
    var indicator = document.querySelector('.auto-save-indicator');
    if (!indicator) {
        indicator = document.createElement('div');
        indicator.className = 'auto-save-indicator position-fixed bottom-0 end-0 p-3';
        indicator.innerHTML = '<small class="text-muted"><i class="bi bi-check-circle me-1"></i>Auto-saved</small>';
        document.body.appendChild(indicator);
    }
    
    indicator.style.display = 'block';
    setTimeout(() => {
        indicator.style.display = 'none';
    }, 2000);
}

// Utility Functions
function showAlert(message, type = 'info') {
    var alertDiv = document.createElement('div');
    alertDiv.className = `alert alert-${type} alert-dismissible fade show`;
    alertDiv.innerHTML = `
        <i class="bi bi-${getAlertIcon(type)} me-2"></i>
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;
    
    var container = document.querySelector('.container');
    if (container) {
        container.insertBefore(alertDiv, container.firstChild);
    }
    
    // Auto-dismiss after 5 seconds
    setTimeout(() => {
        var alert = new bootstrap.Alert(alertDiv);
        alert.close();
    }, 5000);
}

function getAlertIcon(type) {
    var icons = {
        'success': 'check-circle',
        'danger': 'exclamation-triangle',
        'warning': 'exclamation-circle',
        'info': 'info-circle'
    };
    return icons[type] || 'info-circle';
}

function isValidEmail(email) {
    var re = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return re.test(email);
}

function showLoading() {
    var overlay = document.createElement('div');
    overlay.className = 'spinner-overlay';
    overlay.innerHTML = `
        <div class="spinner-border spinner-border-lg text-light" role="status">
            <span class="visually-hidden">Loading...</span>
        </div>
    `;
    document.body.appendChild(overlay);
}

function hideLoading() {
    var overlay = document.querySelector('.spinner-overlay');
    if (overlay) {
        overlay.remove();
    }
}

function confirmAction(message, callback) {
    if (confirm(message)) {
        callback();
    }
}

// QR Code Display (for 2FA setup)
function displayQRCode(qrCodeData) {
    var modal = new bootstrap.Modal(document.getElementById('qrCodeModal'));
    var qrCodeContainer = document.getElementById('qrCodeContainer');
    qrCodeContainer.innerHTML = `<img src="data:image/png;base64,${qrCodeData}" class="img-fluid">`;
    modal.show();
}

// Copy to Clipboard
function copyToClipboard(text, element) {
    navigator.clipboard.writeText(text).then(function() {
        var originalText = element.textContent;
        element.textContent = 'Copied!';
        element.classList.add('btn-success');
        
        setTimeout(function() {
            element.textContent = originalText;
            element.classList.remove('btn-success');
        }, 2000);
    });
}

// Chart initialization (if charts are present)
function initializeCharts() {
    // This would integrate with Chart.js or similar library
    // for dashboard statistics display
    if (typeof Chart !== 'undefined') {
        // Charts are already initialized in individual templates
        console.log('Charts library loaded');
    }
}

// Search functionality
function initializeSearch() {
    var searchInputs = document.querySelectorAll('.search-input');
    searchInputs.forEach(function(input) {
        var searchTimeout;
        input.addEventListener('input', function() {
            clearTimeout(searchTimeout);
            searchTimeout = setTimeout(() => {
                performSearch(this.value, this.dataset.target);
            }, 300);
        });
    });
}

function performSearch(query, target) {
    if (!target) return;
    
    var rows = document.querySelectorAll(`${target} tbody tr`);
    rows.forEach(function(row) {
        var text = row.textContent.toLowerCase();
        var matches = text.includes(query.toLowerCase());
        row.style.display = matches ? '' : 'none';
    });
}

// Form progress tracking
function initializeFormProgress() {
    var form = document.querySelector('.progress-form');
    if (!form) return;
    
    var sections = form.querySelectorAll('.form-section');
    var progressBar = document.querySelector('.form-progress');
    
    if (!progressBar) return;
    
    function updateProgress() {
        var completedSections = 0;
        
        sections.forEach(function(section) {
            var requiredFields = section.querySelectorAll('input[required], select[required], textarea[required]');
            var filledFields = 0;
            
            requiredFields.forEach(function(field) {
                if (field.value.trim() !== '') {
                    filledFields++;
                }
            });
            
            if (filledFields === requiredFields.length && requiredFields.length > 0) {
                completedSections++;
            }
        });
        
        var progress = (completedSections / sections.length) * 100;
        progressBar.style.width = progress + '%';
        progressBar.setAttribute('aria-valuenow', progress);
    }
    
    // Update progress on field changes
    form.addEventListener('input', updateProgress);
    form.addEventListener('change', updateProgress);
    
    // Initial progress calculation
    updateProgress();
}

// Keyboard shortcuts
function initializeKeyboardShortcuts() {
    document.addEventListener('keydown', function(e) {
        // Ctrl/Cmd + S for save
        if ((e.ctrlKey || e.metaKey) && e.key === 's') {
            e.preventDefault();
            var saveBtn = document.querySelector('.btn-save, button[type="submit"]');
            if (saveBtn) {
                saveBtn.click();
            }
        }
        
        // Escape to close modals
        if (e.key === 'Escape') {
            var openModal = document.querySelector('.modal.show');
            if (openModal) {
                var modal = bootstrap.Modal.getInstance(openModal);
                if (modal) {
                    modal.hide();
                }
            }
        }
    });
}

// Initialize all features when DOM is ready
document.addEventListener('DOMContentLoaded', function() {
    initializeSearch();
    initializeFormProgress();
    initializeKeyboardShortcuts();
    initializeCharts();
});

// Export functions for global access
window.PostAccreditation = {
    showAlert,
    showLoading,
    hideLoading,
    confirmAction,
    copyToClipboard,
    displayQRCode,
    autoSaveForm,
    showAutoSaveIndicator,
    updatePasswordStrength,
    checkUsernameAvailability,
    checkEmailAvailability
};var alerts = document.querySelectorAll('.alert:not(.alert-important)');
        alerts.forEach(function(alert) {
            var bsAlert = new bootstrap.Alert(alert);
            bsAlert.close();
        });
    }, 5000);

    // Form validation enhancements
    var forms = document.querySelectorAll('.needs-validation');
    Array.prototype.slice.call(forms).forEach(function(form) {
        form.addEventListener('submit', function(event) {
            if (!form.checkValidity()) {
                event.preventDefault();
                event.stopPropagation();
            }
            form.classList.add('was-validated');
        }, false);
    });

    // File upload enhancements
    initializeFileUploads();
    
    // Dynamic form sections
    initializeDynamicForms();
    
    // Initialize data tables
    initializeDataTables();
    
    // AJAX form handlers
    initializeAjaxForms();
    
    // Real-time validation
    initializeRealTimeValidation();
});

// File Upload Functions
function initializeFileUploads() {
    var fileInputs = document.querySelectorAll('input[type="file"]');
    
    fileInputs.forEach(function(input) {
        var dropArea = input.closest('.file-upload-area');
        
        if (dropArea) {
            ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
                dropArea.addEventListener(eventName, preventDefaults, false);
            });
            
            ['dragenter', 'dragover'].forEach(eventName => {
                dropArea.addEventListener(eventName, highlight, false);
            });
            
            ['dragleave', 'drop'].forEach(eventName => {
                dropArea.addEventListener(eventName, unhighlight, false);
            });
            
            dropArea.addEventListener('drop', handleDrop, false);
            dropArea.addEventListener('click', () => input.click());
        }
        
        input.addEventListener('change', function() {
            handleFiles(this.files, input);
        });
    });
}

function preventDefaults(e) {
    e.preventDefault();
    e.stopPropagation();
}

function highlight(e) {
    e.currentTarget.classList.add('dragover');
}

function unhighlight(e) {
    e.currentTarget.classList.remove('dragover');
}

function handleDrop(e) {
    var dt = e.dataTransfer;
    var files = dt.files;
    var input = e.currentTarget.querySelector('input[type="file"]');
    handleFiles(files, input);
}

function handleFiles(files, input) {
    if (files.length > 0) {
        var file = files[0];
        var maxSize = 16 * 1024 * 1024; // 16MB
        
        if (file.size > maxSize) {
            showAlert('File size exceeds 16MB limit', 'danger');
            return;
        }
        
        // Update UI to show selected file
        var fileName = file.name;
        var fileInfo = input.closest('.file-upload-area')?.querySelector('.file-info');
        if (fileInfo) {
            fileInfo.innerHTML = `<i class="bi bi-file-check me-2"></i>${fileName}`;
            fileInfo.classList.remove('d-none');
        }
        
        // If it's an image, show preview
        if (file.type.startsWith('image/')) {
            showImagePreview(file, input);
        }
    }
}

function showImagePreview(file, input) {
    var reader = new FileReader();
    reader.onload = function(e) {
        var preview = input.closest('.file-upload-area')?.querySelector('.image-preview');
        if (preview) {
            preview.innerHTML = `<img src="${e.target.result}" class="img-thumbnail mt-2" style="max-width: 200px;">`;
            preview.classList.remove('d-none');
        }
    };
    reader.readAsDataURL(file);
}

// Dynamic Form Functions
function initializeDynamicForms() {
    // Services offered conditional sections
    var servicesCheckboxes = document.querySelectorAll('input[name="services_offered"]');
    servicesCheckboxes.forEach(function(checkbox) {
        checkbox.addEventListener('change', toggleConditionalSections);
    });
    
    // Workstation count dynamic fields
    var workstationCountInput = document.getElementById('total_workstations');
    if (workstationCountInput) {
        workstationCountInput.addEventListener('change', generateWorkstationFields);
    }
    
    // Software sections
    initializeSoftwareSections();
    
    // Initial check
    toggleConditionalSections();
}

function toggleConditionalSections() {
    var selectedServices = Array.from(document.querySelectorAll('input[name="services_offered"]:checked'))
                               .map(cb => cb.value);
    
    // Audio software section
    var audioServices = ['adr', 'musical_scoring', 'sound_design', 'audio_editing', 'music_research', 'music_clearance', 'music_creation'];
    var showAudio = audioServices.some(service => selectedServices.includes(service));
    toggleSection('audio-software-section', showAudio);
    
    // Editing software section
    var editingServices = ['video_editing', 'color_correction', 'compositing'];
    var showEditing = editingServices.some(service => selectedServices.includes(service));
    toggleSection('editing-software-section', showEditing);
    
    // Graphics software section
    var graphicsServices = ['2d_animation', '3d_animation', 'special_effects'];
    var showGraphics = graphicsServices.some(service => selectedServices.includes(service));
    toggleSection('graphics-software-section', showGraphics);
    
    // Staff sections
    toggleSection('audio-staff-section', showAudio);
    toggleSection('editing-staff-section', showEditing);
    toggleSection('graphics-staff-section', showGraphics);
}

function toggleSection(sectionId, show) {
    var section = document.getElementById(sectionId);
    if (section) {
        if (show) {
            section.classList.remove('d-none');
            section.style.display = 'block';
        } else {
            section.classList.add('d-none');
            section.style.display = 'none';
        }
    }
}

function generateWorkstationFields() {
    var count = parseInt(this.value) || 0;
    var container = document.getElementById('workstations-container');
    
    if (!container) return;
    
    container.innerHTML = '';
    
    for (var i = 1; i <= count; i++) {
        var workstationHtml = generateWorkstationHtml(i);
        container.insertAdjacentHTML('beforeend', workstationHtml);
    }
}

function generateWorkstationHtml(number) {
    return `
        <div class="card mb-3">
            <div class="card-header">
                <h6 class="mb-0">Workstation ${number}</h6>
            </div>
            <div class="card-body">
                <div class="row">
                    <div class="col-md-6 mb-3">
                        <label class="form-label">Machine Name</label>
                        <input type="text" class="form-control" name="workstation${number}_machine_name" required>
                    </div>
                    <div class="col-md-6 mb-3">
                        <label class="form-label">Functions</label>
                        <div>
                            <div class="form-check form-check-inline">
                                <input class="form-check-input" type="checkbox" name="workstation${number}_functions" value="audio_editing">
                                <label class="form-check-label">Audio Editing</label>
                            </div>
                            <div class="form-check form-check-inline">
                                <input class="form-check-input" type="checkbox" name="workstation${number}_functions" value="video_editing">
                                <label class="form-check-label">Video Editing</label>
                            </div>
                            <div class="form-check form-check-inline">
                                <input class="form-check-input" type="checkbox" name="workstation${number}_functions" value="graphics">
                                <label class="form-check-label">Graphics</label>
                            </div>
                        </div>
                    </div>
                </div>
                <div class="row">
                    <div class="col-md-6 mb-3">
                        <label class="form-label">Device Model</label>
                        <input type="text" class="form-control" name="workstation${number}_device_model" required>
                    </div>
                    <div class="col-md-6 mb-3">
                        <label class="form-label">Operating System</label>
                        <input type="text" class="form-control" name="workstation${number}_operating_system" required>
                    </div>
                </div>
                <!-- Add more workstation fields as needed -->
            </div>
        </div>
    `;
}

function initializeSoftwareSections() {
    // Handle software checkbox changes
    var softwareCheckboxes = document.querySelectorAll('.software-checkbox');
    softwareCheckboxes.forEach(function(checkbox) {
        checkbox.addEventListener('change', function() {
            var softwareRow = this.closest('.software-row');
            var inputs = softwareRow.querySelectorAll('input:not([type="checkbox"]), select');
            
            inputs.forEach(function(input) {
                input.disabled = !checkbox.checked;
                if (!checkbox.checked) {
                    input.value = '';
                }
            });
        });
    });
    
    // Handle free version checkboxes
    var freeCheckboxes = document.querySelectorAll('.free-version-checkbox');
    freeCheckboxes.forEach(function(checkbox) {
        checkbox.addEventListener('change', function() {
            var fileInput = this.closest('.software-row').querySelector('input[type="file"]');
            if (fileInput) {
                fileInput.disabled = this.checked;
                if (this.checked) {
                    fileInput.value = '';
                }
            }
        });
    });
}

// Data Tables
function initializeDataTables() {
    var tables = document.querySelectorAll('.data-table');
    tables.forEach(function(table) {
        // Add sorting functionality
        var headers = table.querySelectorAll('th[data-sort]');
        headers.forEach(function(header) {
            header.style.cursor = 'pointer';
            header.addEventListener('click', function() {
                sortTable(table, this.cellIndex, this.dataset.sort);
            });
        });
    });
}

function sortTable(table, columnIndex, sortType) {
    var tbody = table.querySelector('tbody');
    var rows = Array.from(tbody.querySelectorAll('tr'));
    var isAscending = table.dataset.sortOrder !== 'asc';
    
    rows.sort(function(a, b) {
        var aValue = a.cells[columnIndex].textContent.trim();
        var bValue = b.cells[columnIndex].textContent.trim();
        
        if (sortType === 'number') {
            aValue = parseFloat(aValue) || 0;
            bValue = parseFloat(bValue) || 0;
        } else if (sortType === 'date') {
            aValue = new Date(aValue);
            bValue = new Date(bValue);
        }
        
        if (aValue < bValue) return isAscending ? -1 : 1;
        if (aValue > bValue) return isAscending ? 1 : -1;
        return 0;
    });
    
    rows.forEach(function(row) {
        tbody.appendChild(row);
    });
    
    table.dataset.sortOrder = isAscending ? 'asc' : 'desc';
    
    // Update sort indicators
    table.querySelectorAll('th').forEach(function(th) {
        th.classList.remove('sort-asc', 'sort-desc');
    });
    table.querySelectorAll('th')[columnIndex].classList.add(isAscending ? 'sort-asc' : 'sort-desc');
}

// AJAX Functions
function initializeAjaxForms() {
    var ajaxForms = document.querySelectorAll('.ajax-form');
    ajaxForms.forEach(function(form) {
        form.addEventListener('submit', handleAjaxForm);
    });
}

function handleAjaxForm(e) {
    e.preventDefault();
    var form = e.target;
    var formData = new FormData(form);
    var url = form.action || window.location.href;
    var method = form.method || 'POST';
    
    // Show loading state
    var submitBtn = form.querySelector('button[type="submit"]');
    var originalText = submitBtn.textContent;
    submitBtn.disabled = true;
    submitBtn.innerHTML = '<span class="spinner-border spinner-border-sm me-2"></span>Processing...';
    
    fetch(url, {
        method: method,
        body: formData,
        headers: {
            'X-Requested-With': 'XMLHttpRequest'
        }
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            showAlert(data.message || 'Operation completed successfully', 'success');
            if (data.redirect) {
                setTimeout(() => window.location.href = data.redirect, 1500);
            }
        } else {
            showAlert(data.message || 'An error occurred', 'danger');
        }
    })
    .catch(error => {
        console.error('Error:', error);
        showAlert('An error occurred while processing your request', 'danger');
    })
    .finally(() => {
        // Restore button state
        submitBtn.disabled = false;
        submitBtn.textContent = originalText;
    });
}

// Real-time Validation
function initializeRealTimeValidation() {
    // Username availability check
    var usernameInput = document.getElementById('username');
    if (usernameInput) {
        var usernameTimeout;
        usernameInput.addEventListener('input', function() {
            clearTimeout(usernameTimeout);
            usernameTimeout = setTimeout(() => checkUsernameAvailability(this.value), 500);
        });
    }
    
    // Email availability check
    var emailInput = document.getElementById('email');
    if (emailInput) {
        var emailTimeout;
        emailInput.addEventListener('input', function() {
            clearTimeout(emailTimeout);
            emailTimeout = setTimeout(() => checkEmailAvailability(this.value), 500);
        });
    }
    
    // Password strength indicator
    var passwordInput = document.getElementById('password');
    if (passwordInput) {
        passwordInput.addEventListener('input', function() {
            updatePasswordStrength(this.value);
        });
    }
}

function checkUsernameAvailability(username) {
    if (username.length < 3) return;
    
    fetch('/auth/api/check-username', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({username: username})
    })
    .then(response => response.json())
    .then(data => {
        var input = document.getElementById('username');
        var feedback = input.parentNode.querySelector('.username-feedback') || 
                      createFeedbackElement(input, 'username-feedback');
        
        if (data.available) {
            input.classList.remove('is-invalid');
            input.classList.add('is-valid');
            feedback.className = 'username-feedback valid-feedback';
            feedback.textContent = 'Username is available';
        } else {
            input.classList.remove('is-valid');
            input.classList.add('is-invalid');
            feedback.className = 'username-feedback invalid-feedback';
            feedback.textContent = data.message;
        }
    });
}

function checkEmailAvailability(email) {
    if (!isValidEmail(email)) return;
    
    fetch('/auth/api/check-email', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({email: email})
    })
    .then(response => response.json())
    .then(data => {
        var input = document.getElementById('email');
        var feedback = input.parentNode.querySelector('.email-feedback') || 
                      createFeedbackElement(input, 'email-feedback');
        
        if (data.available) {
            input.classList.remove('is-invalid');
            input.classList.add('is-valid');
            feedback.className = 'email-feedback valid-feedback';
            feedback.textContent = 'Email is available';
        } else {
            input.classList.remove('is-valid');
            input.classList.add('is-invalid');
            feedback.className = 'email-feedback invalid-feedback';
            feedback.textContent = data.message;
        }
    });
}

function updatePasswordStrength(password) {
    var strengthBar = document.querySelector('.password-strength') || 
                     createPasswordStrengthIndicator();
    
    var strength = calculatePasswordStrength(password);
    var strengthText = ['Very Weak', 'Weak', 'Fair', 'Good', 'Strong'];
    var strengthColors = ['danger', 'warning', 'info', 'primary', 'success'];
    
    strengthBar.className = `progress-bar bg-${strengthColors[strength]}`;
    strengthBar.style.width = `${(strength + 1) * 20}%`;
    strengthBar.textContent = strengthText[strength];
}

function calculatePasswordStrength(password) {
    var score = 0;
    if (password.length >= 8) score++;
    if (/[a-z]/.test(password)) score++;
    if (/[A-Z]/.test(password)) score++;
    if (/[0-9]/.test(password)) score++;
    if (/[^A-Za-z0-9]/.test(password)) score++;
    return Math.min(score - 1, 4);
}

function createFeedbackElement(input, className) {
    var feedback = document.createElement('div');
    feedback.className = className;
    input.parentNode.appendChild(feedback);
    return feedback;
}

function createPasswordStrengthIndicator() {
    var passwordInput = document.getElementById('password');
    var container = document.createElement('div');
    container.className = 'progress mt-2';
    container.style.height = '4px';
    
    var bar = document.createElement('div');
    bar.className = 'progress-bar password-strength';
    bar.style.width = '0%';
    
    container.appendChild(bar);
    passwordInput.parentNode.appendChild(container);
    
    return bar;
}

// Utility Functions
function showAlert(message, type = 'info') {
    var alertDiv = document.createElement('div');
    alertDiv.className = `alert alert-${type} alert-dismissible fade show`;
    alertDiv.innerHTML = `
        <i class="bi bi-${getAlertIcon(type)} me-2"></i>
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;
    
    var container = document.querySelector('.container');
    if (container) {
        container.insertBefore(alertDiv, container.firstChild);
    }
    
    // Auto-dismiss after 5 seconds
    setTimeout(() => {
        var alert = new bootstrap.Alert(alertDiv);
        alert.close();
    }, 5000);
}

function getAlertIcon(type) {
    var icons = {
        'success': 'check-circle',
        'danger': 'exclamation-triangle',
        'warning': 'exclamation-circle',
        'info': 'info-circle'
    };
    return icons[type] || 'info-circle';
}

function isValidEmail(email) {
    var re = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return re.test(email);
}

function showLoading() {
    var overlay = document.createElement('div');
    overlay.className = 'spinner-overlay';
    overlay.innerHTML = `
        <div class="spinner-border spinner-border-lg text-light" role="status">
            <span class="visually-hidden">Loading...</span>
        </div>
    `;
    document.body.appendChild(overlay);
}

function hideLoading() {
    var overlay = document.querySelector('.spinner-overlay');
    if (overlay) {
        overlay.remove();
    }
}

function confirmAction(message, callback) {
    if (confirm(message)) {
        callback();
    }
}

// Form Auto-save (for external forms)
function initializeAutoSave() {
    var form = document.querySelector('.auto-save-form');
    if (!form) return;
    
    var inputs = form.querySelectorAll('input, select, textarea');
    var saveTimeout;
    
    inputs.forEach(function(input) {
        input.addEventListener('change', function() {
            clearTimeout(saveTimeout);
            saveTimeout = setTimeout(autoSaveForm, 2000);
        });
    });
}

function autoSaveForm() {
    var form = document.querySelector('.auto-save-form');
    if (!form) return;
    
    var formData = new FormData(form);
    
    fetch(form.action + '?auto_save=1', {
        method: 'POST',
        body: formData
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            showAutoSaveIndicator();
        }
    })
    .catch(error => {
        console.log('Auto-save failed:', error);
    });
}

function showAutoSaveIndicator() {
    var indicator = document.querySelector('.auto-save-indicator');
    if (!indicator) {
        indicator = document.createElement('div');
        indicator.className = 'auto-save-indicator position-fixed bottom-0 end-0 p-3';
        indicator.innerHTML = '<small class="text-muted"><i class="bi bi-check-circle me-1"></i>Auto-saved</small>';
        document.body.appendChild(indicator);
    }
    
    indicator.style.display = 'block';
    setTimeout(() => {
        indicator.style.display = 'none';
    }, 2000);
}

// QR Code Display (for 2FA setup)
function displayQRCode(qrCodeData) {
    var modal = new bootstrap.Modal(document.getElementById('qrCodeModal'));
    var qrCodeContainer = document.getElementById('qrCodeContainer');
    qrCodeContainer.innerHTML = `<img src="data:image/png;base64,${qrCodeData}" class="img-fluid">`;
    modal.show();
}

// Copy to Clipboard
function copyToClipboard(text, element) {
    navigator.clipboard.writeText(text).then(function() {
        var originalText = element.textContent;
        element.textContent = 'Copied!';
        element.classList.add('btn-success');
        
        setTimeout(function() {
            element.textContent = originalText;
            element.classList.remove('btn-success');
        }, 2000);
    });
}

// Chart initialization (if charts are present)
function initializeCharts() {
    // This would integrate with Chart.js or similar library
    // for dashboard statistics display
}

// Export functions for global access
window.PostAccreditation = {
    showAlert,
    showLoading,
    hideLoading,
    confirmAction,
    copyToClipboard,
    displayQRCode
};
