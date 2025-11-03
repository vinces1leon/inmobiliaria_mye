from django import template

register = template.Library()

@register.filter
def get_item(dictionary, key):
    """Obtiene un item de un diccionario usando una clave"""
    if dictionary is None:
        return []
    return dictionary.get(key, [])