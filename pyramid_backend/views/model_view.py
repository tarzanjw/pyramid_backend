__author__ = 'tarzan'

import deform
from pyramid.httpexceptions import HTTPFound
from .. import resources as _rsr

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
            if issubclass(cxt, _rsr.ModelResource):
                _label = ca['_label'] if '_label' in ca else (self.backend_mgr.display_name + '#' + ca_name)
                actions.append({
                    'url': _rsr.model_url(self.request, self.model, ca.get('name', None)),
                    'label': _label,
                    'icon': ca['_icon'] if '_icon' in ca else None,
                })
            elif self.is_current_context_object:
                _label = ca['_label'] if '_label' in ca else ('%s#' + ca_name)
                _label = _label % self.context.object
                actions.append({
                    'url': _rsr.model_url(self.request, self.model, ca.get('name', None)),
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

    def action_create(self):
        schema = self.backend_mgr.schema_cls()
        form = deform.Form(schema, buttons=(deform.Button(title='Create'),))

        if self.request.method == 'POST':
            try:
                data = form.validate(self.request.POST.items())
                obj = self.backend_mgr.create(data)
                self.request.session.flash(u'"%s" was created successful.' % obj, queue='pbackend')
                return HTTPFound(_rsr.object_url(self.request, obj))
            except deform.ValidationFailure as e:
                pass

        return {
            'view': self,
            "form": form,
        }

    def action_detail(self):
        return {

        }