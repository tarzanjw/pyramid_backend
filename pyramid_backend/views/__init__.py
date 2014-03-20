__author__ = 'tarzan'

from pyramid.view import view_config
import pyramid_backend as pb
from pyramid_backend import resources as _rsr
from pyramid_backend import model as model_helper
from . import model_view

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

def add_model_view(config, model, view_cls=None, actions=None):
    """
    :type config: pyramid.config.Configurator
    """
    model_helper.register_model(model)

    if view_cls is None:
        view_cls = model_view.ModelView
    mgr = model.__backend_manager__
    """:type : pyramid_backend.backend_manager.Manager"""
    mgr.configure_actions(actions)
    for a_conf in mgr.actions.values():
        config.add_view(view=view_cls, **{k:v for k,v in a_conf.items() if not k.startswith('_')})