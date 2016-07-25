# -*- coding:utf-8 -*-
__author__ = 'fantasy'

from openerp.osv import fields, osv
from openerp.tools.translate import _
import os
import xlrd
import codecs
import simplejson
import logging
from openerp import SUPERUSER_ID
from openerp import models

class station_solution_budget(osv.Model):
    _inherit = "station.baseinfo"

    def _get_difference(self, cr, uid, ids, name, args, context=None):
        pass

    _columns = {
        'sequence':fields.integer(string=u'序号'),
        # 'station_id':fields.many2one('station.baseinfo','station'),
        'unit_count':fields.float(u'设计院预算'),
        'ai_count':fields.float(u'智能分析预算'),
        'difference':fields.function(_get_difference,type='float',string=u'差额'),
        'unit':fields.char(string=u'设计院预算'),
        'ai':fields.char(string=u'智能分析预算'),
        'diff':fields.char(string=u'对比分析'),
        'remark':fields.char(u'备注',size=1024)
    }

