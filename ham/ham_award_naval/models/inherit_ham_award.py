from odoo import models, fields, api


class Award(models.Model):
    _inherit = "ham.award"

    coastal_jolly = fields.Many2one(
        string="Jolly Station",
        help="Jolly Station",
        comodel_name="ham.award.naval.station"
    )

    coastal_station_ids = fields.Many2many(
        string="Active Station",
        help="Active Station",
        comodel_name="ham.award.naval.station",
        relation="ham_award_naval_station_coastal_rel",
        column1="award_id",
        column2="station_id"
    )
