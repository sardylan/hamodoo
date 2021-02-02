from odoo import models, fields
from odoo.tools.translate import _


class Location(models.Model):
    _name = "ham.repeater.location"
    _description = "Represents a location in which a repeater is installed"

    _inherit = [
        "mail.thread",
        "ham.mixin.position"
    ]

    _sql_constraints = [
        ("name_uniq", "UNIQUE(name)",
         _("Another location with the same name already exists, location names must be unique"))
    ]

    name = fields.Char(
        string="Name",
        help="Location name",
        required=True,
        tracking=True
    )

    partner_id = fields.Many2one(
        string="Contact",
        help="Reference Contact",
        comodel_name="res.partner",
        tracking=True
    )

    note = fields.Html(
        string="Note",
        help="Note"
    )
