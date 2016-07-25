# -*- coding:utf-8 -*-
__author__ = 'fantasy'

from openerp.osv import fields, osv
from openerp.tools.translate import _
import os
import xlrd
import codecs
import simplejson
import logging
import psycopg2
from openerp import SUPERUSER_ID
# from station import station_baseinfo
from openerp import models

# class station_material(osv.Model):
#     _name = "station.material"
#
#     _columns = {
#         'sequence':fields.integer(string=u'序号'),
#         'station_id':fields.many2one('station.baseinfo','station'),
#         'name':fields.char(u'名称',size=512),
#         'specifications':fields.char(u'规格程式',size=512),
#         'unit':fields.char(u'单位',size=512),
#         'number':fields.integer(u'数量'),
#         'price':fields.float(u'单价(元)'),
#         'total':fields.float(u'合计(元)'),
#         'remarks':fields.char(u'备注',size=1024)
#     }
FIELDS_RECURSION_LIMIT = 2
ERROR_PREVIEW_BYTES = 200
_logger = logging.getLogger(__name__)
class station_material(models.AbstractModel):
    # _inherit = 'save.file.base.model'
    _name = 'station.material'


    def save_file(self,cr,uid,import_id,parent_id,file_name,file_content):

        # self.pool('station.baseinfo').read(cr,uid,int(id),['name','type'])
        # file_content = file_content.decode("utf-8")
        solution = self.pool('station.baseinfo')
        solution.set_file(cr,uid,parent_id,file_name,file_content)
        solution.write(cr, uid, [int(parent_id)], {'material_xls_file_name': file_name})

        rows = self._read_xls(file_content)
        json_data = simplejson.dumps(rows,ensure_ascii=False)
        splites = os.path.splitext(file_name)
        file_name = splites[0]+'.json'
        solution.set_json_file(cr,uid,parent_id,file_name,json_data)

        count = self._get_unit_count(rows)
        solution.write(cr, uid, [int(parent_id)], {'material_file_name': file_name,'unit_count':count})
        return json_data

    def _get_unit_count(self,rows):
        row = rows[-1]
        return row.get(u'\u5408\u8ba1(\u5143)',0)

    def _read_xls(self,file_content):
        try:
            data = xlrd.open_workbook(file_contents=file_content)
            sheet = data.sheet_by_index(0)

            nrows = sheet.nrows
            ncols = sheet.ncols
            header = sheet.row_values(0)
            # match_header = self._match_fields(header,fields)

            # if len(match_header) == len(header):
            list =[]
            for rowx in range(1,nrows):
                row = sheet.row_values(rowx)
                if row:
                    app = {}
                    for colx in range(ncols):
                        app[header[colx]] = row[colx]
                    list.append(app)
                # header_list = []
                # for colx in range(ncols):
                #     header_list.append(header[colx])
            return list
        except Exception, e:
            _logger.debug("Error during XML parsing preview", exc_info=True)
            return {
                'error': str(e),
                'preview': file_content[:ERROR_PREVIEW_BYTES]
                                .decode( 'utf-8'),
            }


class station_audit(models.AbstractModel):
    _name = 'station.audit'

    def save_file(self,cr,uid,import_id,parent_id,file_name,file_content):
        # solution = self.pool('station.baseinfo')

        json_data = simplejson.loads(file_content)
        json_involved = json_data.get('Involved',None)
        json_notInvolved = json_data.get('NotInvolved',None)

        notinvolved_data = self.save_notinvolved_data(cr,uid,parent_id,json_notInvolved)

        involved_data = self.save_involved_data(cr,uid,import_id,parent_id,json_involved)
        # involved_data = simplejson.dumps(json_involved,ensure_ascii=False)
        # file_involved_name = 'involved.json'

        #: TODO:智能分析添加建筑物材质列表,然后与单位提义的列表进行比对


        # solution.set_json_file(cr,uid,parent_id,file_involved_name,involved_data)

        return notinvolved_data

    # def do_it(self,cr,uid,id,context=None):
    #
    #
    def save_involved_data(self,cr,uid,import_id,parent_id,json_data):
        model_import = self.pool('direct.import')
        sucess = model_import.write(cr,uid,[import_id],{'res_model':'station.solution.involved'})
        result = model_import.do_it_json(cr,uid,import_id,json_data,context=None)
        ids = result.get('ids',None)

        model_invovled = self.pool('station.solution.involved')
        model_invovled.write(cr,uid,ids,{'station_id':parent_id})


    def save_notinvolved_data(self,cr,uid,parent_id,json_data):
        solution = self.pool('station.baseinfo')
        notinvolved_data = simplejson.dumps(json_data,ensure_ascii=False)
        file_notinvolved_name = 'notinvolved.json'
        solution.write(cr, uid, [int(parent_id)], {'notinvolved_file_name': file_notinvolved_name})
        solution.set_json_file(cr,uid,parent_id,file_notinvolved_name,notinvolved_data)

        return notinvolved_data


