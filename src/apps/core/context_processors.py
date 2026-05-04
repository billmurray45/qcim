"""
Context processors for core app.
Makes common data available to all templates.
"""
from apps.contacts.models import Office


def main_office(request):
    """
    Add main office to context for all templates.
    Used in footer and throughout the site.
    """
    office = Office.objects.filter(is_main=True, is_active=True).first()
    return {
        'main_office': office
    }
