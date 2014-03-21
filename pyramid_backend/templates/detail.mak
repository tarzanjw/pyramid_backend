<%! import markupsafe %>
<%inherit file="_layout.mak" />
<%namespace file="_layout.mak" import="data_cell" />

<style type="text/css">
.object-detail .row {
    padding: 0 0.5em;
    border-bottom: 1px solid #eaf2fb;
}
.object-detail .name, .object-foreign-keys .name, .object-relation .name {
    font-weight: bold;
    text-align: right;
}
</style>
<%block name="page_title">${backend_mgr.display_name}#${obj} detail</%block>

<%block name="object_detail">
% for attr_name, label in backend_mgr.detail__column_names_to_display.items():
<%
    val = obj.__getattribute__(attr_name)
    val_type = view.cell_datatype(val)
%>
<div class="object-detail">
    <div class="row col-type-general">
        <div class="col-lg-3 name">${label}</div>
        <div class="col-lg-9 value datatype-${val_type}">${data_cell(val)}</div>
    </div>
</div>
% endfor
##% if 'delete' in view.actions:
##<div row col-type-general>
##    <div class="col-lg-9 col-lg-offset-3">
##        <a class="btn btn-sm btn-danger" id="btnDelete"
##           data-message="Do you want to delete ${view.Resource.__name__}#${request.context.__name__}"
##           href="${request.resource_url(request.context, 'delete')}">
##            Delete</a>
##    </div>
##</div>
##<script type="text/javascript">
##jQuery(function($) {
##    $('#btnDelete').click(function(e) {
##        if (confirm($(this).attr('data-message')))
##            return true;
##        else {
##            e.preventDefault();
##            return false;
##        }
##    })
##})
##</script>
##% endif
</%block>
##
##<%
##    _ = request.root
##%>
##
##% if view.foreign_keys:
##<legend>Foreign keys</legend>
##<div class="object-foreign-keys">
##% for fk in view.foreign_keys:
##% if cur_obj.__getattribute__(fk):
##<%
##    fk_obj = cur_obj.__getattribute__(fk)
##    fk_name = fk
##%>
##<div class="row col-type-general">
##    <div class="col-lg-3 name">${' '.join([word.capitalize() for word in fk_name.split('_')])}</div>
##    <div class="col-lg-9 value">
##        <a href="${object_url(fk_obj)}">${fk_obj}</a>
##    </div>
##</div>
##% endif
##% endfor
##</div>
##% endif
##
##% if view.relations:
##<legend>Relations</legend>
##<div class="object-relations">
##% for rel_name, rel_model, fk_col in view.relations:
##    <div class="row object-relation">
####        <%
####            if 'query' in rel and rel['query']:
####                query = {}
####                for _name, _value in rel['query'].iteritems():
####                    query[_name] = cur_obj.__getattribute__(_value)
####            else:
####                query = {}
####        %>
##        <div class="col-lg-3 name">
##          <a href="${model_url(rel_model, query={fk_col:cur_obj.id})}">
##            ${' '.join([word.capitalize() for word in rel_name.split('_')])}
##          </a>
##        </div>
##        <% rel_objs = cur_obj.__getattribute__(rel_name) %>
##        <div class="col-lg-9">
####            <div>${len(rel_objs)}</div>
##            <ul class="list-unstyled">
##            % for obj in rel_objs[:10]:
##                <li><a href="${object_url(obj)}">${obj}</a></li>
##            % endfor
##            </ul>
##        </div>
##    </div>
##% endfor
##</div>
##% endif