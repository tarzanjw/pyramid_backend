__author__ = 'tarzan'

from pyramid.view import view_config
from datetime import datetime
import inspect
from pyramid_backend import resources as _rsr
from pyramid_backend import model as model_helper

@view_config(route_name='admin_site', context=_rsr.AdminSite,
             renderer='pyramid_backend:templates/index.mak')
def admin_site_home_view(context, request):
    """
    :type context: pyramid_backend.resources.AdminSite
    :type request: pyramid.request.Request
    """
    models = model_helper.get_registered_models()
    return {
        'models': [dict(
            name=m.__name__,
            url=model_helper.get_model_url(request, m)
        ) for m in models]
    }

def cell_datatype(val):
    if val is None:
        return 'none'
    if isinstance(val, bool):
        return 'bool'
    if isinstance(val, (int, long, float)):
        return 'number'
    if isinstance(val, datetime):
        return 'datetime'
    if isinstance(val, basestring):
        return 'longtext' if len(val) > 40 else 'text'
    if inspect.isclass(type(val)):
        return 'class'
    return 'generic'

from . import model_view
from .model_view import ModelView

def add_model_view(config, model, view_cls=None, actions=None):
    """
    :type config: pyramid.config.Configurator
    """
    model_helper.register_model(model)

    if view_cls is None:
        view_cls = ModelView
    mgr = model.__backend_manager__
    """:type : pyramid_backend.backend_manager.Manager"""
    mgr.configure_actions(actions)
    for a_conf in mgr.actions.values():
        config.add_view(view=view_cls, **{k:v for k,v in a_conf.items() if not k.startswith('_')})

import venusian
class model_view_config(object):
    def __init__(self, model, actions=None):
        assert model, "You have to specify model"
        self.model = model
        self.actions = actions

    def view_config(self, scanner, name, wrapped):
        add_model_view(scanner.config,
                         self.model,
                         wrapped)

    def __call__(self, wrapped):
        self.info = venusian.attach(wrapped, self.view_config)
        return wrapped