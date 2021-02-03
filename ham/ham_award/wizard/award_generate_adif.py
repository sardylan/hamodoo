import datetime

from odoo import models, fields, api

SELECTION_WEBSITE = [
    ("hrdlog", "HRDLog"),
    ("eqsl", "eQSL"),
]


class AwardPublish(models.TransientModel):
    _name = "ham.wizard.award.generate.adif"
    _description = "Wizard for generating ADIF from Award Log"

    award_id = fields.Many2one(
        string="Award",
        help="Related Award",
        comodel_name="ham.award",
        required=True,
        readonly=True
    )

    callsign_id = fields.Many2one(
        string="Callsign",
        help="Select callsign to publish",
        comodel_name="ham.award.callsign",
        required=True
    )

    filename = fields.Char(
        string="Filename",
        help="ADIF Filename",
        required=True
    )

    dt = fields.Datetime(
        string="ADIF Date & Time",
        help="Date & Time saved in ADIF",
        required=True,
        default=lambda self: fields.Datetime.now()
    )

    dt_start = fields.Datetime(
        string="QSO From",
        help="Extract QSO from this datetime"
    )

    dt_end = fields.Datetime(
        string="QSO To",
        help="Extract QSO until this datetime"
    )

    @api.onchange("award_id")
    def onchange_award_id(self):
        return {
            "domain": {
                "callsign_id": [("id", "in", self.award_id.callsigns.ids)]
            }
        }

    @api.onchange("callsign_id")
    def _onchange_callsign_id(self):
        for rec in self:
            rec.filename = self._default_filename()

    def _default_filename(self):
        self.ensure_one()

        if not self.award_id:
            return ""

        if not self.callsign_id:
            return ""

        award_generate_adif_utility = self.env["ham.utility.award.generate.adif"]
        return award_generate_adif_utility.generate_name(
            award=self.award_id,
            callsign=self.callsign_id,
            dt=self.dt
        )

    def action_dt_startend_lastday(self):
        self.ensure_one()

        now = datetime.datetime.utcnow()

    def action_dt_startend_lastweek(self):
        self.ensure_one()

    def action_dt_startend_lastmonth(self):
        self.ensure_one()

    def action_dt_startend_lastyear(self):
        self.ensure_one()

    def action_publish(self):
        self.ensure_one()

        award_generate_adif_utility = self.env["ham.utility.award.generate.adif"]
        award_generate_adif_utility.generate(
            award=self.award_id,
            callsign=self.callsign_id,
            filename=self.filename,
            dt_start=self.dt_start,
            dt_end=self.dt_end,
            dt=self.dt
        )

        return {
            "type": "ir.actions.client",
            "tag": "reload"
        }

