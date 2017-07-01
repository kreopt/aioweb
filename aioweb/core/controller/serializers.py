import re

from aiohttp import web
from aiohttp_jinja2 import APP_KEY

from aioweb.modules import template


class BaseSerializer(object):
    CONTENT_TYPES = ["*"]

    def __init__(self, controller):
        self.controller = controller

    @classmethod
    def can_handle(cls, contentType):
        for type in cls.CONTENT_TYPES:
            if re.match(type, contentType):
                return True
        return False

    def serialize(self, data):
        raise web.HTTPNotAcceptable(body='') # TODO respond with all acceptable content-types


class JsonSerializer(BaseSerializer):
    CONTENT_TYPES = ["application/json"]

    def serialize(self, data):
        return web.json_response(data)


class TemplateSerializer(BaseSerializer):
    CONTENT_TYPES = ["text/html", "text/*"]

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
            if serializer.can_handle(entry):
                return serializer(controller)
    return BaseSerializer(controller)
