from django import template

register = template.Library()

@register.filter
def status_count(queryset, status):
    """Count objects with specific status"""
    return queryset.filter(status=status).count()

@register.filter
def status_filter(queryset, status):
    """Filter objects by status"""
    return queryset.filter(status=status)