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
        view_cls = model_view.model_view_class(model)
    default_actions = model.__backend_manager__.default_actions
    if actions is None:
        actions = model.__backend_manager__.default_actions
    elif isinstance(actions, (list, tuple,)):
        actions = {k:v for k,v in default_actions.items() if k in actions}
    elif isinstance(actions, dict):
        actions = {k:(v if k not in actions else v if v else actions[k]) for k,v in actions}
    view_cls.configure_actions(actions)
    for a_conf in actions.values():
        config.add_view(view=view_cls, **a_conf)