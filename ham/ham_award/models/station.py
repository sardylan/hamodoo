from odoo import models, fields
from odoo.tools.translate import _


class Station(models.Model):
    _name = "ham_award.station"
    _inherit = "mail.thread"
    _description = "Station"
    _order = "name ASC"

    _sql_constraints = [
        ("name_uniq", "UNIQUE(name)", _("Already present. Must be unique")),
    ]

    name = fields.Char(
        string="Name",
        help="Name of the station",
        required=True,
        tracking=True
    )

    active = fields.Boolean(
        string="Active",
        help="Active",
        required=True,
        default=True,
        tracking=True
    )

    def action_active_toggle(self):
        for rec in self:
            rec.active = not rec.active

        return True
