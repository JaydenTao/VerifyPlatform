# -*- coding: utf-8 -*-
{
    'name': "Web Widget JsonTable ",
    'summary': "Add web JsonTable widget.",
    'author': "Fantasy",
    'website': "http://www.dutufou.com",
    'category': 'web',
    'version': '1.0',
    'depends': [
        'web',
    ],
    'data': [
        'views/web_widget_jsontable_view.xml',
    ],
    'qweb': [
        'static/src/xml/widget.xml',
    ],
    'auto_install':False,
    'installable':True,
    'web_preload':True,
}
