from django import template
from django.template.defaultfilters import stringfilter

register = template.Library()

@register.filter
@stringfilter
def uri_cleaned_url_zika_onto(value): 

    return value.split('*')[1]
