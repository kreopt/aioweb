import datetime
from aiohttp_jinja2 import render_string


class FieldInstance(object):
    def __init__(self, request, field_class, name, val=''):
        self.request = request
        self.fieldClass = field_class
        self.value = val
        self.name = name

    def __str__(self):
        try:
            try:
                del self.fieldClass.attributes['value']
                del self.fieldClass.attributes['name']
            except (KeyError, AttributeError):
                pass
            ctx = {}
            if hasattr(self.fieldClass, 'make_context'):
                ctx.update(self.fieldClass.make_context())
            ctx.update({
                'attributes': self.fieldClass.attributes,
                'value': self.value,
                'name': self.name
            })
            return render_string('admin/widgets/%s.html' % self.fieldClass.type, self.request, ctx)
        except Exception as e:
            return ''


class FormField(object):
    def __init__(self, **kwargs):
        self.attributes = kwargs

    @classmethod
    def validate(cls, value):
        return True


class StringField(FormField):
    type = 'string'

    @classmethod
    def validate(cls, value):
        return isinstance(value, type('')) or value is None


class PasswordField(FormField):
    type = 'password'

    @classmethod
    def validate(cls, value):
        return isinstance(value, type('')) or value is None


class ChoiceField(FormField):
    type = 'choice'

    def __init__(self, item_generator, **kwargs):
        self.item_generator = item_generator
        super().__init__(**kwargs)

    def make_context(self):
        return {
            'items': self.item_generator()
        }


class TextField(FormField):
    type = 'text'

    @classmethod
    def validate(cls, value):
        return isinstance(value, type('')) or value is None


class NumberField(FormField):
    type = 'number'

    @classmethod
    def validate(cls, value):
        try:
            float(value)
            return True
        except ValueError:
            return False


class DateField(FormField):
    type = 'date'

    @classmethod
    def validate(cls, value):
        try:
            datetime.datetime.strptime(value, "%Y-%m-%d")
            return True
        except ValueError:
            return False


class BooleanField(FormField):
    type = 'bool'
