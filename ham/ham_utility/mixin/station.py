from odoo import models, fields
from odoo.tools.translate import _


class Station(models.AbstractModel):
    _name = "ham.mixin.station"
    _inherit = "mail.thread"
    _description = "Abstract Station"
    _rec_name = "callsign"

    _sql_constraints = [
        ("callsign_uniq", "UNIQUE(callsign)", _("Callsign must be unique"))
    ]

    callsign = fields.Char(
        string="Callsign",
        help="Station Callsign",
        required=True,
        index=True,
        tracking=True
    )

    owner_partner_id = fields.Many2one(
        string="Owner",
        help="Owner contact",
        comodel_name="res.partner",
        tracking=True
    )
