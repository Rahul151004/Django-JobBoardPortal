// Job Board Portal - Main JavaScript

document.addEventListener("DOMContentLoaded", function () {
  // Set validation error endpoint
  window.validationErrorEndpoint = "/api/validation-error/";

  // Initialize tooltips
  var tooltipTriggerList = [].slice.call(
    document.querySelectorAll('[data-bs-toggle="tooltip"]')
  );
  tooltipTriggerList.map(function (tooltipTriggerEl) {
    return new bootstrap.Tooltip(tooltipTriggerEl);
  });

  // Auto-hide alerts after 5 seconds
  const alerts = document.querySelectorAll(".alert:not(.alert-permanent)");
  alerts.forEach(function (alert) {
    setTimeout(function () {
      const bsAlert = new bootstrap.Alert(alert);
      bsAlert.close();
    }, 5000);
  });

  // Simple form enhancements (non-blocking)
  initializeBasicFormEnhancements();

  // File upload validation
  initializeFileUploadValidation();

  // Real-time field validation
  initializeRealTimeValidation();

  // Confirm delete actions
  const deleteButtons = document.querySelectorAll("[data-confirm-delete]");
  deleteButtons.forEach(function (button) {
    button.addEventListener("click", function (event) {
      const message =
        button.getAttribute("data-confirm-delete") ||
        "Are you sure you want to delete this item?";
      if (!confirm(message)) {
        event.preventDefault();
      }
    });
  });

  // Search form enhancements
  const searchForms = document.querySelectorAll(".search-form form");
  searchForms.forEach(function (form) {
    const inputs = form.querySelectorAll(
      'input[type="text"], input[type="search"]'
    );
    inputs.forEach(function (input) {
      input.addEventListener("keypress", function (event) {
        if (event.key === "Enter") {
          form.submit();
        }
      });
    });
  });

  // Smooth scroll for anchor links
  const anchorLinks = document.querySelectorAll('a[href^="#"]');
  anchorLinks.forEach(function (link) {
    link.addEventListener("click", function (event) {
      const targetId = link.getAttribute("href").substring(1);
      const targetElement = document.getElementById(targetId);

      if (targetElement) {
        event.preventDefault();
        targetElement.scrollIntoView({
          behavior: "smooth",
          block: "start",
        });
      }
    });
  });

  // Loading state for forms - TEMPORARILY DISABLED FOR DEBUGGING
  // initializeSubmitButtonStates();

  // Job card hover effects
  const jobCards = document.querySelectorAll(".job-card");
  jobCards.forEach(function (card) {
    card.addEventListener("mouseenter", function () {
      card.style.transform = "translateY(-2px)";
    });

    card.addEventListener("mouseleave", function () {
      card.style.transform = "translateY(0)";
    });
  });

  // Deadline warning animation
  const deadlineWarnings = document.querySelectorAll(".deadline-warning");
  deadlineWarnings.forEach(function (warning) {
    setInterval(function () {
      warning.style.opacity = warning.style.opacity === "0.7" ? "1" : "0.7";
    }, 1000);
  });
});

// Basic Form Enhancement Functions (Non-blocking)
function initializeBasicFormEnhancements() {
  // Simple submit button state management without validation blocking
  const submitButtons = document.querySelectorAll('button[type="submit"]');
  submitButtons.forEach(function (button) {
    button.setAttribute("data-original-text", button.innerHTML);

    button.addEventListener("click", function () {
      // Only change button state, don't prevent submission
      setTimeout(function () {
        button.disabled = true;
        button.innerHTML =
          '<i class="fas fa-spinner fa-spin me-2"></i>Processing...';

        // Re-enable after 8 seconds as fallback
        setTimeout(function () {
          button.disabled = false;
          button.innerHTML =
            button.getAttribute("data-original-text") || "Submit";
        }, 8000);
      }, 100); // Small delay to allow form submission to proceed
    });
  });
}

