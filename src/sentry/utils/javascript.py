"""
sentry.utils.javascript
~~~~~~~~~~~~~~~~~~~~~~~

:copyright: (c) 2010-2012 by the Sentry Team, see AUTHORS for more details.
:license: BSD, see LICENSE for more details.
"""
from django.core.urlresolvers import reverse
from django.utils.html import escape
from sentry.constants import STATUS_RESOLVED
from sentry.models import Group
from sentry.templatetags.sentry_plugins import get_tags
from sentry.utils import json


def transform(obj, request=None):
    if isinstance(obj, (list, tuple)):
        return [transform(o, request=request) for o in obj]
    elif isinstance(obj, dict):
        return dict((k, transform(v, request=request)) for k, v in obj.iteritems())

    t = transformers.get(type(obj))
    if t:
        return t(obj, request=request)
    return obj


def transform_group(obj, request=None):
    d = {
        'id': str(obj.id),
        'count': str(obj.times_seen),
        'title': escape(obj.message_top()),
        'message': escape(obj.error()),
        'level': obj.level,
        'levelName': escape(obj.get_level_display()),
        'logger': escape(obj.logger),
        'permalink': reverse('sentry-group', args=[obj.project.slug, obj.id]),
        'versions': list(obj.get_version() or []),
        'lastSeen': obj.last_seen.isoformat(),
        'timeSpent': obj.avg_time_spent,
        'canResolve': request and request.user.is_authenticated(),
        'isResolved': obj.status == STATUS_RESOLVED,
    }
    if request:
        d['tags'] = list(get_tags(obj, request))
    return d


transformers = {
    Group: transform_group,
}


def to_json(obj, request=None):
    result = transform(obj, request=request)
    return json.dumps(result)