class station_solution(osv.Model):
    _inherit = "station.baseinfo"
    # _name = 'station.solution'

    def create(self, cr, uid, vals, context=None):

        _id = super(station_solution, self).create(cr, uid, vals, context=context)

        #每个项目设置五个类型的文件
        #(1,u'CAD总图纸'),(2,u'连接图'),(3,u'系统图'),
        #    (4,u'平面图'),(5,u'PDF压缩文件')
        file = self.pool.get('station.solution.file')

        for i in range(1, 7):
            if i < 5:
                file_values = {
                    'type':i,
                    'station_id':_id,
                    'valid':False,
                    'comments':u'必须上传'
                }
            else:
                file_values = {
                    'type':i,
                    'station_id':_id,
                    'valid':True
                }

            file.create(cr,uid,file_values)


        # self._create_directory(cr,uid,vals,context=_id)
        return _id


    def open_url(self, cr, uid, ids, context=None):
        return {
            'type': 'ir.actions.act_url',
            'url': 'http://www.baidu.com',
            'target': 'new'}

    def action_to_open_analysis(self,cr,uid,ids,context=None):
        if context is None:
            context = {}
        if context.get('xml_id'):
            res = self.pool.get('ir.actions.act_window').for_xml_id(cr, uid ,'station_solution', context['xml_id'], context=context)
            res['res_id'] = ids[0]
            # res['context'] = {'default_station_id':'active_id'}
            # res['domain'] = [('default_station_id','=','active_id')]
            # res['default_station_id'] = ids[0]
            return res
        return False

    def action_to_open(self, cr, uid, ids, context=None):
        """ This opens the xml view specified in xml_id for the current category """
        if context is None:
            context = {}
        if context.get('xml_id'):
            res = self.pool.get('ir.actions.act_window').for_xml_id(cr, uid ,'station_solution', context['xml_id'], context=context)
            res['res_id'] = ids[0]
            res['flags'] ={'search_view':False}
            # res['context'] = {'default_station_id':'active_id'}
            # res['domain'] = [('default_station_id','=','active_id')]
            # res['default_station_id'] = ids[0]
            return res
        return False

    def act_export(self,cr,uid,ids,context=None):
        pass

    def get_local_path(self,cr,uid,context):
        return self.pool.get('station.solution.config').get_local_document_repository(cr,uid,context=context)


    def _get_full_path(self,cr,uid,id):
        '''
            获取存储文件的完整路径:filestore/station_id/xxx.dwc
        '''
        # if self._full_path:
        #     return self._full_path


        local_document_repository = self.get_local_path(cr, uid, context=None)
        if local_document_repository and id:
            full_path = os.path.join(local_document_repository,str(id))
            return full_path

        return None

    def _get_file(self,cr,uid,id,name):
        '''
            获取存储的文件内容
            先从文件夹中读取,失败后再从数据库中读取
        '''
        full_path = self._get_full_path(cr,uid,id)
        full_path = os.path.join(full_path,name)
        if full_path:
            if os.path.exists(full_path):
                try:
                    f = open(full_path,'rb')
                    file = f.read()
                    f.close()
                except Exception,e:
                    # logger = netsvc.Logger()
                    # logger.notifyChannel('station_solution_file',netsvc.LOG_ERROR,'Can not open the file %s,error:%s' %(full_path,e))
                    return False
            else:
                # logger = netsvc.Logger()
                # logger.notifyChannel('station_solution_file',netsvc.LOG_ERROR,"The file % doesn't exist " %full_path)
                return False
        return file,name

    def set_file(self,cr,uid,id,name,value):
        '''
            供外部调用
        '''
        self._set_file(cr,uid,id,name,value)
        # self.write(cr, uid, [int(id)], {'name': name})

    def _set_file(self,cr,uid,id,name,value):
        '''
            存储记录时用来存储文件
        '''
        if not value:
            return None
        local_document_repository = self.get_local_path(cr, uid, context=None)

        if local_document_repository:
            full_path = self._get_full_path(cr,uid,id)
            return self._save_file(full_path, name, value)

    def set_json_file(self,cr,uid,id,name,value):
        if not value:
            return None
        local_document_repository = self.get_local_path(cr, uid, context=None)

        if local_document_repository:
            path = self._get_full_path(cr,uid,id)
            full_path = os.path.join(path,name)
            self._check_filestore(path)

            ofile = codecs.open(full_path,'w',encoding='utf-8')
            try:
                ofile.write(value)
            finally:
                ofile.close()
            return True


    def _save_file(self,path,filename,b64_file):
        """Save a file encoded in base 64"""
        full_path = os.path.join(path,filename)
        self._check_filestore(path)

        ofile = open(full_path,'w')
        try:
            ofile.write(b64_file)
        finally:
            ofile.close()
        return True

    def _check_filestore(self,pdf_filestore):
        try:
            if not os.path.isdir(pdf_filestore):
                os.makedirs(pdf_filestore)
        except Exception,e:
            raise osv.except_osv(_('Error'),_('The file filestore can not be created,%s' %e))
        return True


    def get_material(self,cr,uid,id,context=None):
        item = self.read(cr, uid, int(id), ['material_file_name'])
        name = item.get('material_file_name')
        if name:
            return self._get_file(cr,uid,id,name)

    def set_material(self,cr,uid,id,name,value):
        self._set_file(cr,uid,id,name,value,None)
        self.write(cr, uid, [int(id)], {'material_file_name': name})

    def _get_material(self,cr,uid,ids,field_name,arg,context=None):
        res = {}
        for each in ids:
            res[each] = self.get_material(cr,uid,each,context=context)
        return res

    def _set_material(self,cr,uid,id,name,value,arg,context=None):
        self._set_file(cr,uid,id,name,value)


    def set_notinvolved(self,cr,uid,id,name,value):
        self.set_json_file(cr,uid,id,name,value,None)
        self.write(cr, uid, [int(id)], {'notinvolved_file_name': name})

    def _set_notinvolved(self,cr,uid,id,name,value,arg,context=None):
        self.set_notinvolved(cr,uid,id,name,value)

    def get_notinvolved(self,cr,uid,id,context=None):
        item = self.read(cr, uid, int(id), ['notinvolved_file_name'])
        name = item.get('notinvolved_file_name')
        if name:
            return self._get_file(cr,uid,id,name)

    def _get_notinvolved(self,cr,uid,ids,field_name,arg,context=None):
        res = {}
        for each in ids:
            res[each] = self.get_notinvolved(cr,uid,each,context=context)
        return res


    STATE_SELECTION = [
        ('draft', '未送审'),
        ('sent', u'已送审'),
        ('rejected', u'驳回'),
        ('approved', u'审核通过')
    ]

    _columns = {
        'file_ids':fields.one2many(
                'station.solution.file',
                'station_id',
                'Files',
                domain=[('type', '<=', 5)]
        ),
        # 'material_file':fields.one2many('station.solution.file','material_file_id','material_file',domain=[('type', '=', 6)]),
        'material_xls_file_name':fields.char('material_xls_file_name'),
        'material_file':fields.function(_get_material,fnct_inv=_set_material,type='binary',method=True,string='file'),
        'material_file_name':fields.char('material_file_name'),

        'state': fields.selection(STATE_SELECTION, 'Status', readonly=True,
                                  select=True, copy=False),

        'notinvolved_file':fields.function(_get_notinvolved,fnct_inv=_set_notinvolved,type='binary',method=True,string='notinvolved'),
        'notinvolved_file_name':fields.char('notinvolved_file_name'),

        'involved_ids':fields.one2many(
            'station.solution.involved',
            'station_id',
            'involved'
        )
    }


    def act_analyze(self,cr,uid,ids,context=None):
        pass


