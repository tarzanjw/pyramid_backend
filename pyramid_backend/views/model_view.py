__author__ = 'tarzan'

from .. import resources as _rsr
from pyramid.view import view_config

class ModelView(object):

    def __init__(self, context, request):
        """
        :type context: pyramid_backend.resources.ModelResource
        :type request: pyramid.request.Request
        """
        self.context = context
        self.request = request

    @property
    def model(self):
        return self.context.model

    @property
    def is_current_context_object(self):
        """
        :rtype : bool
        """
        return isinstance(self.context, _rsr.ObjectResource)

    @property
    def backend_mgr(self):
        """
        :rtype : pyramid_backend.backend_manager.Manager
        """
        return self.model.__backend_manager__

    @property
    def actions(self):
        configured_actions = self.backend_mgr.actions
        actions = []
        for ca_name, ca in configured_actions.items():
            cxt = ca['context']
            if self.is_current_context_object or issubclass(cxt, _rsr.ModelResource):
                actions.append({
                    'url': _rsr.model_url(self.request, self.model, ca_name),
                    'label': self.backend_mgr.model.__name__ + '#' + ca_name,
                    'icon': ca['_icon'] if '_icon' in ca else None,
                })
        return actions

    @property
    def breadcrumbs(self):
        return []

    def action_list(self):
        return {
            'view': self,
        }

