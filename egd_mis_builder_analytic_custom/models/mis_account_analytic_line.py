# Copyright 2025 - TODAY, Kaynnan Lemes <kaynnan.lemes@escodoo.com.br>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
# flake8: noqa: B950

from odoo import fields, models, tools


class MisAccountAnalyticLine(models.Model):

    _inherit = "mis.account.analytic.line"

    balance_extra = fields.Float(string="Balance Extra")

    def init(self):
        tools.drop_view_if_exists(self._cr, "mis_account_analytic_line")
        self._cr.execute(
            """
            CREATE OR REPLACE VIEW mis_account_analytic_line AS (
                SELECT
                    aal.id AS id,
                    aal.id AS analytic_line_id,
                    aal.date AS date,
                    aal.general_account_id AS account_id,
                    aal.account_id AS analytic_account_id,
                    aal.company_id AS company_id,
                    'posted'::VARCHAR AS state,
                    -- Credit: amount positivo + total_extra_amount positivo
                    CASE
                        WHEN aal.amount >= 0.0 THEN aal.amount
                        ELSE 0.0
                    END +
                    CASE
                        WHEN aal.total_extra_amount >= 0.0 THEN aal.total_extra_amount
                        ELSE 0.0
                    END AS credit,
                    -- Debit: amount negativo (convertido para positivo) + total_extra_amount negativo (convertido para positivo)
                    CASE
                        WHEN aal.amount < 0 THEN (aal.amount * -1)
                        ELSE 0.0
                    END +
                    CASE
                        WHEN aal.total_extra_amount < 0 THEN (aal.total_extra_amount * -1)
                        ELSE 0.0
                    END AS debit,
                    -- Balance: amount original
                    aal.amount AS balance,
                    -- Balance Extra: total_extra_amount original
                    aal.total_extra_amount AS balance_extra
                FROM
                    account_analytic_line aal
            )"""
        )
