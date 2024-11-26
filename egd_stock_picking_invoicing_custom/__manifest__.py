# Copyright 2024 - TODAY, Escodoo
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    "name": "EGD Stock Picking Invoicing Custom",
    "summary": """
        EGD Stock Picking Invoicing Custom""",
    "version": "14.0.1.0.0",
    "license": "AGPL-3",
    "author": "Escodoo",
    "website": "https://github.com/Escodoo/egd-addons",
    "depends": ["stock_picking_invoicing"],
    "data": [
        "views/account_move.xml",
        "views/sale_order.xml",
        "wizards/stock_invoice_onshipping.xml",
    ],
}
