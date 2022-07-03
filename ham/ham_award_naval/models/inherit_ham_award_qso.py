from odoo import models, fields, api
from odoo.exceptions import ValidationError
from odoo.tools.translate import _


class QSO(models.Model):
    _inherit = "ham.award.qso"

    naval_station_id = fields.Many2one(
        string="Related Naval Station",
        help="Related Naval Station",
        comodel_name="ham.award.naval.station",
        compute="_compute_naval_station_id",
        store=True
    )

    @api.depends("short_callsign")
    def _compute_naval_station_id(self):
        naval_station_obj = self.env["ham.award.naval.station"]

        for rec in self:
            naval_station = naval_station_obj.search([
                ("callsign", "ilike", rec.short_callsign)
            ])

            if len(naval_station) == 1:
                rec.naval_station_id = naval_station
            else:
                rec.naval_station_id = None
