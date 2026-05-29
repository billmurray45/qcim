from django import template
from django.conf import settings
from django.utils.translation import get_language
from urllib.parse import urlsplit, urlunsplit

register = template.Library()


def get_localized_value(obj, field_name, language_code=None):
    if obj is None:
        return ''

    language = (language_code or get_language() or 'ru').split('-')[0]
    value = None

    if language in {'kk', 'en'}:
        value = getattr(obj, f'{field_name}_{language}', None)

    if value in (None, ''):
        value = getattr(obj, field_name, '')

    return value or ''


@register.filter(name='localized')
def localized(obj, field_name):
    return get_localized_value(obj, field_name)


@register.simple_tag(takes_context=True)
def change_language_url(context, language_code):
    request = context.get('request')
    if not request:
        return '/'

    split_url = urlsplit(request.get_full_path())
    path = split_url.path or '/'
    languages = {code for code, _name in settings.LANGUAGES}
    default_language = settings.LANGUAGE_CODE.split('-')[0]

    parts = [part for part in path.split('/') if part]
    if parts and parts[0] in languages:
        parts = parts[1:]

    localized_path = '/' + '/'.join(parts)
    if not localized_path.endswith('/') and path.endswith('/'):
        localized_path += '/'

    if language_code != default_language:
        localized_path = f'/{language_code}' + (localized_path if localized_path != '/' else '/')

    return urlunsplit(('', '', localized_path, split_url.query, split_url.fragment))
