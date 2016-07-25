# -*- coding:utf-8 -*-
__author__ = 'fantasy'

import os
from openerp.osv import fields,osv
from openerp.tools.translate import _
import base64
# import netsvc
import zlib

class station_solution_file(osv.Model):
    "rail document file must be pdf for this addon."
    _name = "station.solution.file"
    _description = __doc__
    _table = "station_solution_file"


    #为了解决upload上传时,Model无法重复构建的原因,所以在get_file时把full_path存下来
    #但每次get_file时都把_full_path=None,最后一次刚好存下来,保存时可以使用
    _full_path = None

    _uploaded = False

    def get_local_path(self,cr,uid,context):
        return self.pool.get('station.solution.config').get_local_document_repository(cr,uid,context=context)

    def unlink(self, cr, uid, ids, context=None):
        '''
            删除纪录时,把存储的文件删除掉
        '''
        if not isinstance(ids, list):
            ids = [ids]
        local_document_repository = self.get_local_path(cr, uid, context)
        if local_document_repository:
            for file in self.browse(cr, uid, ids, context=context):
                path = self._get_full_path(cr,uid,file.id,context)
                if os.path.isfile(path):
                    os.remove(path)
        return super(station_solution_file,self).unlink(cr,uid,ids,context=context)

    def create(self, cr, uid, vals, context=None):
        if context is None:
            context = {}
        vals['station_id'] = context.get('station_id',False) or vals.get('station_id',False)


        return super(station_solution_file,self).create(cr, uid, vals, context=context)


    def get_file(self,cr,uid,id,context=None):
        '''
            获取存储的文件内容
            先从文件夹中读取,失败后再从数据库中读取
        '''
        self._full_path = None
        full_path = self._get_full_path(cr,uid,id,context)
        item = self.read(cr, uid, int(id), ['name'])
        name = item.get('name')
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
        else:
            item = self.read(cr, uid, id, ['name','file_db_store'])
            file = item('file_db_store')
        return file,name



    def _get_file(self,cr,uid,ids,field_name,arg,context=None):
        res = {}
        for each in ids:
            res[each] = self.get_file(cr, uid, each, context=context)
        return res
    def _check_filestore(self,pdf_filestore):
        try:
            if not os.path.isdir(pdf_filestore):
                os.makedirs(pdf_filestore)
        except Exception,e:
            raise osv.except_osv(_('Error'),_('The file filestore can not be created,%s' %e))
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


    def _get_full_path(self,cr,uid,id,context):
        '''
            获取存储文件的完整路径:filestore/station_id/xxx.dwc
        '''
        # if self._full_path:
        #     return self._full_path

        item = self.read(cr, uid, int(id), ['name','station_id'])

        local_document_repository = self.get_local_path(cr, uid, context)
        station_id = item.get('station_id')[0]
        if local_document_repository and station_id:
            # station_item = self.pool.get('station.solution').read(cr,uid,station_id,['name'])
            # full_path = os.path.join(local_document_repository,station_item.get('name'))
            full_path = os.path.join(local_document_repository,str(station_id))
            self._full_path = full_path
            return full_path

        return None

    def del_file(self,cr,uid,id):
        '''
        供外部调用,只删除文件,不删除纪录
        '''
        item = self.read(cr,uid,int(id),['name','type'])
        name = item.get('name',None)
        type = item.get('type',None)
        if not name:
            return True

        path = self._get_full_path(cr,uid,id,context=None)
        if not path:
            return True

        full_path = os.path.join(path,name)
        if os.path.isfile(full_path):
            os.remove(full_path)

        if type and int(type) <5:
            self.write(cr,uid,[int(id)],{'name':u'','uploaded':False,'valid':False,'comments':u'必须上传'})
        else:
            self.write(cr,uid,[int(id)],{'name':u'','uploaded':False})

        self._uploaded = False




    def set_file(self,cr,uid,id,name,value):
        '''
            供外部调用
        '''
        self._set_file(cr,uid,id,name,value,None)
        self.write(cr, uid, [int(id)], {'name': name,'uploaded':True,'valid':True,'comments':u' '})
        self._uploaded = True

    def _set_file(self,cr,uid,id,name,value,arg,context=None):
        '''
            存储记录时用来存储文件
        '''
        if not value:
            return None
        local_document_repository = self.get_local_path(cr, uid, context)

        if local_document_repository:
            # item = self.read(cr,uid,id,['name','station_id'])
            full_path = self._get_full_path(cr,uid,id,context)
            return self._save_file(full_path, name, value)
        return self.write(cr, uid, id, {'file_db_store':value}, context=context)

    _columns = {
        'name':fields.char('file Name',size=100),
        'orgin_name':fields.char(u'原始文件名',size=100),
        'type':fields.selection([
            (1,u'CAD总图纸'),(2,u'连接图'),(3,u'系统图'),
            (4,u'平面图'),(5,u'PDF压缩文件'),(6,u'物流')
        ],u'文件类型',required=True),
        'extention':fields.char('file extention',size=6),
        'file_db_store':fields.binary('file stored in database'),
        'file':fields.function(_get_file,fnct_inv=_set_file,type='binary',method=True,string='file',filters='*.pdf'),
        'station_id':fields.many2one('station.baseinfo','station'),
        'comments':fields.text('Comments'),
        'write_date':fields.datetime('Date Modified',readonly=True),
        'write_uid':fields.many2one('res.users','Last modification User',readonly=True),
        'create_date':fields.datetime('Date Created',readonly=True),
        'create_uid':fields.many2one('res.users','Creator',readonly=True),
        'user_id':fields.many2one('res.users','Owner'),
        'group_ids':fields.many2many('res.groups','rail_document_image_group_rel','item_id','group_id','Groups'),
        'company_id':fields.many2one('res.company','Company',change_default=True),
        'uploaded':fields.boolean('isuploaded'),
        'valid':fields.boolean('isvalid'),
        'isjson':fields.boolean('isjson')
    }

    _defaults = {
                 'company_id':lambda s,cr,uid,c: s.pool.get('res.company')._company_default_get(cr,uid,'station.solution.file',context=c),
                 'user_id':lambda self,cr,uid,ctx:uid,
                 #'static':True,
                 }

    def open_url(self, cr, uid, ids, context=None):
        return {
            'type': 'ir.actions.act_url',
            'url': 'http://www.baidu.com',
            'target': 'new'}

    def write(self, cr, uid, ids, vals, context=None):
        if isinstance(ids, (int, long)):
            ids = [ids]
        res = super(station_solution_file, self).write(cr, uid, ids, vals, context=context)
        return res


    def act_upload(self,cr,uid,ids,context=None):
        while not self._uploaded:
            # item = self.read(cr, uid, ids, ['uploaded','name'])
            # is_uploaded = item[0].get('uploaded',False)
            import time
            time.sleep(1)
            # break
        # self.write(cr,uid,ids,{'uploaded',False},context=context)
        self._uploaded = False
        return False#self.write(cr, uid, ids, {'name': 'uploadfile'}, context=context)

    def act_delfile(self,cr,uid,ids,context=None):
        # item = self.read(cr, uid, ids[0], ['name'])
        # name = item.get('name',None)
        # if name:
        self.del_file(cr,uid,ids[0])
        return True

    def act_download(self,cr,uid,ids,context=None):
        _id = ids[0]
        # item = self.read(cr, uid, _id, ['uploaded','name','station_id'])
        # name = item.get('name',None)
        # station_id = item.get('station_id',None)
        #
        # if not name or not station_id:
        #     return False
        #
        # path = self._get_full_path(cr,uid,_id,context=None)
        # if not path:
        #     return False
        #
        # full_path = os.path.join(path,name)


        return  {
            'type': 'ir.actions.act_url',
            'url': 'web/custom_upload_file/download/'+str(_id),
            'target': 'self'}
    # def bt_start(self,cr,uid,ids,context=None):
    #     return {
    #         'type': 'ir.actions.client',
    #         'tag': 'web_widget_uploadfile.bt_start',
    #     }

    # _sql_constraints = [
    #     ('filename_unique', 'unique (name,parent_id)', 'The filename must be unique in a directory !')
    # ]
