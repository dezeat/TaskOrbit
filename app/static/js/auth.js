/**
 * ui.js
 * Handles client-side interactions like Modals and Form validation UX.
 */
(function () {
  
  /**
   * Simple client-side check to ensure passwords match before submitting.
   * This provides instant feedback without waiting for the server.
   */
  function handleRegisterSubmit(e) {
    const form = e.target;
    const pwd = form.querySelector('#reg-password');
    const pwdConfirm = form.querySelector('#reg-password-confirm');

    if (pwd && pwdConfirm && pwd.value !== pwdConfirm.value) {
      alert('Passwords do not match'); // Consider replacing with a nice error div later
      e.preventDefault();
      return false;
    }
    return true;
  }

  // --- Modal Logic ---

  function toggleRegisterModal(show) {
    const modal = document.getElementById('register-modal');
    if (modal) {
      show ? modal.classList.remove('hidden') : modal.classList.add('hidden');
    }
  }

  // Initialize listeners when DOM is ready
  document.addEventListener('DOMContentLoaded', function () {
    // 1. Password Match Validation
    const registerForm = document.getElementById('register-form');
    if (registerForm) {
      registerForm.addEventListener('submit', handleRegisterSubmit);
    }

    // 2. Modal Controls
    const openBtn = document.getElementById('open-register');
    const closeBtn = document.getElementById('close-register');
    const cancelBtn = document.getElementById('reg-cancel');

    if (openBtn) openBtn.addEventListener('click', (e) => {
      e.preventDefault();
      toggleRegisterModal(true);
    });

    if (closeBtn) closeBtn.addEventListener('click', () => toggleRegisterModal(false));
    if (cancelBtn) cancelBtn.addEventListener('click', () => toggleRegisterModal(false));
  });

  // Expose for external calls if needed (e.g. from HTMX events)
  window.toggleRegisterModal = toggleRegisterModal;
})();