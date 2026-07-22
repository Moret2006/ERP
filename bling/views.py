import secrets

from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render

from .api import BlingConfigError, build_authorize_url, exchange_code_for_token
from .models import BlingToken


@login_required(login_url='login')
def bling_status_view(request):
    context = {
        'token': BlingToken.objects.first(),
        'configurado': bool(
            settings.BLING_CLIENT_ID and settings.BLING_CLIENT_SECRET and settings.BLING_REDIRECT_URI
        ),
    }
    return render(request, 'bling/status.html', context)


@login_required(login_url='login')
def bling_connect_view(request):
    state = secrets.token_urlsafe(24)
    request.session['bling_oauth_state'] = state

    try:
        url = build_authorize_url(state)
    except BlingConfigError:
        messages.error(
            request,
            'BLING_CLIENT_ID/BLING_CLIENT_SECRET/BLING_REDIRECT_URI ainda não '
            'configurados. Defina essas variáveis de ambiente e tente novamente.',
        )
        return redirect('bling:status')

    return redirect(url)


@login_required(login_url='login')
def bling_callback_view(request):
    expected_state = request.session.pop('bling_oauth_state', None)
    state = request.GET.get('state')
    code = request.GET.get('code')

    if not code or not state or state != expected_state:
        messages.error(request, 'Falha na autorização com a Bling (state inválido ou código ausente).')
        return redirect('bling:status')

    try:
        exchange_code_for_token(code)
    except BlingConfigError:
        messages.error(request, 'BLING_CLIENT_ID/BLING_CLIENT_SECRET não configurados.')
        return redirect('bling:status')
    except Exception:
        messages.error(request, 'Não foi possível concluir a conexão com a Bling. Tente novamente.')
        return redirect('bling:status')

    messages.success(request, 'Conectado à Bling com sucesso.')
    return redirect('bling:status')
