__author__ = 'tarzan'
import re
import inspect
from pyramid.decorator import reify
import resources

def create_backend_manager(model):
    """
    create backend manager for a model
    :rtype Manager
    """
    return Manager(model)

def get_manager(model):
    """
    get backend manager for a model
    :rtype Manager
    """
    try:
        return model.__backend_manager__
    except AttributeError:
        manager = create_backend_manager(model)
        model.__backend_manager__ = manager
        return manager

class Manager(object):
    def __init__(self, model):
        """
        :type model: object
        """
        assert inspect.isclass(model)
        self.model = model
        self.actions = {}

    @reify
    def default_actions(self):
        return {
        'list': {
            'route_name': 'admin_site',
            'context': self.ModelResource,
            'attr': 'action_list',
            'renderer': 'pyramid_backend:templates/list.mak',
            'permission': 'list',
        },
        'create': {
            'route_name': 'admin_site',
            'context': self.ModelResource,
            'name': 'create',
            'attr': 'action_create',
            'renderer': 'pyramid_backend:templates/create.mak',
            'permission': 'create',
        },
        'detail': {
            'route_name': 'admin_site',
            'context': self.ObjectResource,
            'attr': 'action_detail',
            'renderer': 'pyramid_backend:templates/detail.mak',
            'permission': 'detail',
        },
        'update': {
            'route_name': 'admin_site',
            'context': self.ObjectResource,
            'name': 'update',
            'attr': 'action_update',
            'renderer': 'pyramid_backend:templates/update.mak',
            'permission': 'update',
        },
        'delete': {
            'route_name': 'admin_site',
            'context': self.ObjectResource,
            'name': 'delete',
            'attr': 'action_delete',
            'renderer': 'pyramid_backend:templates/update.mak',
            'permission': 'delete',
        },
    }

    @reify
    def slug(self):
        """get slug for current model"""
        if hasattr(self.model, '__backend_slug__'):
            return self.model.__backend_slug__
        cls_name = self.model.__name__
        # implement camel case to underscore
        s1 = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', cls_name)
        return re.sub('([a-z0-9])([A-Z])', r'\1_\2', s1).lower()

    @reify
    def ModelResource(self):
        return resources.model_resource_class(self.model)

    @reify
    def ObjectResource(self):
        return resources.object_resource_class(self.model)

    def configure_actions(self, actions):
        if actions is None:
            actions = self.default_actions
        elif isinstance(actions, (list, tuple,)):
            actions = {k:v for k,v in self.default_actions.items() if k in actions}
        elif isinstance(actions, dict):
            actions = {k:(v if k not in actions else v if v else actions[k]) for k,v in actions}
        self.actions = actions