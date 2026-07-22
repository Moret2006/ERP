def _display_name(user):
    if user.get_full_name():
        return user.get_full_name()
    if user.first_name:
        return user.first_name
    return user.username.capitalize()


def _user_role(user):
    if user.is_superuser or user.is_staff:
        return 'Administração'
    return 'Operação'


def topbar_user(request):
    if not request.user.is_authenticated:
        return {}
    return {
        'display_name': _display_name(request.user),
        'user_role': _user_role(request.user),
    }
