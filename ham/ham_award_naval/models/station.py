from odoo import models, fields
from odoo.tools.translate import _


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

    reference = fields.Char(
        string="Reference",
        help="Naval Club reference"
    )
