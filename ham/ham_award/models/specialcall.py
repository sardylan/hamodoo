from odoo import models, fields, api


class Specialcall(models.Model):
    _name = "ham_award.specialcall"
    _inherit = "mail.thread"
    _description = "Special Callsign"
    _order = "award_id DESC, callsign"

    award_id = fields.Many2one(
        string="Award",
        help="Award reference",
        comodel_name="ham_award.award",
        required=True,
        tracking=True
    )

    callsign = fields.Char(
        string="Callsgin",
        help="Callsign",
        required=True,
        tracking=True
    )

    reference = fields.Char(
        string="Reference",
        help="Reference",
        tracking=True
    )

    description = fields.Char(
        string="Description",
        help="Description",
        tracking=True
    )

    points = fields.Integer(
        string="Points",
        help="Points",
        required=True,
        default=0,
        tracking=True
    )

    name = fields.Char(
        string="Name",
        help="Name",
        readonly=True,
        compute="_compute_name"
    )

    @api.depends("callsign", "description", "reference")
    def _compute_name(self):
        for rec in self:
            items = [rec.callsign]

            if rec.description:
                items.append(rec.description)

            if rec.reference:
                items.append(rec.reference)

            rec.name = " - ".join(items)
