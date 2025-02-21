from django.shortcuts import redirect
from django.urls import reverse
from django.utils.deprecation import MiddlewareMixin

class LoginRequiredMiddleware(MiddlewareMixin):
    def process_request(self, request):
        exempt_paths = [
            reverse('admin:login'),
            reverse('admin:logout'),
            # reverse('admin:password_reset'),
            # reverse('admin:password_reset_done'),
            # reverse('admin:password_reset_confirm'),
            # reverse('admin:password_reset_complete')
        ]
        if not request.user.is_authenticated and all([not request.path.startswith(ep) for ep in exempt_paths]):
            return redirect(reverse('admin:login'))

