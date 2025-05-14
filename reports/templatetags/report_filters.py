# reports/templatetags/report_filters.py
from django import template
from django.template.defaultfilters import floatformat

register = template.Library()

@register.filter
def get_item(dictionary, key):
    """从字典中获取项目"""
    return dictionary.get(key)

@register.filter
def percentage(value, total):
    """计算百分比"""
    try:
        return floatformat(float(value) / float(total) * 100, 1)
    except (ValueError, ZeroDivisionError):
        return 0