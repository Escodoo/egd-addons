# Copyright 2023 - TODAY, Escodoo
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    "name": "Egd Stock Picking Custom",
    "summary": """
        EGD Stock Picking Custom""",
    "version": "14.0.1.0.0",
    "license": "AGPL-3",
    "author": "Escodoo",
    "website": "https://github.com/Escodoo/egd-addons",
    "depends": [
        "product_expiry",
        "stock_analytic",
        "hr_employee_ppe",
    ],
    "data": [
        "views/stock_procuction_lot.xml",
        "views/stock_picking.xml",
        "views/egd_report_views.xml",
        "views/egd_report_custody.xml",
    ],
    "demo": [],
}
