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

    naval_reference = fields.Char(
        related="naval_station_id.reference"
    )

    coastal_radio_station_points = fields.Integer(
        related="naval_station_id.coastal_radio_station_points"
    )

    points = fields.Integer(
        string="Points",
        help="Points",
        compute="action_calculate_points",
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

    def action_calculate_points(self):
        for rec in self:
            self.calculate_points(rec)

    @api.model
    def calculate_points(self, qso=None):
        if not qso:
            raise ValidationError(_("Invalid QSO record"))

        point_fields: list = [
            qso.naval_station_id.coastal_radio_station_points
        ]

        points: int = 0
        for field in point_fields:
            points += field

        dupe_qsos = self.search(
            args=[
                ("award_id", "=", qso.award_id.id),
                ("callsign", "=", qso.callsign),
                ("count_as", "=", qso.count_as),
                ("ts_start", ">=", qso.ts_start.replace(hour=0, minute=0, second=0)),
                ("ts_start", "<=", qso.ts_start.replace(hour=23, minute=59, second=59)),
            ],
            order="ts_start"
        )

        if len(dupe_qsos) < 1:
            raise ValidationError(_("Error searching same-day QSOs"))

        if qso.id == dupe_qsos[0].id:
            qso.points = points
