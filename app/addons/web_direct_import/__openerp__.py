{
    'name': 'direct import',
    'description': """
    直接导入数据
""",
    'category': 'web',
    'website': 'https://www.dutufou.com',
    'author': 'Fantasy',
    'depends': ['web'],
    'installable': True,
    'auto_install': False,
    'depends': [
        'web',
    ],
    'data': [
        'views/web_direct_import.xml',
    ],
    'qweb': ['static/src/xml/direct_import.xml'],
}
