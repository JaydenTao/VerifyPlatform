# -*- coding: utf-8 -*-
import csv
import itertools
import logging
import operator
import xlrd

try:
    from cStringIO import StringIO
except ImportError:
    from StringIO import StringIO

import psycopg2
from openerp.osv import orm, fields
from openerp.tools.translate import _
from openerp import models

FIELDS_RECURSION_LIMIT = 2
ERROR_PREVIEW_BYTES = 200
_logger = logging.getLogger(__name__)


class direct_import(orm.TransientModel):
    _name = 'direct.import'
    # allow imports to survive for 12h in case user is slow
    _transient_max_hours = 12.0

    _columns = {
        'res_model': fields.char('Model'),
        'file': fields.binary(
            'File', help="File to check and/or import, raw binary (not base64)"),
        'file_name': fields.char('File Name'),
        'file_type': fields.char('File Type'),
        'save_type': fields.char('save type'),
    }

    def get_fields(self, cr, uid, model, context=None,
                   depth=FIELDS_RECURSION_LIMIT):
        """ Recursively get fields for the provided model (through
        fields_get) and filter them according to importability

        The output format is a list of ``Field``, with ``Field``
        defined as:

        .. class:: Field

            .. attribute:: id (str)

                A non-unique identifier for the field, used to compute
                the span of the ``required`` attribute: if multiple
                ``required`` fields have the same id, only one of them
                is necessary.

            .. attribute:: name (str)

                The field's logical (Odoo) name within the scope of
                its parent.

            .. attribute:: string (str)

                The field's human-readable name (``@string``)

            .. attribute:: required (bool)

                Whether the field is marked as required in the
                model. Clients must provide non-empty import values
                for all required fields or the import will error out.

            .. attribute:: fields (list(Field))

                The current field's subfields. The database and
                external identifiers for m2o and m2m fields; a
                filtered and transformed fields_get for o2m fields (to
                a variable depth defined by ``depth``).

                Fields with no sub-fields will have an empty list of
                sub-fields.

        :param str model: name of the model to get fields form
        :param int landing: depth of recursion into o2m fields
        """
        model_obj = self.pool[model]
        fields = [{
            'id': 'id',
            'name': 'id',
            'string': _("External ID"),
            'required': False,
            'fields': [],
        }]
        fields_got = model_obj.fields_get(cr, uid, context=context)
        blacklist = orm.MAGIC_COLUMNS + [model_obj.CONCURRENCY_CHECK_FIELD]
        for name, field in fields_got.iteritems():
            if name in blacklist:
                continue
            # an empty string means the field is deprecated, @deprecated must
            # be absent or False to mean not-deprecated
            if field.get('deprecated', False) is not False:
                continue
            if field.get('readonly'):
                states = field.get('states')
                if not states:
                    continue
                # states = {state: [(attr, value), (attr2, value2)], state2:...}
                if not any(attr == 'readonly' and value is False
                           for attr, value in itertools.chain.from_iterable(
                    states.itervalues())):
                    continue

            f = {
                'id': name,
                'name': name,
                'string': field['string'],
                # Y U NO ALWAYS HAS REQUIRED
                'required': bool(field.get('required')),
                'fields': [],
            }

            if field['type'] in ('many2many', 'many2one'):
                f['fields'] = [
                    dict(f, name='id', string=_("External ID")),
                    dict(f, name='.id', string=_("Database ID")),
                ]
            elif field['type'] == 'one2many' and depth:
                f['fields'] = self.get_fields(
                    cr, uid, field['relation'], context=context, depth=depth - 1)
                if self.pool['res.users'].has_group(cr, uid, 'base.group_no_one'):
                    f['fields'].append(
                        {'id': '.id', 'name': '.id', 'string': _("Database ID"), 'required': False, 'fields': []})

            fields.append(f)

        # TODO: cache on model?
        return fields

    def _read_json(self, json):
        pass

    def _read_xls(self, record, fields):
        try:
            data = xlrd.open_workbook(file_contents=record.file)
            sheet = data.sheet_by_index(0)

            nrows = sheet.nrows
            ncols = sheet.ncols
            header = sheet.row_values(0)
            match_header = self._match_fields(header, fields)

            if len(match_header) == len(header):
                list = []
                for rowx in range(1, nrows):
                    row = sheet.row_values(rowx)
                    if row:
                        app = []
                        for colx in range(ncols):
                            app.append(row[colx])
                            # app[match_header[colx]] = row[colx]
                        app.append(u'station_baseinfo_8')
                        list.append(tuple(app))
                # header_list = []
                # for colx in range(ncols):
                #     header_list.append(header[colx])
                match_header.append('station_id/id')
                return list, match_header
            return None, None



        except Exception, e:
            # Due to lazy generators, UnicodeDecodeError (for
            # instance) may only be raised when serializing the
            # preview to a list in the return.
            _logger.debug("Error during XML parsing preview", exc_info=True)
            return {
                'error': str(e),
                # iso-8859-1 ensures decoding will always succeed,
                # even if it yields non-printable characters. This is
                # in case of UnicodeDecodeError (or csv.Error
                # compounded with UnicodeDecodeError)
                'preview': record.file[:ERROR_PREVIEW_BYTES]
                    .decode('iso-8859-1'),
            }

    def do_it(self, cr, uid, id, context=None):
        cr.execute('SAVEPOINT import')
        # try:
        # data,import_fields = self._convert_import_data(record,fields,options,context=context)
        (record,) = self.browse(cr, uid, [id], context=context)
        fields = self.get_fields(cr, uid, record.res_model, context=context)
        try:
            rows, import_fields = self._read_xls(record, fields)
        except ValueError, e:
            return [
                {
                    'type': 'error',
                    'message': unicode(e),
                    'record': False
                }
            ]
        _logger.info('importing %d rows...', len(rows))
        import_result = self.pool[record.res_model].load(
            cr, uid, import_fields, rows, context=context)
        _logger.info('done')

        try:
            cr.execute('RELEASE SAVEPOINT import')
        except psycopg2.InternalError:
            pass

        return import_result

    def do_it_json(self, cr, uid, id, json_data, context=None):
        cr.execute('SAVEPOINT import')
        (record,) = self.browse(cr, uid, [id], context=context)
        fields = self.get_fields(cr, uid, record.res_model, context=context)
        rows,import_fields = self.parse_json(json_data, fields)

        import_result = self.pool[record.res_model].load(
            cr, uid, import_fields, rows, context=context
        )
        _logger.info('done')
        try:
            cr.execute('RELEASE SAVEPOINT import')
        except psycopg2.InternalError:
            pass

        return import_result


    def parse_json(self,json_data, fields):
        row = json_data[0]
        match_fields = []
        list = []
        for field in fields:
            if (row.has_key(field.get('name',None))):
                match_fields.append(field.get('name',None))

        for row in json_data:
            app = []
            for field in match_fields:
                app.append(row.get(field,None))
            list.append(tuple(app))

        return list,match_fields
        # for title in row

    def _read_csv(self, record, options):
        """ Returns a CSV-parsed iterator of all empty lines in the file

        :throws csv.Error: if an error is detected during CSV parsing
        :throws UnicodeDecodeError: if ``options.encoding`` is incorrect
        """
        csv_iterator = csv.reader(
            StringIO(record.file),
            quotechar=str(options['quoting']),
            delimiter=str(options['separator']))

        def nonempty(row):
            return any(x for x in row if x.strip())

        csv_nonempty = itertools.ifilter(nonempty, csv_iterator)
        # TODO: guess encoding with chardet? Or https://github.com/aadsm/jschardet
        encoding = options.get('encoding', 'utf-8')
        return itertools.imap(
            lambda row: [item.decode(encoding) for item in row],
            csv_nonempty)

    def _match_fields(self, header, fields):

        valid = True
        match_header = []
        for title in header:
            for item in fields:
                if title == item.get('string', None):
                    match_header.append(item.get('name', None))

        return match_header

    def _match_header(self, header, fields, options):
        """ Attempts to match a given header to a field of the
        imported model.

        :param str header: header name from the CSV file
        :param fields:
        :param dict options:
        :returns: an empty list if the header couldn't be matched, or
                  all the fields to traverse
        :rtype: list(Field)
        """
        string_match = None
        for field in fields:
            # FIXME: should match all translations & original
            # TODO: use string distance (levenshtein? hamming?)
            if header.lower() == field['name'].lower():
                return [field]
            if header.lower() == field['string'].lower():
                # matching string are not reliable way because
                # strings have no unique constraint
                string_match = field
        if string_match:
            # this behavior is only applied if there is no matching field['name']
            return [string_match]

        if '/' not in header:
            return []

        # relational field path
        traversal = []
        subfields = fields
        # Iteratively dive into fields tree
        for section in header.split('/'):
            # Strip section in case spaces are added around '/' for
            # readability of paths
            match = self._match_header(section.strip(), subfields, options)
            # Any match failure, exit
            if not match: return []
            # prep subfields for next iteration within match[0]
            field = match[0]
            subfields = field['fields']
            traversal.append(field)
        return traversal

    def _match_headers(self, rows, fields, options):
        """ Attempts to match the imported model's fields to the
        titles of the parsed CSV file, if the file is supposed to have
        headers.

        Will consume the first line of the ``rows`` iterator.

        Returns a pair of (None, None) if headers were not requested
        or the list of headers and a dict mapping cell indices
        to key paths in the ``fields`` tree

        :param Iterator rows:
        :param dict fields:
        :param dict options:
        :rtype: (None, None) | (list(str), dict(int: list(str)))
        """
        if not options.get('headers'):
            return None, None

        headers = next(rows)
        return headers, dict(
            (index, [field['name'] for field in self._match_header(header, fields, options)] or None)
            for index, header in enumerate(headers)
        )

    def parse_preview(self, cr, uid, id, options, count=10, context=None):
        """ Generates a preview of the uploaded files, and performs
        fields-matching between the import's file data and the model's
        columns.

        If the headers are not requested (not options.headers),
        ``matches`` and ``headers`` are both ``False``.

        :param id: identifier of the import
        :param int count: number of preview lines to generate
        :param options: format-specific options.
                        CSV: {encoding, quoting, separator, headers}
        :type options: {str, str, str, bool}
        :returns: {fields, matches, headers, preview} | {error, preview}
        :rtype: {dict(str: dict(...)), dict(int, list(str)), list(str), list(list(str))} | {str, str}
        """
        (record,) = self.browse(cr, uid, [id], context=context)
        fields = self.get_fields(cr, uid, record.res_model, context=context)

        try:
            rows = self._read_csv(record, options)

            headers, matches = self._match_headers(rows, fields, options)
            # Match should have consumed the first row (iif headers), get
            # the ``count`` next rows for preview
            preview = list(itertools.islice(rows, count))
            assert preview, "CSV file seems to have no content"
            return {
                'fields': fields,
                'matches': matches or False,
                'headers': headers or False,
                'preview': preview,
            }
        except Exception, e:
            # Due to lazy generators, UnicodeDecodeError (for
            # instance) may only be raised when serializing the
            # preview to a list in the return.
            _logger.debug("Error during CSV parsing preview", exc_info=True)
            return {
                'error': str(e),
                # iso-8859-1 ensures decoding will always succeed,
                # even if it yields non-printable characters. This is
                # in case of UnicodeDecodeError (or csv.Error
                # compounded with UnicodeDecodeError)
                'preview': record.file[:ERROR_PREVIEW_BYTES]
                    .decode('iso-8859-1'),
            }

    def _convert_import_data(self, record, fields, options, context=None):
        # Get indices for non-empty fields
        indices = [index for index, field in enumerate(fields) if field]
        if not indices:
            raise ValueError(_("You must configure at least one field to import"))
        # If only one index, itemgetter will return an atom rather
        # than a 1-tuple
        if len(indices) == 1:
            mapper = lambda row: [row[indices[0]]]
        else:
            mapper = operator.itemgetter(*indices)
        # Get only list of actually imported fields
        import_fields = filter(None, fields)

        rows_to_import = self._read_csv(record, options)
        if options.get('headers'):
            rows_to_import = itertools.islice(
                rows_to_import, 1, None)
        data = [
            row for row in itertools.imap(mapper, rows_to_import)
            # don't try inserting completely empty rows (e.g. from
            # filtering out o2m fields)
            if any(row)
            ]

        return data, import_fields

    def do(self, cr, uid, id, fields, options, dryrun=False, context=None):
        """ Actual execution of the import

        :param fields: import mapping: maps each column to a field,
                       ``False`` for the columns to ignore
        :type fields: list(str|bool)
        :param dict options:
        :param bool dryrun: performs all import operations (and
                            validations) but rollbacks writes, allows
                            getting as much errors as possible without
                            the risk of clobbering the database.
        :returns: A list of errors. If the list is empty the import
                  executed fully and correctly. If the list is
                  non-empty it contains dicts with 3 keys ``type`` the
                  type of error (``error|warning``); ``message`` the
                  error message associated with the error (a string)
                  and ``record`` the data which failed to import (or
                  ``false`` if that data isn't available or provided)
        :rtype: list({type, message, record})
        """
        cr.execute('SAVEPOINT import')

        (record,) = self.browse(cr, uid, [id], context=context)
        try:
            data, import_fields = self._convert_import_data(
                record, fields, options, context=context)
        except ValueError, e:
            return [{
                'type': 'error',
                'message': unicode(e),
                'record': False,
            }]

        _logger.info('importing %d rows...', len(data))
        import_result = self.pool[record.res_model].load(
            cr, uid, import_fields, data, context=context)
        _logger.info('done')

        # If transaction aborted, RELEASE SAVEPOINT is going to raise
        # an InternalError (ROLLBACK should work, maybe). Ignore that.
        # TODO: to handle multiple errors, create savepoint around
        #       write and release it in case of write error (after
        #       adding error to errors array) => can keep on trying to
        #       import stuff, and rollback at the end if there is any
        #       error in the results.
        try:
            if dryrun:
                cr.execute('ROLLBACK TO SAVEPOINT import')
            else:
                cr.execute('RELEASE SAVEPOINT import')
        except psycopg2.InternalError:
            pass

        return import_result['messages']


class save_file_base_model(models.AbstractModel):
    _name = 'save.file.base.model'

    record_id = None
    parent_id = None

    def init(self, record_id):
        self.record_id = record_id

    # def init(self, parent_id,file_name,file_content):
    #     self.parent_id = parent_id

    def save_file(self, import_id, parent_id, file_name, file_content):
        raise NotImplementedError

        # def get_filename(self):
        #     raise NotImplementedError
        #
        # def get_content(self):
        #     raise NotImplementedError
