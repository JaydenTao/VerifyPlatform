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
# from station import station_baseinfo
from openerp import models

class station_solution_involved(osv.Model):
    _name = "station.solution.involved"

    _columns = {
        'Number':fields.integer(string=u'序号'),
        'station_id':fields.many2one('station.baseinfo','方案'),
        'Catalog':fields.char(u'分类',size=512),
        'Standard':fields.char(u'标准值',size=512),
        'Real':fields.char(u'真实值',size=512),
        'Result':fields.char(u'是否合格'),
        'remark':fields.char(u'备注',size=2048)
    }