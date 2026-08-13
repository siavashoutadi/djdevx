document.addEventListener('DOMContentLoaded', function() {
  // Auto-dismiss toasts after 5 seconds
  const toasts = document.querySelectorAll('.toast');
  toasts.forEach(function(toast) {
    setTimeout(function() {
      toast.classList.add('hiding');
      setTimeout(function() {
        toast.remove();
      }, 300);
    }, 5000);
  });

  // Manual dismissal via close button (event delegation)
  document.addEventListener('click', function(event) {
    const closeButton = event.target.closest('.toast-close');
    if (!closeButton) {
      return;
    }
    const toast = closeButton.closest('.toast');
    if (toast) {
      toast.remove();
    }
  });
});
