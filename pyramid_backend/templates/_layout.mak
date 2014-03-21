<%!
    def get_layout_file(context):
        try:
            return context['main_template'].uri
        except KeyError:
            return None
%>
<%inherit file="${get_layout_file(context)}"/>

<style type="text/css">
.table-objects td, .object-detail {font-family: Monaco,Menlo,Consolas,"Courier New",monospace; font-size:90%;}
td.datatype-number {text-align: right}
td.datatype-datetime {text-align: right}
.datatype-bool {font-weight: bold; font-style: italic}
</style>

<%block name="flashes_block">
<% messages = request.session.pop_flash('pbackend') %>
% if messages:
    % for message in messages:
        <div class="alert alert-success">${message}</div>
    % endfor
% endif
</%block>

<%block name="page_header">
<legend>
    <%block name="page_title">There's no title here</%block>
    <small>
      <div class="pull-right">
      % for cmd in view.toolbar_actions:
        <a href="${cmd['url']}" title="${cmd['label']}"><span class="glyphicon glyphicon-${cmd.get('icon', 'usd') or 'usd'}"></span></a>
      % endfor
      </div>
    </small>
</legend>
</%block>


<%block name="breadcrumbs">
<% entries = view.breadcrumbs %>
% if len(entries):
<ul class="breadcrumb">
% for e in entries:
    % if isinstance(e, basestring):
        <li class="active">${e}</li>
    % else:
    <li><a href=${e['url']}>${e['label']}</a></li>
    % endif
% endfor
</ul>
% endif
</%block>
${next.body()}