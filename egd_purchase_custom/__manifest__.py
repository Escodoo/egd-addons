# Copyright 2023 - TODAY, Escodoo
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    "name": "EGD Purchase Custom",
    "summary": """
        EGD Purchase Custom""",
    "version": "14.0.1.0.0",
    "license": "AGPL-3",
    "author": "Escodoo",
    "website": "https://github.com/Escodoo/egd-addons",
    "depends": [
        "purchase",
        "egd_sale_blanket_order_custom",
        "stock_request_analytic",
        "stock_request_purchase_request",
    ],
    "data": [
        "views/purchase_order_line.xml",
        "views/purchase_order.xml",
    ],
}
