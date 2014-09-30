__author__ = 'tarzan'

import six
if six.PY2:
    from urllib import urlencode
else:
    from urllib.parse import urlencode
import inspect
import deform
from pyramid_backend.helpers.paginate import Page
from pyramid.httpexceptions import HTTPFound
from pyramid.view import view_config
from . import cell_datatype
from .. import resources as _rsr
import json
import colander
from pyramid.traversal import lineage


def _none_to_colander_null(data):
    return {k: v if v is not None else colander.null for k, v in data.items()}


def _colander_null_to_none(data):
    return {k: v if v is not colander.null else None for k, v in data.items()}


class InvalidSchemaClassError(RuntimeError):
    def __init__(self, backend_mgr):
        """
        :type backend_mgr: pyramid_backend.backend_manager.Manager
        """
        self.backend_mgr = backend_mgr
        super(InvalidSchemaClassError, self).__init__('%s is not class for %s\'s schema'
                                                      % (self.backend_mgr.schema_cls,
                                                         self.backend_mgr.Model))


@view_config(context=InvalidSchemaClassError, renderer='pyramid_backend:templates/no_schema.mak')
def on_invalid_schema_class(context, request):
    return {
        'error': context,
    }


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
    def model_schema_cls(self):
        if not inspect.isclass(self.backend_mgr.schema_cls):
            raise InvalidSchemaClassError(self.backend_mgr)
        # assert inspect.isclass(self.backend_mgr.schema_cls), \
        #     '%s.__backend_schema_cls__ (%s) is not a class' % \
        #     (self.model.__name__, self.backend_mgr.schema_cls)
        return self.backend_mgr.schema_cls

    def cell_datatype(self, val):
        return cell_datatype(val)

    @property
    def toolbar_actions(self):
        actions = self.model_actions
        if isinstance(self.context, self.backend_mgr.ObjectResource):
            actions += self.object_actions(self.context.object)
        return actions

    @property
    def model_actions(self):
        configured_actions = self.backend_mgr.actions
        actions = []
        for ca_name, ca in configured_actions.items():
            cxt = ca['context']
            if issubclass(cxt, _rsr.ModelResource):
                _label = ca['_label'] if '_label' in ca else \
                    (self.backend_mgr.display_name + '@' + ca_name)
                actions.append({
                    'url': _rsr.model_url(self.request, self.model, ca.get('name', None)),
                    'label': _label,
                    'icon': ca['_icon'] if '_icon' in ca else None,
                })
        return actions

    def object_actions(self, obj):
        actions = []
        for ca_name, ca in self.backend_mgr.actions.items():
            cxt = ca['context']
            if issubclass(cxt, _rsr.ObjectResource):
                _label = ca['_label'] if '_label' in ca else ('%s@' + ca_name)
                _label = _label % obj
                _onclick = json.dumps(ca['_onclick'] % obj).strip(
                    '"\'') if '_onclick' in ca else None
                actions.append({
                    'url': _rsr.object_url(self.request, obj, ca.get('name', None)),
                    'label': _label,
                    'icon': ca['_icon'] if '_icon' in ca else None,
                    'onclick': _onclick,
                })
        return actions

    @property
    def breadcrumbs(self):
        cxt = self.context
        cxts = list(reversed(list(lineage(cxt))))
        r = self.request
        if not r.view_name:
            if self.is_current_context_object:
                cmd_name = 'detail'
            else:
                cmd_name = 'list'
            cxts = cxts[:-1]
        else:
            cmd_name = r.view_name

        if cmd_name in self.backend_mgr.actions:
            ca = self.backend_mgr.actions[cmd_name]
            if self.is_current_context_object:
                _label = ca['_label'] if '_label' in ca else ('%s@' + cmd_name)
                _label = _label % cxt.object
            else:
                _label = ca['_label'] if '_label' in ca else \
                    (self.backend_mgr.display_name + '@' + cmd_name)
        else:
            _label = '@' + cmd_name

        return [{
            'url': r.resource_url(c),
            'label': u'%s' % c,
        } for c in cxts] + [_label, ]

    def list_page_url(self, page, partial=False):
        params = self.request.GET.copy()
        params["_page"] = page
        if partial:
            params["partial"] = "1"
        qs = urlencode(params, True)
        return "%s?%s" % (self.request.path, qs)

    def action_list(self):
        cur_page = int(self.request.params.get("_page", 1))
        filters = {k: v for k, v in self.request.GET.items() if not k.startswith('_')}
        objects = self.backend_mgr.fetch_objects(page=cur_page, filters=filters)
        objects = list(objects)
        objects_count = self.backend_mgr.count_objects(filters)
        # objects_count = objects_count * 20
        page = Page(objects, page=cur_page,
                    item_count=objects_count,
                    items_per_page=self.backend_mgr.list__items_per_page,
                    url=self.list_page_url,
                    presliced_list=True,
        )
        return {
            'view': self,
            'backend_mgr': self.backend_mgr,
            'page': page,
        }

    def action_create(self):
        schema = self.model_schema_cls().bind()
        form = deform.Form(schema,
                           buttons=(deform.Button(title='Create'),
                                    deform.Button(title='Cancel', type='reset', name='cancel')))

        if 'submit' in self.request.POST:
            try:
                data = form.validate(self.request.POST.items())
                data = _colander_null_to_none(data)
                obj = self.backend_mgr.create(data)
                self.request.session.flash(u'"%s" was created successful.' % obj, queue='pbackend')
                return HTTPFound(_rsr.object_url(self.request, obj))
            except deform.ValidationFailure as e:
                pass

        return {
            'view': self,
            "form": form,
        }

    def action_update(self):
        obj = self.context.object
        schema = self.model_schema_cls().bind(obj=obj)
        """:type schema: colander.Schema"""
        appstruct = _none_to_colander_null({k: obj.__getattribute__(k)
                                            for k in self.backend_mgr.column_names})
        form = deform.Form(schema,
                           appstruct=appstruct,
                           buttons=(deform.Button(title='Update'),
                                    deform.Button(title='Cancel', type='reset', name='cancel')))

        if 'submit' in self.request.POST:
            try:
                data = form.validate(self.request.POST.items())
                data = _colander_null_to_none(data)
                obj = self.backend_mgr.update(obj, data)
                self.request.session.flash(u'"%s" was updated successful.' % obj, queue='pbackend')
                return HTTPFound(_rsr.object_url(self.request, obj))
            except deform.ValidationFailure as e:
                pass

        return {
            'view': self,
            'obj': obj,
            "form": form,
        }

    def action_detail(self):
        return {
            'view': self,
            'obj': self.context.object,
            'backend_mgr': self.backend_mgr,
        }

    def action_delete(self):
        obj = self.context.object
        self.backend_mgr.delete(obj)
        self.request.session.flash(u'%s#%s was history!' % (self.backend_mgr.display_name, obj))
        return HTTPFound(_rsr.model_url(self.request, self.model))
