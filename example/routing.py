# encoding: utf-8

from channels.auth import AuthMiddlewareStack
from channels.routing import ProtocolTypeRouter, URLRouter
from django.urls import path

from cool.views.websocket import CoolBFFAPIConsumer

application = ProtocolTypeRouter({
    'websocket': AuthMiddlewareStack(
        URLRouter(
            [path('wsapi', CoolBFFAPIConsumer)],
        )
    ),
})
