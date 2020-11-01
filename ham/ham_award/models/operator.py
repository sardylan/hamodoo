from odoo import models, fields, api
from odoo.tools.translate import _


class Operator(models.Model):
    _name = "ham.award.operator"
    _inherit = "mail.thread"
    _description = "Operator"
    _order = "callsign ASC"

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
        help="Callsign of the operator",
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

    # award_ids = fields.Many2many(
    #     string="Awards",
    #     help="Enabled awards",
    #     comodel_name="ham.award",
    #     relation="ham_award_operator_award_rel",
    #     column1="award_id",
    #     column2="operator_id",
    #     tracking=True
    # )

    name = fields.Char(
        related="partner_id.name"
    )

    @api.model
    def create(self, vals):
        vals = self.sanitize_vals(vals)
        return super().create(vals)

    def write(self, vals):
        vals = self.sanitize_vals(vals)
        return super().write(vals)

    def name_get(self):
        result = []

        for rec in self:
            result.append((rec.id, "%s (%s)" % (rec.name, rec.callsign)))

        return result

    @api.onchange("callsign")
    def uppercase_onchange(self):
        callsign_utility = self.env["ham.utility.callsign"]

        for rec in self:
            rec.callsign = callsign_utility.uppercase(rec.callsign)

    @api.model
    def sanitize_vals(self, vals):
        callsign_utility = self.env["ham.utility.callsign"]

        for field in ["callsign"]:
            if field in vals:
                vals[field] = callsign_utility.uppercase(vals[field])

        return vals

    def action_active_toggle(self):
        for rec in self:
            rec.active = not rec.active

        return True