// Enhanced Form Validation Functions (DISABLED)
function initializeFormValidation() {
  const forms = document.querySelectorAll("form");
  forms.forEach(function (form) {
    // Skip validation for registration forms - let Django handle everything
    if (form.action.includes("register")) {
      console.log("Skipping validation for registration form");
      return;
    }

    // Add novalidate to prevent browser default validation
    form.setAttribute("novalidate", "novalidate");

    form.addEventListener("submit", function (event) {
      console.log(
        "Form submission attempt:",
        form.action || form.getAttribute("action")
      );

      // Only validate CSRF token for POST forms, let Django handle other validation
      if (form.method.toLowerCase() === "post" && !validateCSRFToken(form)) {
        console.log("Form blocked by CSRF validation");
        event.preventDefault();
        event.stopPropagation();
        return;
      }

      console.log("Form submission allowed");
      // Let Django handle form validation instead of blocking with JavaScript
      form.classList.add("was-validated");
    });

    // Add form reset functionality
    const resetButton = form.querySelector('button[type="reset"]');
    if (resetButton) {
      resetButton.addEventListener("click", function () {
        form.classList.remove("was-validated");
        form
          .querySelectorAll(".is-invalid, .is-valid")
          .forEach(function (field) {
            field.classList.remove("is-invalid", "is-valid");
          });
      });
    }
  });
}

function validateForm(form) {
  let isValid = true;
  const fields = form.querySelectorAll("input, textarea, select");

  fields.forEach(function (field) {
    if (!validateField(field)) {
      isValid = false;
    }
  });

  return isValid;
}

