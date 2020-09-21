# encoding: utf-8

from channels.auth import AuthMiddlewareStack
from channels.routing import ProtocolTypeRouter, URLRouter
from cool.views.websocket import CoolBFFAPIConsumer
from django.urls import path

application = ProtocolTypeRouter({
    'websocket': AuthMiddlewareStack(
        URLRouter(
            [path('wsapi', CoolBFFAPIConsumer)],
        )
    ),
})
