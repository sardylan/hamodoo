from odoo import models, fields, api


class Position(models.AbstractModel):
    _name = "ham.mixin.position"
    _description = "Adds Position and Maidenhead Locator"

    latitude = fields.Float(
        string="Latitude",
        help="Latitude",
        digits=(8, 6)
    )

    longitude = fields.Float(
        string="Longitude",
        help="Longitude",
        digits=(9, 6)
    )

    locator = fields.Char(
        string="Locator",
        help="Maidenhead Locator"
    )

    @api.onchange("latitude", "longitude")
    def _onchange_latitude_longitude(self):
        locator_utility = self.env["ham.utility.locator"]

        for rec in self:
            if not rec.latitude or not rec.longitude:
                continue

            rec.locator = locator_utility.latlng_to_locator(rec.latitude, rec.longitude) or False
