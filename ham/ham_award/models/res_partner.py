from odoo import models, fields


class ResPartner(models.Model):
    _inherit = "res.partner"

    callsign = fields.Char(
        string="Callsign",
        help="Operator callsign",
        required=True,
        tracking=True
    )
