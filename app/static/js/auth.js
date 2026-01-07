/**
 * ui.js
 * Handles client-side interactions like Modals and Form validation UX.
 */
(function () {
  
  /**
   * Validate password fields before HTMX sends the request
   */
  function validatePasswords(form) {
    const pwd = form.querySelector('#reg-password');
    const pwdConfirm = form.querySelector('#reg-password-confirm');
    const clientError = form.querySelector('#password-match-error');

    // First clear all errors
    clearAllErrors(form);

    if (pwd && pwdConfirm && pwd.value !== pwdConfirm.value) {
      // Clear password fields and show error
      clearPasswordFields(form);
      if (clientError) {
        clientError.classList.remove('hidden');
      }
      return false;
    }
    
    return true;
  }

  /**
   * Clear all error messages
   */
  function clearAllErrors(form) {
    const errorContainer = form.querySelector('#error-container');
    if (errorContainer) {
      // Hide client-side error
      const clientError = errorContainer.querySelector('#password-match-error');
      if (clientError) {
        clientError.classList.add('hidden');
      }
      // Remove server-side error
      const serverError = errorContainer.querySelector('.server-error');
      if (serverError) {
        serverError.remove();
      }
    }
  }

  /**
   * Clear password fields but keep username
   */
  function clearPasswordFields(form) {
    const pwd = form.querySelector('#reg-password');
    const pwdConfirm = form.querySelector('#reg-password-confirm');
    if (pwd) pwd.value = '';
    if (pwdConfirm) pwdConfirm.value = '';
  }

  /**
   * Clear inline password match error when user types
   */
  function handlePasswordInput() {
    const form = document.getElementById('register-form');
    if (form) {
      clearAllErrors(form);
    }
  }

  // --- Modal Logic ---

  function toggleRegisterModal(show) {
    const modal = document.getElementById('register-modal');
    if (modal) {
      if (show) {
        modal.classList.remove('hidden');
        // Clear form when opening
        const form = modal.querySelector('#register-form');
        if (form) {
          form.reset();
          // Hide all errors
          clearAllErrors(form);
        }
      } else {
        modal.classList.add('hidden');
      }
    }
  }

  function attachEventListeners() {
    const registerForm = document.getElementById('register-form');
    
    if (registerForm) {
      // Clear password fields if server error exists (password too short or other error)
      const modal = document.getElementById('register-modal');
      const serverError = modal ? modal.querySelector('.server-error') : null;
      if (serverError) {
        clearPasswordFields(registerForm);
      }

      // Validate before HTMX sends the request
      registerForm.addEventListener('htmx:configRequest', function(evt) {
        if (!validatePasswords(registerForm)) {
          evt.preventDefault();
        }
      });

      // Clear error when user types in password fields
      const pwd = registerForm.querySelector('#reg-password');
      const pwdConfirm = registerForm.querySelector('#reg-password-confirm');
      if (pwd) pwd.addEventListener('input', handlePasswordInput);
      if (pwdConfirm) pwdConfirm.addEventListener('input', handlePasswordInput);
    }

    // Modal Controls
    const openBtn = document.getElementById('open-register');
    const closeBtn = document.getElementById('close-register');
    const cancelBtn = document.getElementById('reg-cancel');

    if (openBtn) {
      openBtn.removeEventListener('click', handleOpenRegister);
      openBtn.addEventListener('click', handleOpenRegister);
    }

    if (closeBtn) closeBtn.addEventListener('click', () => toggleRegisterModal(false));
    if (cancelBtn) cancelBtn.addEventListener('click', () => toggleRegisterModal(false));
  }

  function handleOpenRegister(e) {
    e.preventDefault();
    toggleRegisterModal(true);
  }

  // Initialize listeners when DOM is ready
  document.addEventListener('DOMContentLoaded', attachEventListeners);

  // Re-attach listeners after HTMX swaps the modal
  document.body.addEventListener('htmx:afterSwap', function(evt) {
    if (evt.detail.target.id === 'register-modal') {
      attachEventListeners();
    }
  });

  // Expose for external calls if needed (e.g. from HTMX events)
  window.toggleRegisterModal = toggleRegisterModal;
})();