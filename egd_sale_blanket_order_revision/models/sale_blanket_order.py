# Copyright 2025 - TODAY, Kaynnan Lemes <kaynnan.lemes@escodoo.com.br>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

import logging
import re

from odoo import _, api, fields, models
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)


class SaleBlanketOrder(models.Model):
    _inherit = "sale.blanket.order"

    revision_wizard_ids = fields.One2many(
        comodel_name="sale.blanket.order.revision.wizard",
        inverse_name="old_blanket_order_id",
        string="Revision Wizards",
        help="References to the revision wizards associated with this blanket order.",
    )
    revised_from_id = fields.Many2one(
        comodel_name="sale.blanket.order",
        string="Revised From",
        readonly=True,
        copy=False,
        index=True,
        help="Blanket order this one is a revision of.",
    )
    revision_ids = fields.One2many(
        comodel_name="sale.blanket.order",
        inverse_name="revised_from_id",
        string="Revisions",
        help="Revisions created from this blanket order.",
    )
    revision_count = fields.Integer(
        compute="_compute_revision_count",
        help="Count of revisions associated with this blanket order.",
    )

    all_quotations_invoiced = fields.Boolean(
        compute="_compute_all_quotations_invoiced",
        help="True if all related quotations are invoiced.",
    )

    def _compute_all_quotations_invoiced(self):
        for record in self:
            quotations = record.mapped("line_ids.sale_lines.order_id")
            if quotations:
                record.all_quotations_invoiced = all(
                    q.invoice_status == "invoiced" for q in quotations
                )
            else:
                record.all_quotations_invoiced = False

    @api.depends("revision_ids")
    def _compute_revision_count(self):
        for record in self:
            record.revision_count = len(record.revision_ids)

    def _get_revision_number(self):
        """Return how many revisions separate this blanket order from the
        original one (0 for the original blanket order)."""
        self.ensure_one()
        number = 0
        order = self.revised_from_id
        while order:
            number += 1
            order = order.revised_from_id
        return number

    @api.model
    def _link_revisions_by_name(self):
        """Recover surviving wizard links, then use unambiguous names."""
        wizards = self.env["sale.blanket.order.revision.wizard"].search(
            [
                ("new_blanket_order_id", "!=", False),
                ("old_blanket_order_id", "!=", False),
                ("new_blanket_order_id.revised_from_id", "=", False),
            ]
        )
        wizard_revisions = wizards.mapped("new_blanket_order_id")
        for revision in wizard_revisions:
            originals = wizards.filtered_domain(
                [("new_blanket_order_id", "=", revision.id)]
            ).mapped("old_blanket_order_id")
            if (
                len(originals) == 1
                and originals.company_id == revision.company_id
                and originals.id < revision.id
            ):
                revision.revised_from_id = originals
            else:
                _logger.warning(
                    "Revision %s has conflicting or invalid wizard links; "
                    "manual verification is required",
                    revision.id,
                )
        pattern = re.compile(r"^(?P<base>.*?)\s*\(Rev (?P<number>\d+)\)$")
        revisions = self.search(
            [("name", "like", "(Rev "), ("revised_from_id", "=", False)],
            order="id",
        )
        for revision in revisions:
            if revision in wizard_revisions:
                continue
            match = pattern.match(revision.name)
            if not match:
                continue
            number = int(match.group("number"))
            base = match.group("base")
            previous_name = base if number == 1 else f"{base} (Rev {number - 1})"
            previous = self.search(
                [
                    ("name", "=", previous_name),
                    ("id", "<", revision.id),
                    ("company_id", "=", revision.company_id.id),
                ],
                limit=2,
            )
            if len(previous) == 1:
                revision.revised_from_id = previous
            elif previous:
                _logger.warning(
                    "Revision %s has multiple predecessors named %r in company %s; "
                    "manual verification is required",
                    revision.id,
                    previous_name,
                    revision.company_id.id,
                )

    def action_view_revisions(self):
        """Open a window to view all revisions of the blanket order."""
        self.ensure_one()

        revision_ids = self.revision_ids.ids

        if not revision_ids:
            return {"type": "ir.actions.act_window_close"}

        return {
            "type": "ir.actions.act_window",
            "name": _("Revisions"),
            "res_model": "sale.blanket.order",
            "view_mode": "tree,form",
            "domain": [("id", "in", revision_ids)],
        }

    def set_to_draft(self):
        """Restrict setting the order to draft if there are associated revisions."""
        for record in self:
            if record.revision_ids:
                raise UserError(
                    _(
                        "You cannot set this Blanket Order to Draft because "
                        "it has associated revisions."
                    )
                )
        return super().set_to_draft()
