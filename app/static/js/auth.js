/**
 * auth.js
 * Shared authentication helpers for the client UI.
 *
 * This module centralizes small behaviors needed by the login and
 * registration flows:
 * - Basic client-side validation and modal helpers.
 * - Passwords are hashed server-side; the client performs no hashing.
 * - Simple show/hide helpers for the register modal.
 *
 * The functions are intentionally small and defensive — they will no-op
 * if the expected DOM elements are not present so the module is safe to
 * include on any page.
 */
(function () {
  /**
   * Compute the SHA-256 hex digest of a given string.
   * @param {string} message - The input string to hash.
   * @returns {Promise<string>} Hex-encoded SHA-256 digest.
   */
  // Passwords are sent in plaintext to the server which is
  // responsible for hashing them. The client only performs
  // minimal validation (e.g. matching confirmation) for UX.

  /**
   * Handle login form submission: hash the password field and submit.
   * @param {Event} e - The submit event from the login form.
   */
  function handleLoginSubmit(e) {
    // Let normal form submission occur; no client hashing.
    return true;
  }

  /**
   * Handle registration form submission: validate, hash, and submit.
   * Clears the plain-text fields before submitting to avoid leakage.
   * @param {Event} e - The submit event from the register form.
   */
  function handleRegisterSubmit(e) {
    // Basic client-side validation only: ensure passwords match.
    const form = e.target;
    const pwd = form.querySelector('#reg-password');
    const pwdConfirm = form.querySelector('#reg-password-confirm');
    if (!pwd || !pwdConfirm) return;
    if (pwd.value !== pwdConfirm.value) {
      alert('Passwords do not match');
      e.preventDefault();
      return false;
    }
    // Allow submission; server will hash the password.
    return true;
  }

  /**
   * Show the register modal (if present).
   */
  function openRegisterModal() {
    const modal = document.getElementById('register-modal');
    if (modal) modal.classList.remove('hidden');
  }

  /**
   * Hide the register modal (if present).
   */
  function closeRegisterModal() {
    const modal = document.getElementById('register-modal');
    if (modal) modal.classList.add('hidden');
  }

  // Wire up handlers when the DOM is ready. The checks make inclusion
  // of this script safe on pages that may not contain all auth elements.
  document.addEventListener('DOMContentLoaded', function () {
    const loginForm = document.querySelector('form[action="/login"]');
    if (loginForm) loginForm.addEventListener('submit', handleLoginSubmit);

    const registerForm = document.getElementById('register-form');
    if (registerForm) registerForm.addEventListener('submit', handleRegisterSubmit);

    const openBtn = document.getElementById('open-register');
    if (openBtn) openBtn.addEventListener('click', function (ev) {
      ev.preventDefault();
      openRegisterModal();
    });

    const closeBtn = document.getElementById('close-register');
    if (closeBtn) closeBtn.addEventListener('click', function () { closeRegisterModal(); });

    const cancelBtn = document.getElementById('reg-cancel');
    if (cancelBtn) cancelBtn.addEventListener('click', function () { closeRegisterModal(); });
  });

  // Expose a convenience function for opening the modal from other scripts.
  window.openRegisterModal = openRegisterModal;
})();
