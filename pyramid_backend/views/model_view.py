__author__ = 'tarzan'

import urllib
from datetime import datetime
import deform
from webhelpers.paginate import Page
from pyramid.httpexceptions import HTTPFound
from . import cell_datatype
from .. import resources as _rsr
import json

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
                _label = ca['_label'] if '_label' in ca else (self.backend_mgr.display_name + '#' + ca_name)
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
                _label = ca['_label'] if '_label' in ca else ('%s#' + ca_name)
                _label = _label % obj
                _onclick = json.dumps(ca['_onclick'] % obj).strip('"\'') if '_onclick' in ca else None
                actions.append({
                    'url': _rsr.object_url(self.request, obj, ca.get('name', None)),
                    'label': _label,
                    'icon': ca['_icon'] if '_icon' in ca else None,
                    'onclick': _onclick,
                })
        return actions

    @property
    def breadcrumbs(self):
        return []

    def list_page_url(self, page, partial=False):
        params = self.request.GET.copy()
        params["_page"] = page
        if partial:
            params["partial"] = "1"
        qs = urllib.urlencode(params, True)
        return "%s?%s" % (self.request.path, qs)

    def action_list(self):
        cur_page = int(self.request.params.get("_page", 1))
        # objs = self.DBSession.query(self.Object)
        # attr_names = self.obj_attr_names
        #
        # for name, value in self.request.params.mixed().iteritems():
        #     if name in attr_names:
        #         objs = objs.filter(getattr(self.Object, name).like("%%%s%%" % value))
        #
        # from sqlalchemy import func
        # objs = objs.order_by(self.Object.id.desc())
        # item_count = self.DBSession.query(func.count(self.Object.id))
        # for name, value in self.request.params.mixed().iteritems():
        #     if name in attr_names:
        #         item_count = item_count.filter(getattr(self.Object, name).like("%%%s%%" % value))
        # item_count = item_count.scalar()
        #
        # page = Page(objs, page=cur_page,
        #             item_count=item_count,
        #             items_per_page=self.list__items_per_page,
        #             url=PageURL_WebOb(self.request)
        #             )
        #
        # return {
        #     "page": page,
        #     "view": self,
        # }
        filters = {k:v for k,v in self.request.GET.items() if not k.startswith('_')}
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
            # 'columns': self.backend_mgr.list__column_names_to_display,
            'page': page,
        }

    def action_create(self):
        schema = self.backend_mgr.schema_cls().bind()
        form = deform.Form(schema,
                           buttons=(deform.Button(title='Create'),
                                    deform.Button(title='Cancel', type='reset', name='cancel')))

        if 'submit' in self.request.POST:
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

    def action_update(self):
        obj = self.context.object
        schema = self.backend_mgr.schema_cls().bind(obj=obj)
        appstruct = {c.name:obj.__getattribute__(c.name) for c in schema.children}
        form = deform.Form(schema,
                           appstruct=appstruct,
                           buttons=(deform.Button(title='Update'),
                                    deform.Button(title='Cancel', type='reset', name='cancel')))

        if 'submit' in self.request.POST:
            try:
                data = form.validate(self.request.POST.items())
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
