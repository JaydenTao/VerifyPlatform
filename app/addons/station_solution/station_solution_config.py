# -*- coding:utf-8 -*-
__author__ = 'fantasy'

from openerp.osv import fields, osv

class station_solution_config(osv.osv_memory):
    _name = 'station.solution.config'
    _inherit = 'res.config.settings'
    _columns = {
        'local_document_repository': fields.char(
                        'local document Repository Path',
                        size=256,
                        required=True,
                        help='Local mounted path where all your document are stored.'
                    ),
    }

    def get_local_document_repository(self, cr, uid, id=None, context=None):
        #item_id = self.search(cr, uid, [('id','>',0)], count=1)
        #item = self.browse(cr, uid, item_id)
        #if not item:
        #return False
        return "filestore"
        #return item.local_document_repository
        #user = self.pool.get('res.users').browse(cr, uid, uid, context=context)
        #return user.company_id.local_media_repository
station_solution_config()