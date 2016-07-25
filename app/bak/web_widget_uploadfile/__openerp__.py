# -*- coding: utf-8 -*-
# © 2016 Cesar Lage (bloopark systems GmbH)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
{
    'name': "Web Custom Widgets ",
    'summary': "Add custom web widgets.",
    'author': "Fantasy",
    'website': "http://www.dutufou.com",
    'category': 'web',
    'version': '1.0',
    'depends': [
        'web',
    ],
    'data': [
        'views/web_widget_uploadfile_view.xml',
    ],
    'qweb': [
        'static/src/xml/widget.xml',
    ],
    'auto_install':False,
    'installable':True,
    'web_preload':True,
}
