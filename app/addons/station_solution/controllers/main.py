# coding: utf-8
import simplejson
import base64
import urllib2
import cgi
from openerp.tools import ustr
from openerp import http
from openerp.http import request


class Uploadfile(http.Controller):
    @http.route('/web/custom_upload_file/upload', type='http', auth='user')
    def upload(self, callback, ufile):
        # out = """<script language="javascript" type="text/javascript">
        #             var win = window.top.window;
        #             win.jQuery(win).trigger(%s, %s);
        #         </script>"""
        # try:
        data = ufile.read()
        args = [len(data), ufile.filename,
                ufile.content_type]

        id = callback.replace('oe_form_file', '')

        # data = base64.b64encode(data)

        Model = request.session.model('station.solution.file')
        Model.del_file(id)
        # item =Model.read([int(id)],False,request.context)
        Model.set_file(id, ufile.filename, data)

        # return '''{'upload':ok}'''
    # except Exception, e:
    #     args = [False, e.message]
    #     return out % (simplejson.dumps(callback), simplejson.dumps(args))

    @http.route('/web/custom_upload_file/download/<id>', type='http', auth='public')
    def download(self,id):
        Model = request.session.model('station.solution.file')

        file,name = Model.get_file(int(id),request.context)

        return request.make_response(file,
                [('Content-Type', 'application/octet-stream'),
                 ('Content-Disposition', self.content_disposition(name))])

    @http.route('/web/custom_upload_file/json/<id>', type='http', auth='public')
    def get_json_content(self,id):
        Model = request.session.model('station.solution')
        file,name = Model.get_material(int(id),request.context)
        return file

    # @http.route('/web/material/upload', type='http', auth='user')
    # def upload_material(self,callback,ufile,jsonp='callback'):
    #     data = ufile.read()
    #     args = [len(data), ufile.filename,
    #             ufile.content_type]
    #
    #     return 'window.top.%s(%s)' % (
    #         cgi.escape(jsonp), simplejson.dumps({'result': True}))





    def content_disposition(self,filename):
        filename = ustr(filename)
        escaped = urllib2.quote(filename.encode('utf8'))
        browser = request.httprequest.user_agent.browser
        version = int((request.httprequest.user_agent.version or '0').split('.')[0])
        if browser == 'msie' and version < 9:
            return "attachment; filename=%s" % escaped
        elif browser == 'safari' and version < 537:
            return u"attachment; filename=%s" % filename.encode('ascii', 'replace')
        else:
            return "attachment; filename*=UTF-8''%s" % escaped




