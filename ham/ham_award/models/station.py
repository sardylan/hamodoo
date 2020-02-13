from odoo import models, fields, api
from odoo.tools.translate import _


class Station(models.Model):
    _name = "ham_award.station"
    _inherit = "mail.thread"
    _description = "Station"
    _order = "name ASC"

    _sql_constraints = [
        ("partner_id_uniq", "UNIQUE(partner_id)", _("Already present. Must be unique")),
        ("callsign_uniq", "UNIQUE(callsign)", _("Callsign already present. Must be unique"))
    ]

    partner_id = fields.Many2one(
        string="Contact",
        help="Related contact",
        comodel_name="res.partner",
        required=True,
        tracking=True
    )

    callsign = fields.Char(
        string="Callsign",
        help="Callsign of the station",
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

    def create(self, vals):
        vals = self.sanitize_vals(vals)
        return super().create(vals)

    def write(self, vals):
        vals = self.sanitize_vals(vals)
        return super().write(vals)

    @api.onchange("callsign")
    def uppercase_onchange(self):
        callsign_utility = self.env["ham_utility.utility_callsign"]

        for rec in self:
            rec.callsign = callsign_utility.uppercase(rec.callsign)

    @api.model
    def sanitize_vals(self, vals):
        callsign_utility = self.env["ham_utility.utility_callsign"]

        for field in ["callsign"]:
            if field in vals:
                vals[field] = callsign_utility.uppercase(vals[field])

        return vals
