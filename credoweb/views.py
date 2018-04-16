# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.shortcuts import render, get_object_or_404

from django.db.models import Count

from credoapi.models import Team, User, Detection

import base64


def index(request):
    recent_detections = Detection.objects.all().order_by('-timestamp')[:20]
    top_users = User.objects.annotate(detection_count=Count('detection')).order_by('-detection_count')[:5]
    context = {
        'detections_total': Detection.objects.count(),
        'users_total': User.objects.count(),
        'teams_total': Team.objects.count(),
        'recent_detections': [{
            'date': d.timestamp,
            'user': {
                'name': d.user.username,
                'display_name': d.user.display_name,
            },
            'team': {
                'name': d.user.team.name,
            },
            'img': base64.encodestring(d.frame_content)
        } for d in recent_detections],
        'top_users': [{
            'name': u.username,
            'display_name': u.display_name,
            'detection_count': u.detection_count
        } for u in top_users]
    }
    return render(request, 'credoweb/index.html', context)


def user_page(request, username=''):
    u = get_object_or_404(User, username=username)
    user_recent_detections = Detection.objects.filter(user=u).order_by('-timestamp')[:20]
    user_detection_count = Detection.objects.filter(user=u).count()
    context = {
        'user': {
            'name': u.username,
            'display_name': u.display_name,
            'team': {
                'name': u.team.name,
            },
            'detection_count': user_detection_count
        },
        'user_recent_detections': [{
            'date': d.timestamp,
            'img': base64.encodestring(d.frame_content)
        } for d in user_recent_detections]

    }
    return render(request, 'credoweb/user.html', context)


def team_page(request, name=''):
    t = get_object_or_404(Team, name=name)
    team_users = User.objects.filter(team=t).annotate(detection_count=Count('detection'))
    team_user_count = team_users.count()
    context = {
        'team': {
            'name': t.name,
            'user_count': team_user_count
        },
        'team_users': [{
            'name': u.username,
            'display_name': u.display_name,
            'detection_count': u.detection_count
        } for u in team_users]

    }
    return render(request, 'credoweb/team.html', context)