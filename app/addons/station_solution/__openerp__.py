# -*- coding:utf-8 -*-


{
    'name' : 'Station Solution Management',
    'version' : '0.1',
    'author' : 'Fantasy',
    'sequence': 10,
    'category': 'Managing mobile station',
    'website' : 'https://dutufou.com',
    'summary' : 'station',
    'description' : """

With this module, System helps you managing all your phone station.

""",
    'depends' : [
        'base',
        'station'
    ],
    'data' : [
        'views/station_solution_view.xml'
    ],

    'installable' : True,
    'application' : True,
}
