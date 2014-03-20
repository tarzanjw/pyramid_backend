__author__ = 'tarzan'

import re
from .resources import AdminSite
from .backend_manager import create_backend_manager

_registered_models = [

]

def get_model_url(request, model, action=None):
    if model not in _registered_models:
        raise NotImplementedError('%s model has not been implemented' % model.__name__)
    traverse = [model.__backend_manager__.slug,]
    if action:
        traverse.append(action)
    return request.route_url('admin_site',
                             traverse=traverse)

def get_registered_models():
    return _registered_models

def register_model(model):
    global _registered_models
    if model in _registered_models:
        return
    model.__backend_manager__ = create_backend_manager(model)
    _registered_models.append(model)
    AdminSite.model_mappings[model.__backend_manager__.slug] = model