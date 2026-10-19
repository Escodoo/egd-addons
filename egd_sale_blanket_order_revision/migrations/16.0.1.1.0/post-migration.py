# Copyright 2026 - TODAY, Wesley Oliveira <wesley.oliveira@escodoo.com.br>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

import logging

from odoo import SUPERUSER_ID, api

_logger = logging.getLogger(__name__)


def migrate(cr, version):
    """Link the existing revisions to the blanket order they come from.

    The link used to be kept only on the (transient) revision wizard, already
    removed by the vacuum cleaner: rebuild it from the "<name> (Rev N)" names.
    """
    env = api.Environment(cr, SUPERUSER_ID, {})
    env["sale.blanket.order"].with_context(active_test=False)._link_revisions_by_name()
    _logger.info("Revisions of the blanket orders linked by name")
