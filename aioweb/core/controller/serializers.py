import re

from aiohttp import web
from aiohttp_jinja2 import APP_KEY

from aioweb.modules import template


class BaseSerializer(object):
    CONTENT_TYPE = "*"

    def __init__(self, controller):
        self.controller = controller

    @staticmethod
    def can_handle(cls, contentType):
        return re.match(cls.CONTENT_TYPE, contentType)

    def serialize(self, data):
        raise web.HTTPNotAcceptable(body='') # TODO pass all acceptable content-types


class JsonSerializer(BaseSerializer):
    CONTENT_TYPE = "application/json"

    def serialize(self, data):
        return web.json_response(data)


class TemplateSerializer(BaseSerializer):
    CONTENT_TYPE = "text/html"

    def serialize(self, data):
        try:
            self.controller.request.app[APP_KEY].globals['controller'] = self.controller
            return template.render(self.controller._private.template, self.controller.request, data)
        except web.HTTPInternalServerError as e:
            if self.controller.request.is_ajax():
                raise web.HTTPNotImplemented()
            else:
                raise e


SERIALIZERS = [
    TemplateSerializer, JsonSerializer, BaseSerializer
]


def make_serializer(controller, acceptEntries):
    for serializer in SERIALIZERS:
        for entry in acceptEntries:
            if serializer.can_handle(serializer, entry):
                return serializer(controller)
    return BaseSerializer(controller)
