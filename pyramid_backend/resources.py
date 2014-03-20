__author__ = 'tarzan'

import urllib
from . import model as model_helper
from . import ADMIN_SITE_PATH

def model_url(request, model, action=None, query=None):
    """
    Get url for an model with its action
    :type request: pyramid.request.Request
    :type model: object
    :type action: string
    :type query: string or dict
    """
    model = model_helper.get_registered_model(model)

    url = ADMIN_SITE_PATH + model.__backend_manager__.slug
    if action:
        url += '/' + action
    if query and isinstance(query, dict):
        query = urllib.urlencode(query)
    if query:
        url += '?' + query
    return request.relative_url(url, True)

def object_url(obj, id_value=None):
    if isinstance(obj, type):
        model = obj
        assert id_value is not None
    else:
        model = obj.__class__
        id_value = obj.id
    murl = model_url(model)
    return '%s%s/' % (murl, id_value)

class ModelResource(object):
    model = None

    def __init__(self, parent, name):
        self.__parent__ = parent
        self.__name__ = name

class ObjectResource(object):
    url = '#'

    def __init__(self, parent, name):
        self.__parent__ = parent
        self.__name__ = name
        self.object = object

    def __resource_url__(self, *args, **kwargs):
        return object_url(self.__model__, self.__name__)

    def __str__(self):
        return self.__model__.__name__ + '#' + self.__name__

_AUTO_CLASSES = {}

def model_resource_class(model):
    cls_name = model.__name__ + '_ModelResource'
    if cls_name not in _AUTO_CLASSES:
        _AUTO_CLASSES[cls_name] = type(cls_name, (ModelResource,), {
            'model': model,
        })

    try:
        _AUTO_CLASSES[cls_name].__acl__ = model.__backend_manager__.__acl__
    except AttributeError:
        pass

    return _AUTO_CLASSES[cls_name]

def object_resource_class(model):
    cls_name = model.__name__ + '_ObjectResource'
    if cls_name not in _AUTO_CLASSES:
        _AUTO_CLASSES[cls_name] = type(cls_name, (ObjectResource,), {
            'model': model,
        })

    return _AUTO_CLASSES[cls_name]


from pyramid.security import Allow, Everyone, ALL_PERMISSIONS

class AdminSite(object):
    __acl__ = [
        (Allow, Everyone, ALL_PERMISSIONS),
    ]
    model_mappings = {

    }

    def __init__(self, request):
        """
        :type request: pyramid.request.Request
        """
        self.request = request

    def __getitem__(self, item):
        try:
            model = AdminSite.model_mappings[item]
        except KeyError:
            for model in model_helper.get_registered_models():
                if model.__backend_manager__.slug == item:
                    AdminSite.model_mappings[item] = model
                    break
        return model.__backend_manager__.ModelResource(self, item)