function validateField(field) {
  let isValid = true;
  const value = field.value.trim();
  const fieldType = field.type;
  const fieldName = field.name;

  // Clear previous custom validation
  field.setCustomValidity("");

  // Security validation for text inputs
  if (
    value &&
    (fieldType === "text" ||
      fieldType === "textarea" ||
      fieldName === "description" ||
      fieldName === "requirements")
  ) {
    const securityError = validateSecureInput(value, fieldName);
    if (securityError) {
      field.setCustomValidity(securityError);
      reportValidationError(field, securityError);
      isValid = false;
    }
  }

  // Required field validation
  if (field.hasAttribute("required") && !value) {
    field.setCustomValidity("This field is required.");
    isValid = false;
  }

  // Email validation
  if (fieldType === "email" && value) {
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    if (!emailRegex.test(value)) {
      field.setCustomValidity("Please enter a valid email address.");
      isValid = false;
    }

    // Additional email security check
    if (value.length > 254) {
      field.setCustomValidity("Email address is too long.");
      isValid = false;
    }
  }

  // Phone validation
  if (fieldName === "phone" && value) {
    const phoneRegex = /^[+]?[0-9\s\-\(\)]{10,15}$/;
    if (!phoneRegex.test(value)) {
      field.setCustomValidity(
        "Please enter a valid phone number (10-15 digits)."
      );
      isValid = false;
    }
  }

  // Password validation
  if (fieldName === "password1" && value) {
    if (value.length < 8) {
      field.setCustomValidity("Password must be at least 8 characters long.");
      isValid = false;
    }

    // Enhanced password strength validation
    const hasUpperCase = /[A-Z]/.test(value);
    const hasLowerCase = /[a-z]/.test(value);
    const hasNumbers = /\d/.test(value);
    const hasSpecialChar = /[!@#$%^&*(),.?":{}|<>]/.test(value);

    if (!hasUpperCase || !hasLowerCase || !hasNumbers) {
      field.setCustomValidity(
        "Password must contain uppercase, lowercase, and numeric characters."
      );
      isValid = false;
    }
  }

  // Password confirmation validation
  if (fieldName === "password2" && value) {
    const password1 = document.querySelector('input[name="password1"]');
    if (password1 && value !== password1.value) {
      field.setCustomValidity("Passwords do not match.");
      isValid = false;
    }
  }

  // Name validation (letters, spaces, apostrophes, and hyphens)
  if ((fieldName === "first_name" || fieldName === "last_name") && value) {
    const nameRegex = /^[a-zA-Z\s\'\-]{2,30}$/;
    if (!nameRegex.test(value)) {
      field.setCustomValidity(
        "Name must be 2-30 characters, letters, spaces, apostrophes, and hyphens only."
      );
      isValid = false;
    }
  }

  // Username validation
  if (fieldName === "username" && value) {
    const usernameRegex = /^[a-zA-Z0-9_@.+-]{3,150}$/;
    if (!usernameRegex.test(value)) {
      field.setCustomValidity(
        "Username must be 3-150 characters, letters, numbers, and @/./+/-/_ only."
      );
      isValid = false;
    }
  }

  // Salary validation
  if (fieldName === "salary" && value) {
    const salary = parseFloat(value);
    if (isNaN(salary) || salary <= 0 || salary > 9999999.99) {
      field.setCustomValidity("Salary must be between $1 and $9,999,999.99.");
      isValid = false;
    }
  }

  // Date validation (deadline must be in future)
  if (fieldName === "deadline" && value) {
    const selectedDate = new Date(value);
    const today = new Date();
    today.setHours(0, 0, 0, 0);

    if (isNaN(selectedDate.getTime())) {
      field.setCustomValidity("Please enter a valid date.");
      isValid = false;
    } else if (selectedDate <= today) {
      field.setCustomValidity("Deadline must be in the future.");
      isValid = false;
    } else {
      // Check if date is not too far in future (2 years)
      const maxDate = new Date();
      maxDate.setFullYear(maxDate.getFullYear() + 2);
      if (selectedDate > maxDate) {
        field.setCustomValidity(
          "Deadline cannot be more than 2 years in the future."
        );
        isValid = false;
      }
    }
  }

  // URL validation for website fields
  if (fieldName === "website" && value) {
    try {
      const url = new URL(value);
      if (!["http:", "https:"].includes(url.protocol)) {
        field.setCustomValidity("Website must use HTTP or HTTPS protocol.");
        isValid = false;
      }
    } catch (e) {
      field.setCustomValidity("Please enter a valid website URL.");
      isValid = false;
    }
  }

  // Text length validation
  if (value && field.hasAttribute("maxlength")) {
    const maxLength = parseInt(field.getAttribute("maxlength"));
    if (value.length > maxLength) {
      field.setCustomValidity(`Maximum ${maxLength} characters allowed.`);
      isValid = false;
    }
  }

  if (value && field.hasAttribute("minlength")) {
    const minLength = parseInt(field.getAttribute("minlength"));
    if (value.length < minLength) {
      field.setCustomValidity(`Minimum ${minLength} characters required.`);
      isValid = false;
    }
  }

  return isValid;
}

function initializeRealTimeValidation() {
  const fields = document.querySelectorAll("input, textarea, select");

  fields.forEach(function (field) {
    // Validate on blur
    field.addEventListener("blur", function () {
      validateField(field);
      updateFieldValidationUI(field);
    });

    // Clear validation on input for better UX
    field.addEventListener("input", function () {
      if (field.classList.contains("is-invalid")) {
        field.setCustomValidity("");
        updateFieldValidationUI(field);
      }
    });

    // Special handling for password confirmation
    if (field.name === "password1") {
      field.addEventListener("input", function () {
        const password2 = document.querySelector('input[name="password2"]');
        if (password2 && password2.value) {
          validateField(password2);
          updateFieldValidationUI(password2);
        }
      });
    }
  });
}

function updateFieldValidationUI(field) {
  const isValid = field.checkValidity();
  const feedbackElement = field.parentNode.querySelector(".invalid-feedback");

  if (isValid) {
    field.classList.remove("is-invalid");
    field.classList.add("is-valid");
    if (feedbackElement) {
      feedbackElement.style.display = "none";
    }
  } else {
    field.classList.remove("is-valid");
    field.classList.add("is-invalid");

    // Create or update feedback element
    if (!feedbackElement) {
      const feedback = document.createElement("div");
      feedback.className = "invalid-feedback";
      field.parentNode.appendChild(feedback);
    }

    const feedback = field.parentNode.querySelector(".invalid-feedback");
    feedback.textContent = field.validationMessage;
    feedback.style.display = "block";
  }
}

function initializeFileUploadValidation() {
  const fileInputs = document.querySelectorAll('input[type="file"]');
  fileInputs.forEach(function (input) {
    input.addEventListener("change", function (event) {
      const file = event.target.files[0];
      validateFileUpload(input, file);
    });
  });
}

function validateFileUpload(input, file) {
  const maxSize = 5 * 1024 * 1024; // 5MB
  let isValid = true;

  // Clear previous validation
  input.setCustomValidity("");

  if (file) {
    const fileName = file.name;
    const fileSize = file.size;
    const fileExtension = fileName.split(".").pop().toLowerCase();

    // File size validation
    if (fileSize > maxSize) {
      input.setCustomValidity(
        `File size must be less than ${formatFileSize(maxSize)}.`
      );
      isValid = false;
    }

    // File type validation
    if (input.name === "resume" && fileExtension !== "pdf") {
      input.setCustomValidity("Resume must be a PDF file.");
      isValid = false;
    }

    if (
      (input.name === "logo" || input.name === "profile_picture") &&
      !["jpg", "jpeg", "png", "gif", "bmp"].includes(fileExtension)
    ) {
      input.setCustomValidity("Image must be JPG, PNG, GIF, or BMP format.");
      isValid = false;
    }

    // Filename validation
    if (!/^[a-zA-Z0-9._\-\s]+$/.test(fileName)) {
      input.setCustomValidity("Filename contains invalid characters.");
      isValid = false;
    }

    // Update file info display
    updateFileInfo(input, file, isValid);
  }

  updateFieldValidationUI(input);
  return isValid;
}

function updateFileInfo(input, file, isValid) {
  const fileName = file.name;
  const fileSize = formatFileSize(file.size);

  // Create or update file info display
  let fileInfo = input.parentNode.querySelector(".file-info");
  if (!fileInfo) {
    fileInfo = document.createElement("div");
    fileInfo.className = "file-info mt-2 small";
    input.parentNode.appendChild(fileInfo);
  }

  const iconClass = isValid
    ? "fas fa-file text-success"
    : "fas fa-exclamation-triangle text-danger";
  const textClass = isValid ? "text-muted" : "text-danger";

  fileInfo.className = `file-info mt-2 small ${textClass}`;
  fileInfo.innerHTML = `
        <i class="${iconClass} me-1"></i>
        ${fileName} (${fileSize})
    `;
}

function initializeSubmitButtonStates() {
  const submitButtons = document.querySelectorAll('button[type="submit"]');
  submitButtons.forEach(function (button) {
    // Store original text
    button.setAttribute("data-original-text", button.innerHTML);

    button.addEventListener("click", function (event) {
      console.log("Submit button clicked:", button);
      const form = button.closest("form");
      if (form) {
        console.log("Form found:", form);

        // Skip validation for registration forms
        if (form.action.includes("register")) {
          console.log(
            "Registration form - allowing submission without validation"
          );
          button.disabled = true;
          button.innerHTML =
            '<i class="fas fa-spinner fa-spin me-2"></i>Processing...';

          // Re-enable after 5 seconds as fallback
          setTimeout(function () {
            button.disabled = false;
            button.innerHTML =
              button.getAttribute("data-original-text") || "Submit";
            console.log("Button re-enabled after timeout");
          }, 5000);
          return; // Don't prevent default for registration forms
        }

        // For other forms, check CSRF token
        if (validateCSRFToken(form)) {
          console.log("CSRF validation passed, setting button state");
          button.disabled = true;
          button.innerHTML =
            '<i class="fas fa-spinner fa-spin me-2"></i>Processing...';

          // Re-enable after 5 seconds as fallback
          setTimeout(function () {
            button.disabled = false;
            button.innerHTML =
              button.getAttribute("data-original-text") || "Submit";
            console.log("Button re-enabled after timeout");
          }, 5000);
        } else {
          console.log("CSRF validation failed");
          event.preventDefault();
        }
      } else {
        console.log("No form found for button");
      }
    });
  });
}

// Utility functions
function showAlert(message, type = "info") {
  const alertContainer = document.querySelector(".container");
  if (alertContainer) {
    const alert = document.createElement("div");
    alert.className = `alert alert-${type} alert-dismissible fade show`;
    alert.innerHTML = `
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
        `;
    alertContainer.insertBefore(alert, alertContainer.firstChild);

    // Auto-hide after 5 seconds
    setTimeout(function () {
      const bsAlert = new bootstrap.Alert(alert);
      bsAlert.close();
    }, 5000);
  }
}

function formatFileSize(bytes) {
  if (bytes === 0) return "0 Bytes";
  const k = 1024;
  const sizes = ["Bytes", "KB", "MB", "GB"];
  const i = Math.floor(Math.log(bytes) / Math.log(k));
  return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + " " + sizes[i];
}

function validateCSRFToken(form) {
  // Only check CSRF token for POST forms
  const method = form.method.toLowerCase();
  if (method !== "post") {
    return true; // GET forms don't need CSRF tokens
  }

  const csrfToken = form.querySelector('input[name="csrfmiddlewaretoken"]');
  if (!csrfToken || !csrfToken.value) {
    console.warn("CSRF token missing in POST form:", form);
    showAlert(
      "Security token missing. Please refresh the page and try again.",
      "warning"
    );
    return false;
  }
  return true;
}

// Enhanced security validation
function validateSecureInput(value, fieldName) {
  // XSS prevention
  const xssPatterns = [
    /<script\b[^<]*(?:(?!<\/script>)<[^<]*)*<\/script>/gi,
    /javascript:/gi,
    /on\w+\s*=/gi,
    /<iframe/gi,
    /<object/gi,
    /<embed/gi,
  ];

  for (let pattern of xssPatterns) {
    if (pattern.test(value)) {
      return `${fieldName} contains potentially dangerous content.`;
    }
  }

  // SQL injection prevention (basic)
  const sqlPatterns = [
    /(\b(SELECT|INSERT|UPDATE|DELETE|DROP|CREATE|ALTER|EXEC|UNION)\b)/gi,
    /(--|\/\*|\*\/|;)/g,
  ];

  for (let pattern of sqlPatterns) {
    if (pattern.test(value)) {
      return `${fieldName} contains invalid characters.`;
    }
  }

  return null;
}

// Form submission rate limiting
const formSubmissionTracker = new Map();

function checkSubmissionRate(form) {
  const formId = form.id || form.action || "default";
  const now = Date.now();
  const lastSubmission = formSubmissionTracker.get(formId);

  if (lastSubmission && now - lastSubmission < 2000) {
    // 2 second cooldown
    showAlert("Please wait before submitting again.", "warning");
    return false;
  }

  formSubmissionTracker.set(formId, now);
  return true;
}

// Enhanced error reporting
function reportValidationError(field, error) {
  // Log validation errors for debugging
  console.log(`Validation error in ${field.name}: ${error}`);

  // Send error to server for monitoring (if endpoint exists)
  if (window.validationErrorEndpoint) {
    fetch(window.validationErrorEndpoint, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "X-CSRFToken": document.querySelector("[name=csrfmiddlewaretoken]")
          ?.value,
      },
      body: JSON.stringify({
        field: field.name,
        error: error,
        url: window.location.href,
        timestamp: new Date().toISOString(),
      }),
    }).catch((err) => console.log("Error reporting failed:", err));
  }
}
