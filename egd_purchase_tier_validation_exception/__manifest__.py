# Copyright 2026 - TODAY, Cristiano Mafra Junior <cristiano.mafra@escodoo.com.br>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    "name": "EGD Purchase Tier Validation Exception",
    "summary": """
        Allow editing Received Quantity on Purchase Order lines already
        under Tier Validation, keeping all other fields locked""",
    "version": "16.0.1.0.0",
    "license": "AGPL-3",
    "author": "Escodoo",
    "website": "https://github.com/Escodoo/egd-addons",
    "depends": [
        "purchase_tier_validation",
        "l10n_br_purchase",
    ],
    "data": [
        "data/tier_validation_exception_data.xml",
        "views/purchase_order_view.xml",
    ],
}
