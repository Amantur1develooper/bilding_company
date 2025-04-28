# from django import template

# register = template.Library()

# @register.filter
# def sum_attr(queryset, attr):
#     return sum(getattr(item, attr) for item in queryset)

from django import template

register = template.Library()

@register.filter(name='sum_attr')
def sum_attr(queryset, attr_name):
    """Суммирует значения атрибута для всех элементов QuerySet"""
    return sum(getattr(item, attr_name, 0) for item in queryset)