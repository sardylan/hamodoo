import re

from odoo import models, fields, api


class QSO(models.Model):
    _name = "ham_award.qso"
    _description = "QSO"

    _inherit = [
        "ham_utility.qso",
        "mail.thread"
    ]

    active = fields.Boolean(
        string="Enabled",
        help="Enabled",
        required=True,
        default=True
    )

    award_id = fields.Many2one(
        string="Award",
        help="Related award",
        comodel_name="ham_award.award",
        required=True,
        tracking=True
    )

    operator_id = fields.Many2one(
        string="Operator",
        help="Operator",
        comodel_name="ham_award.operator",
        required=True,
        tracking=True
    )

    upload_id = fields.Many2one(
        string="Upload",
        help="Related upload",
        comodel_name="ham_award.upload",
        tracking=True
    )

    station_ids = fields.Many2many(
        string="Referenced Stations",
        help="Referenced Stations",
        comodel_name="ham_award.station",
        relation="ham_award_qso_station_rel",
        column1="qso_id",
        column2="station_id",
        compute="_compute_station_ids"
    )

    @api.model_create_multi
    def create(self, vals):
        return super().create(vals)

    def write(self, vals):
        return super().write(vals)

    @api.depends("callsign")
    def _compute_station_ids(self):
        station_obj = self.env["ham_award.station"]

        for rec in self:
            if not rec.callsign:
                continue

            callsign = sorted(re.split(r"([A-Z0-9]+)", rec.callsign.strip().upper()), key=len, reverse=True)[0]

            station_ids = station_obj.search([
                ("callsign", "ilike", callsign)
            ])

            rec.station_ids = [(6, 0, station_ids.ids)]
