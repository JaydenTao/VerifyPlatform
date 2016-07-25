# -*- coding:utf-8 -*-
__author__ = 'fantasy'
from StringIO import StringIO

import xlsxwriter


class MyExcelReport(models.TransientModel):

    _inherit = 'download.file.base.model'
    _name = 'station.solution.file.download'

    def init(self, record_id):
        self.record_id = record_id

    def get_filename(self):
        Model = self.pool.get('station.solution.file')
        Model.read(read(cr, uid, [int(id)], fields, context)[0])
        return 'my_report.xlsx'

    def get_content(self):
        output = StringIO()
        wb = xlsxwriter.Workbook(output)
        sheet = wb.add_worksheet('sheet1')
        # make something
        wb.close()
        output.seek(0)
        return output.read()