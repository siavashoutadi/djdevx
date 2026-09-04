document.addEventListener('click', function(event) {
  var button = event.target.closest('[name="action_remove"]');
  if (!button) {
    return;
  }
  var message = button.getAttribute('data-confirm-message');
  if (message && !window.confirm(message)) {
    event.preventDefault();
  }
});
