from allauth.mfa.utils import is_mfa_enabled
from django.shortcuts import redirect
from django.urls import reverse


class MFARequiredMiddleware:
    """
    Middleware that checks if the user has completed MFA setup.
    If not, redirects them to the MFA setup page.
    """

    def __init__(self, get_response):
        self.get_response = get_response
        self.exempt_urls = [
            reverse("mfa_index"),
            reverse("mfa_activate_totp"),
            reverse("account_logout"),
        ]

    def __call__(self, request):
        if request.user.is_authenticated:
            path = request.path_info
            is_exempt = any(path == url for url in self.exempt_urls)
            if not is_exempt and not is_mfa_enabled(request.user):
                return redirect("mfa_index")

        response = self.get_response(request)
        return response
