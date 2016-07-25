# -*- coding: utf-8 -*-
import cgi
import simplejson

from openerp.http import Controller, route

class ImportController(Controller):
    @route('/direct_import/upload')
    def set_file(self, req, file, import_id,parent_id,save_type,model,jsonp='callback'):

        out = """<script language="javascript" type="text/javascript">
                    var win = window.top.window;
                    win.jQuery(win).trigger(%s, %s);
                </script>"""

        import_id = int(import_id)
        if (save_type == 'file'):
            Model = req.session.model(model)
            # obj = req.env[model]
            # obj.init(parent_id)
            data = file.read()
            json_data = Model.save_file(import_id,parent_id,file.filename,data)

        # return out % (simplejson.dumps(jsonp), json_data)
        #TODO:上传完成后,在客户端加载数据
        return 'window.top.%s(%s)' % (
            cgi.escape(jsonp), simplejson.dumps({'result': json_data}))


        Model = req.session.model('direct.import')

        written = Model.write(import_id, {
            'file': file.read(),
            'file_name': file.filename,
            'file_type': file.content_type,
        }, req.context)
        options = {
                'headers':True}
        # data = Model.parse_preview(import_id,options)
        Model.do_it(import_id,options)

        return 'window.top.%s(%s)' % (
            cgi.escape(jsonp), simplejson.dumps({'result': written}))

    #  @http.route('/web/material/upload', type='http', auth='user')
    # def upload_material(self,callback,ufile,jsonp='callback'):
    #     data = ufile.read()
    #     args = [len(data), ufile.filename,
    #             ufile.content_type]
    #
    #     return 'window.top.%s(%s)' % (
    #         cgi.escape(jsonp), simplejson.dumps({'result': True}))
