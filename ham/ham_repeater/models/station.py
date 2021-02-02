from odoo import models, fields


class Station(models.Model):
    _name = "ham.repeater.station"
    _description = "Represent an automated station"

    _inherit = [
        "mail.thread",
        "ham.mixin.station"
    ]

    location_id = fields.Many2one(
        string="Location",
        help="Related Location",
        comodel_name="ham.repeater.location",
        required=True,
        tracking=True
    )

    location_name = fields.Char(related="location_id.name")
    location_latitude = fields.Char(related="location_id.latitude")
    location_longitude = fields.Char(related="location_id.longitude")
    location_locator = fields.Char(related="location_id.locator")

    note = fields.Html(
        string="Note",
        help="Note"
    )
