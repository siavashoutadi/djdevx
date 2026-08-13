document.addEventListener('click', function(event) {
  var alertClose = event.target.closest('.twui-alert-close');
  if (alertClose) {
    var alertEl = alertClose.closest('.twui-alert');
    if (alertEl) {
      alertEl.style.display = 'none';
    }
    return;
  }

  var toastClose = event.target.closest('.twui-toast-close');
  if (toastClose) {
    var toastEl = toastClose.closest('.twui-toast');
    if (toastEl) {
      toastEl.classList.add('hiding');
      setTimeout(function() {
        toastEl.remove();
      }, 300);
    }
    return;
  }

  var themeButton = event.target.closest('[data-set-theme]');
  if (themeButton) {
    if (typeof setTheme === 'function') {
      setTheme(themeButton.getAttribute('data-set-theme'));
    }
  }
});
