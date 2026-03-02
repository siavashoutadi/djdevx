from django import template

from . import twui_alert, twui_badge, twui_toast

register = template.Library()

for lib in (twui_alert.register, twui_badge.register, twui_toast.register):
    for name, tag in lib.tags.items():
        register.tag(name, tag)
    for name, filt in lib.filters.items():
        register.filter(name, filt)
