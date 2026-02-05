{
    'name': 'App One',
    'version': '19.0.1.0',
    'summary': 'This is a test module',
    'description': 'Module to test basic functionality in Odoo',
    'category': 'Custom',
    'author': 'Your Name',
    'depends': ['base','web','product','stock'],
    'data': [
        'security/ir.model.access.csv',
        'security/internal_request.xml',
        'views/internal_request_view.xml',
    ],
    'installable': True,
    'application': True,
    'license': 'LGPL-3',
}
