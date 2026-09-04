
      // Toast notification system
      function getToastIcon(type) {
        const icons = {
          success: '<svg class="toast-icon" fill="currentColor" viewBox="0 0 20 20"><path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clip-rule="evenodd"></path></svg>',
          error: '<svg class="toast-icon" fill="currentColor" viewBox="0 0 20 20"><path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clip-rule="evenodd"></path></svg>',
          warning: '<svg class="toast-icon" fill="currentColor" viewBox="0 0 20 20"><path fill-rule="evenodd" d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z" clip-rule="evenodd"></path></svg>',
          info: '<svg class="toast-icon" fill="currentColor" viewBox="0 0 20 20"><path fill-rule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a1 1 0 000 2v3a1 1 0 001 1h1a1 1 0 100-2v-3a1 1 0 00-1-1H9z" clip-rule="evenodd"></path></svg>'
        };
        return icons[type] || icons.info;
      }

      function createToast(message, type = 'info', duration = 5000) {
        // Create toast container if it doesn't exist
        let container = document.querySelector('.toast-container');
        if (!container) {
          container = document.createElement('div');
          container.className = 'toast-container';
          document.body.appendChild(container);
        }

        // Create toast element
        const toast = document.createElement('div');
        toast.className = `toast ${type}`;
        toast.innerHTML = `
          ${getToastIcon(type)}
          <div class="toast-content">${message}</div>
          <button class="toast-close" aria-label="Close">&times;</button>
        `;

        // Add toast to container
        container.appendChild(toast);

        // Show toast with animation
        setTimeout(() => {
          toast.classList.add('show');
        }, 10);

        // Auto remove after duration
        const autoRemove = setTimeout(() => {
          removeToast(toast);
        }, duration);

        // Manual close button
        const closeButton = toast.querySelector('.toast-close');
        closeButton.addEventListener('click', () => {
          clearTimeout(autoRemove);
          removeToast(toast);
        });

        return toast;
      }

      function removeToast(toast) {
        toast.classList.add('hide');
        setTimeout(() => {
          if (toast.parentNode) {
            toast.parentNode.removeChild(toast);
          }
        }, 300);
      }

      // Show existing Django messages as toasts
      document.addEventListener('DOMContentLoaded', function() {
        const messages = document.querySelectorAll('.django-messages .message');
        messages.forEach(messageElement => {
          const message = messageElement.textContent.trim();
          const type = messageElement.className.replace('message ', '');
          createToast(message, type, 7000); // Longer duration for Django messages
        });
      });
