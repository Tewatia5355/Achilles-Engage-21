from .authenticate import *
from .profile import *
from .clas import *
from .asgn import *
from .subb import *
from .notification import *
from django.template.defaulttags import register


@register.filter
def get_range(value):
    return range(1, value + 1)
