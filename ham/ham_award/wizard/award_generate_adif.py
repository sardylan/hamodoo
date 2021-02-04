from odoo import models, fields, api
from odoo.tools.translate import _

SELECTION_DT_MODE = [
    ("manual", "Manual"),
    ("last_day", "Last Day"),
    ("last_week", "Last Week"),
    ("last_month", "Last Month"),
    ("last_year", "Last Year")
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

    dt_mode = fields.Selection(
        string="Mode",
        help="Interval for QSO extraction",
        selection=SELECTION_DT_MODE,
        required=True,
        default="manual"
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

    @api.onchange("dt_mode")
    def _onchange_dt_mode(self):
        self.ensure_one()

        dt_utility = self.env["ham.utility.dt"]

        if self.dt_mode not in ["manual"]:
            dt_start, dt_end = dt_utility.compute_start_end(self.dt_mode)
            self.dt_start = dt_start
            self.dt_end = dt_end

        self.filename = self._default_filename()

    def _default_filename(self):
        self.ensure_one()

        if not self.award_id:
            return ""

        if not self.callsign_id:
            return ""

        award_generate_adif_utility = self.env["ham.utility.award.generate.adif"]

        suffix = ""

        if self.dt_start and self.dt_end:
            if self.dt_mode == "last_day":
                suffix = f"{_('Day')} {self.dt_start.strftime('%Y-%m-%d')}"
            elif self.dt_mode == "last_week":
                suffix = f"{_('Week')} from {self.dt_start.strftime('%Y-%m-%d')} to {self.dt_end.strftime('%Y-%m-%d')}"
            elif self.dt_mode == "last_month":
                suffix = f"{_('Month')} {self.dt_start.strftime('%Y-%m')}"
            elif self.dt_mode == "last_year":
                suffix = f"{_('Year')} {self.dt_start.strftime('%Y')}"

        filename = award_generate_adif_utility.generate_name(
            award=self.award_id,
            callsign=self.callsign_id,
            dt=self.dt,
            suffix=suffix
        )

        return filename

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
