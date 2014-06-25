'''
Created on Jun 19, 2014

@author: anroco
'''

EMAIL_REGEX = '^[(a-z0-9\_\-\.)]+@[(a-z0-9\_\-\.)]+\.[(a-z)]{2,4}$'
LATLONG_REGEX = '^(\-?([\d+]{1,2})(\.\d+)?),\s*(\-?([\d+]{1,3})(\.\d+)?)$'
FORMAT_SKILLS_REGEX = '^([a-zA-Z0-9]|[.][a-zA-Z0-9]+|^$)[\s\w#+-.]*$'
EMAIL_MESSAGE = 'Invalid email format.'
LATLONG_MESSAGE = 'Invalid geolocation Lat,Long format.'
LENGTH_MESSAGE = 'The max length is {0} characters.'
FORMAT_SKILLS_MESSAGE = 'The value must be alphanumeric characters or #_+.-'


class ItemsRepeated(object):

    def __init__(self, message=None):
        if not message:
            message = 'This value is repeated.'
        self.message = message

    def __call__(self, form, field):
        items_repeated = False
        for item in field.entries:
            item.process_data(item.data.lower())
            if item.data and field.data.count(item.data) > 1:
                item.errors.append(self.message)
                items_repeated = True
        if items_repeated:
            from wtforms import ValidationError
            raise ValidationError()


class LengthListItems(object):

    def __init__(self, min_items=0, message=None):
        self.min_items = min_items
        if not message and self.min_items > 0:
            plural = lambda x: 's' if x > 1 else ''
            message = u'Must be at least {0} value{1}.'.format(min_items,
                                                             plural(min_items))
        self.message = message

    def __call__(self, form, field):
        from wtforms import ValidationError
        if len(field.data) < self.min_items:
            raise ValidationError(self.message)
