from odoo import models, fields
from odoo.exceptions import ValidationError
from odoo.tools.translate import _


class QSO(models.Model):
    _name = "ham.award.qso"
    _description = "QSO"

    _inherit = [
        "ham.mixin.qso",
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
        comodel_name="ham.award",
        required=True,
        tracking=True
    )

    operator_id = fields.Many2one(
        string="Operator",
        help="Operator",
        comodel_name="ham.award.operator",
        required=True,
        tracking=True
    )

    upload_id = fields.Many2one(
        string="Upload",
        help="Related upload",
        comodel_name="ham.award.upload",
        tracking=True
    )

    hrdlog_sent = fields.Boolean(
        string="Sent to HRDLog",
        help="Sent to HRDLog",
        required=True,
        default=False,
        readonly=True,
        tracking=True

    )

    hrdlog_ts_sent = fields.Datetime(
        string="Date and Time HRDLog",
        help="Date and Time of upload to HRDLog",
        readonly=True,
        tracking=True
    )

    def action_set_hrdlog_sent(self):
        for rec in self:
            self.set_hrdlog_sent(rec)

    def set_hrdlog_sent(self, qso):
        if not qso:
            raise ValidationError(_("Invalid QSO"))

        qso.write({
            "hrdlog_ts_sent": fields.Datetime.now(),
            "hrdlog_sent": True
        })

    # station_ids = fields.Many2many(
    #     string="Referenced Stations",
    #     help="Referenced Stations",
    #     comodel_name="ham_award.station",
    #     relation="ham_award_qso_station_rel",
    #     column1="qso_id",
    #     column2="station_id",
    #     compute="_compute_station_ids"
    # )

    # @api.depends("callsign")
    # def _compute_station_ids(self):
    #     station_obj = self.env["ham_award.station"]
    #
    #     for rec in self:
    #         if not rec.callsign:
    #             continue
    #
    #         callsign = sorted(re.split(r"([A-Z0-9]+)", rec.callsign.strip().upper()), key=len, reverse=True)[0]
    #
    #         station_ids = station_obj.search([
    #             ("callsign", "ilike", callsign)
    #         ])
    #
    #         rec.station_ids = [(6, 0, station_ids.ids)]
