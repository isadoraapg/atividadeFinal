from django import template

register = template.Library()

@register.simple_tag
def notificacoes_nao_lidas(user):
    return user.notificacoes.filter(lida=False).count() 