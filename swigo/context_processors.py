from django.conf import settings

def debug_context(request):
    """
    Rend la variable DEBUG disponible dans tous les templates.
    Exemple : {% if not debug %} ... {% endif %}
    """
    return {'debug': settings.DEBUG}
