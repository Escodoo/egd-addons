# Copyright 2024 - TODAY Escodoo
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    "name": "Egd Hr Timesheet Custom",
    "summary": """
        Egd Hr Timesheet Custom""",
    "version": "14.0.1.0.0",
    "license": "AGPL-3",
    "author": "Escodoo",
    "website": "https://github.com/Escodoo/egd-addons",
    "depends": ["hr_timesheet", "account"],
    "data": [
        "security/ir.model.access.csv",
        "views/hr_views.xml",
        "views/hr_overtime_dsr.xml",
        "views/hr_overtime_factor.xml",
        "views/analytic_account_line.xml",
    ],
    "demo": [],
}
