from odoo import models, fields
from odoo.tools.translate import _


class Station(models.Model):
    _name = "ham_award.station"
    _inherit = "mail.thread"
    _description = "Station"

    _sql_constraints = [
        ("partner_id_uniq", "UNIQUE(partner_id)", _("Already present. Must be unique"))
    ]

    partner_id = fields.Many2one(
        string="Contact",
        help="Related contact",
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

    name = fields.Char(
        related="partner_id.name"
    )
