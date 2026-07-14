from django.contrib import messages
from django.contrib.auth import authenticate, get_user_model, login, logout
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render
from django.utils.http import url_has_allowed_host_and_scheme
from django.views.decorators.http import require_http_methods

User = get_user_model()


def _authenticate_by_login(request, login_value, password):
    user = authenticate(request, username=login_value, password=password)
    if user is not None:
        return user

    try:
        user_by_email = User.objects.get(email__iexact=login_value)
    except User.DoesNotExist:
        return None

    return authenticate(request, username=user_by_email.username, password=password)


def _safe_next_url(request, next_url):
    if next_url and url_has_allowed_host_and_scheme(
        next_url,
        allowed_hosts={request.get_host()},
        require_https=request.is_secure(),
    ):
        return next_url
    return None


def index_view(request):
    if request.user.is_authenticated:
        return redirect('dash')
    return redirect('login')


@require_http_methods(['GET', 'POST'])
def login_view(request):
    if request.user.is_authenticated:
        return redirect('dash')

    next_url = _safe_next_url(request, request.GET.get('next', ''))

    if request.method == 'POST':
        login_value = request.POST.get('email', '').strip()
        password = request.POST.get('password', '')
        remember = request.POST.get('remember')
        next_url = _safe_next_url(request, request.POST.get('next', ''))

        user = _authenticate_by_login(request, login_value, password)

        if user is not None:
            login(request, user)
            if not remember:
                request.session.set_expiry(0)
            return redirect(next_url or 'dash')

        messages.error(request, 'E-mail ou senha incorretos. Tente novamente.')

    return render(request, 'login/login.html', {'next': next_url})


@login_required
def home_view(request):
    return render(request, 'login/home.html')


@require_http_methods(['GET', 'POST'])
def logout_view(request):
    logout(request)
    return redirect('login')
