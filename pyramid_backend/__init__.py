__author__ = 'tarzan'

import re
import importlib
ADMIN_SITE_PATH = None

def includeme(config):
    """
    :type config: pyramid.config.Configurator
    """
    global ADMIN_SITE_PATH
    settings = config.get_settings()
    ADMIN_SITE_PATH = settings['pyramid_backend.admin_site']
    ADMIN_SITE_PATH = ADMIN_SITE_PATH.strip('/') + '/'

    from . import resources as _rsr
    from . import model as model_helper
    from . import views

    route_pattern = ADMIN_SITE_PATH + '*traverse'
    config.add_route('admin_site', route_pattern, factory=_rsr.AdminSite)
    config.add_directive('add_model_view', views.add_model_view)

    model_paths = settings.get('pyramid_backend.models', '')
    model_paths = filter(bool, re.split('\s+', model_paths))
    for path in model_paths:
        _module, _var = path.rsplit('.', 1)
        _module = importlib.import_module(_module, package=None)
        model = getattr(_module, _var)
        # model_helper.register_model(model)
        config.add_model_view(model)

    config.scan(__name__)