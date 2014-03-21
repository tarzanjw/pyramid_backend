<%! import markupsafe %>
<%inherit file="_layout.mak"/>

<%block name="page_title">${request.context.model.__backend_manager__.display_name} list</%block>

<%block name="object_list">
<table class="table table-striped table-bordered table-condensed table-objects">
    <thead>
        <tr>
            <th>Commands</th>
            % for name, label in columns.items():
            <th class="">${label}</th>
            % endfor
        </tr>
    </thead>
    <tbody>
    % for e in page.items:
        <tr>
            <td class="col-type-commands">
                % for cmd in view.object_actions(e):
                <a href="${cmd['url']}" title="${cmd['label']}"><span class="glyphicon glyphicon-${cmd.get('icon', 'usd') or 'usd'}"></span></a>
                % endfor
##                % if 'detail' in view.actions:
##                <a href="${request.resource_url(request.context[e.id])}">
##                    <span class="glyphicon glyphicon-eye-open"></span></a>
##                % endif
##                % if 'update' in view.actions:
##                <a href="${request.resource_url(request.context[e.id], 'update')}">
##                    <span class="glyphicon glyphicon-edit"></span></a>
##                % endif
##                % if 'delete' in view.actions:
##                <a class="cmd-delete" href="${request.resource_url(request.context[e.id], 'delete')}"
##                   data-message="Do you want to delete ${view.Object.__name__} ${e}">
##                    <span class="glyphicon glyphicon-remove"></span></a>
##                % endif
            </td>
        % for name in columns:
            <%
                val = e.__getattribute__(name)
                val_type = view.cell_datatype(val)

                val = str(markupsafe.escape(val))
                if val_type == 'longtext':
                    val = '<br>'.join(val.splitlines())
                elif val_type == 'none':
                    val = '<code>' + val + '</code>'
                val = unicode(val)
            %>
            <td class="datatype-${val_type}">${val|n}</td>
        % endfor
        </tr>
    % endfor
    </tbody>
</table>
</%block>

<%block name="object_paging">
<%
    import re
    pager_html = page.pager(
        format='(Page $page of $page_count) &nbsp;&nbsp; <ul class="pagination pagination-sm">$link_first~3~$link_last</ul>',
        dotdot_attr={"class":"disabled"},
        curpage_attr={"class":"current-page"},
        symbol_first=u'«',
        symbol_last=u'»',
    )

    ## replace current page link
    pager_html = unicode(pager_html)
    pager_html = re.sub(
        r'<span[^>]+class="current-page">(.*?)</span>',
        r'<li class="active"><a href="#">\1 <span class="sr-only">(current)</span></a></li>',
        pager_html)
    pager_html = re.sub(
        r'<a[^>]+class="pager_link"[^>]+href="([^"]*)">(.*?)</a>',
        r'<li><a href="\1">\2</a></li>',
        pager_html)
    pager_html = re.sub(
        r'<span[^>]+class="disabled"[^>]*>(.*?)</span>',
        r'<li class="disabled"><span>\1</span></li>',
        pager_html)
%>
${pager_html|n}
</%block>