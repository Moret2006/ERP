from django.contrib import admin

from .models import BlingToken


@admin.register(BlingToken)
class BlingTokenAdmin(admin.ModelAdmin):
    list_display = ['id', 'expires_at', 'expirado', 'atualizado_em']
    readonly_fields = ['access_token', 'refresh_token', 'expires_at', 'atualizado_em']
