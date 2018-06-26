# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import base64
import time

from django.core.cache import cache
from django.core.paginator import Paginator
from django.db.models import Count

from django_redis import get_redis_connection

from credocommon.models import Team, User, Detection


def format_date(timestamp):
    return time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(timestamp / 1000)) + ".{:03}".format(timestamp % 1000)


def get_global_stats():
    return cache.get_or_set('global_stats', lambda: {
        'detections_total': Detection.objects.filter(visible=True).count(),
        'users_total': User.objects.count(),
        'teams_total': Team.objects.count(),
    })


def get_recent_detections():
    return [{
            'date': format_date(d.timestamp),
            'timestamp': d.timestamp,
            'user': {
                'name': d.user.username,
                'display_name': d.user.display_name,
            },
            'team': {
                'name': d.team.name,
            },
            'img': base64.encodestring(d.frame_content)
            } for d in Detection.objects.order_by('-timestamp').filter(visible=True).select_related('user', 'team')[:20]]


def get_top_users():
    return [{
            'name': u.username,
            'display_name': u.display_name,
            'detection_count': u.detection_count
            } for u in User.objects.filter(detection__visible=True).annotate(detection_count=Count('detection')).order_by('-detection_count')[:5]]


def get_recent_users():
    return [{
            'name': u.username,
            'display_name': u.display_name,
            'detection_count': u.detection_count
            } for u in User.objects.filter(detection__visible=True).annotate(detection_count=Count('detection')).order_by('-id')[:5]]


def get_user_detections_page(user, page):
    data = cache.get('user_{}_recent_detections_{}'.format(user.id, page))
    if not data:
        p = Paginator(Detection.objects.filter(user=user).order_by('-timestamp').filter(visible=True), 20).page(page)
        data = {
            'has_next': p.has_next(),
            'has_previous': p.has_previous(),
            'page_number': page,
            'detections': [{
                'date': format_date(d.timestamp),
                'timestamp': d.timestamp,
                'img': base64.encodestring(d.frame_content)
            } for d in p.object_list]
        }
        cache.set('user_{}_recent_detections_{}'.format(user.id, page), data)
    return data


def get_user_on_time_and_rank(user):
    on_time = get_redis_connection(write=False).zscore(cache.make_key('on_time'), user.id)
    if not on_time:
        return None, None

    rank = get_redis_connection(write=False).zrevrank(cache.make_key('on_time'), user.id)

    hours, remainder = divmod(int(on_time) / 1000, 3600)
    minutes, seconds = divmod(remainder, 60)
    return '{}h {}m'.format(hours, minutes), rank + 1
