from odoo import models, fields


class NavalStation(models.Model):
    _name = "ham.award.naval.station"
    _description = "Naval station"

    _sql_constraints = [
        # ("callsign_club_id_uniq", "UNIQUE(callsign, club_id)", _("A combination of Callsign and Club already exists."))
    ]

    callsign = fields.Char(
        string="Callsign",
        help="Station Callsign",
        required=True
    )

    club_id = fields.Many2one(
        string="Club",
        help="Naval Club",
        comodel_name="ham.award.naval.club",
        required=True
    )

    reference_number = fields.Char(
        string="Reference number",
        help="Naval Club reference"
    )

    reference = fields.Char(
        string="Reference",
        help="Reference with club tag",
        compute="_compute_reference",
        readonly=True,
        store=True
    )

    coastal_radio_station_points = fields.Integer(
        string="Coastal Radio Station Points",
        help="Station points for the Italian Navy Coastal Radio Station Award",
        default="15"
    )

    def name_get(self):
        return [(rec.id, f"{rec.callsign} - {rec.reference}") for rec in self]

    def _compute_reference(self):
        for rec in self:
            rec.reference = f"{rec.club_id.tag}{rec.reference_number}"
