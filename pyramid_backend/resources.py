__author__ = 'tarzan'

class ModelResource(object):
    def __init__(self, parent, name):
        self.__parent__ = parent
        self.__name__ = name

class ObjectResource(object):
    def __init__(self, parent, name):
        self.__parent__ = parent
        self.__name__ = name

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
        model = AdminSite.model_mappings[item]
        return model.__backend_manager__.ModelResource(self, item)