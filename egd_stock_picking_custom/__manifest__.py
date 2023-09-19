# Copyright 2023 Escodoo
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    "name": "Egd Stock Picking Custom",
    "summary": """
        Customizações no módulo Stock Pincking""",
    "version": "14.0.1.0.0",
    "license": "AGPL-3",
    "author": "Escodoo",
    "website": "https://github.com/Escodoo/egd-addons",
    "depends": [
        "stock_analytic",
        "product_expiry",
        "hr_personal_equipment_request",
    ],
    "data": [
        "views/egd_stock_picking_custom.xml",
        "views/egd_stock_product_lot_custom.xml",
        "report/report_egd_cautela.xml",
        "report/report_egd.xml",
    ],
    "demo": [
        "demo/egd_stock_picking_custom.xml",
    ],
}
