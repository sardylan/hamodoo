import base64
import datetime

from odoo import models, fields, api
from odoo.exceptions import ValidationError
from odoo.tools.translate import _

SELECTION_STATE = [
    ("scheduled", "Scheduled"),
    ("running", "Running"),
    ("completed", "Completed"),
    ("closed", "Closed")
]


class Award(models.Model):
    _name = "ham.award"
    _inherit = "mail.thread"
    _description = "Award"
    _order = "ts_start DESC"

    _sql_constraints = [
        ("name_uniq", "UNIQUE(name)", _("Already present. Must be unique"))
    ]

    name = fields.Char(
        string="Name",
        help="Name of the award",
        required=True,
        tracking=True
    )

    callsigns = fields.One2many(
        string="Callsigns",
        help="Callsigns used by all stations in the award",
        comodel_name="ham.award.callsign",
        inverse_name="award_id",
        required=True,
        tracking=True
    )

    ts_start = fields.Datetime(
        string="Date & Time Start",
        help="Date and Time of start",
        required=True,
        tracking=True
    )

    ts_end = fields.Datetime(
        string="Date & Time End",
        help="Date and Time of end",
        required=True,
        tracking=True
    )

    ts_upload_start = fields.Datetime(
        string="Upload Start",
        help="Start Date and Time of the interval in which ADIF uploading is permitted",
        tracking=True
    )

    ts_upload_end = fields.Datetime(
        string="Upload End",
        help="End Date and Time of the interval in which ADIF uploading is permitted",
        tracking=True
    )

    operator_ids = fields.Many2many(
        string="Operators",
        help="Enabled operators",
        comodel_name="ham.award.operator",
        relation="ham_award_operator_rel",
        column1="operator_id",
        column2="award_id",
        tracking=True
    )

    public = fields.Boolean(
        string="Public",
        help="Enable visibility on public site",
        required=True,
        default=True,
        tracking=True
    )

    uploads = fields.One2many(
        string="Uploads",
        help="Log uploads by operators",
        comodel_name="ham.award.upload",
        inverse_name="award_id",
        readonly=True
    )

    adif_id = fields.Many2one(
        string="ADIF",
        help="Generated ADIF",
        comodel_name="ir.attachment",
        readonly=True
    )

    uploads_count = fields.Integer(
        string="Uploads count",
        help="Uploads count",
        readonly=True,
        compute="_compute_counts"
    )

    qsos_count = fields.Integer(
        string="QSOs count",
        help="QSOs count",
        readonly=True,
        compute="_compute_counts"
    )

    state = fields.Selection(
        string="State",
        help="Award state",
        selection=SELECTION_STATE,
        readonly=True,
        compute="_compute_state"
    )

    @api.constrains("ts_start", "ts_end", "ts_upload_start", "ts_upload_end")
    def _constrain_ts_fields(self):
        for rec in self:
            if rec.ts_upload_start and rec.ts_upload_start < rec.ts_start:
                raise ValidationError(_("Upload Start datetime must be equal or after Award Start datetime"))
            if rec.ts_upload_end and rec.ts_upload_end < rec.ts_end:
                raise ValidationError(_("Upload End datetime must be equal or after Award End datetime"))

    @api.depends("uploads")
    def _compute_counts(self):
        qso_obj = self.env["ham.award.qso"]

        for rec in self:
            rec.uploads_count = len(rec.uploads)
            rec.qsos_count = qso_obj.search_count([("award_id", "=", rec.id)])

    @api.depends()
    def _compute_state(self):
        now = fields.Datetime.now()

        for rec in self:
            ts_upload_end = rec.ts_upload_end and rec.ts_upload_end or rec.ts_end

            if now < rec.ts_start:
                rec.state = "scheduled"
            elif now < rec.ts_end:
                rec.state = "running"
            elif now < ts_upload_end:
                rec.state = "completed"
            else:
                rec.state = "closed"

    # TODO: Deprecated
    def action_produce_adif(self):
        for rec in self:
            self.produce_adif(rec)

        return {
            "type": "ir.actions.client",
            "tag": "reload"
        }

    def action_publish(self):
        self.ensure_one()

        return {
            "type": "ir.actions.act_window",
            "name": _("Award QSOs Publish"),
            "res_model": "ham.wizard.award.publish",
            "view_mode": "form",
            "target": "new",
            "context": {
                "default_award_id": self.id
            }
        }

    def action_generate_adif(self):
        self.ensure_one()

        return {
            "type": "ir.actions.act_window",
            "name": _("Generate Award ADIF"),
            "res_model": "ham.wizard.award.generate.adif",
            "view_mode": "form",
            "target": "new",
            "context": {
                "default_award_id": self.id
            }
        }

    def action_show_uploads(self):
        self.ensure_one()

        action = self.env.ref("ham_award.action_upload_list")
        result = action.read()[0]

        result["domain"] = [("award_id", "=", self.id)]

        return result

    def action_show_qsos(self):
        self.ensure_one()

        action = self.env.ref("ham_award.action_qso_list")
        result = action.read()[0]

        result["domain"] = [("award_id", "=", self.id)]

        return result

    def is_upload_permitted(self) -> bool:
        self.ensure_one()

        upload_interval_start = self.ts_start
        upload_interval_end = self.ts_end

        if self.ts_upload_start:
            upload_interval_start = self.ts_upload_start
        if self.ts_upload_end:
            upload_interval_end = self.ts_upload_end

        now = datetime.datetime.utcnow()
        return bool(upload_interval_start <= now <= upload_interval_end)

    @api.model
    def produce_adif(self, award):
        if not award:
            raise ValidationError(_("Award not valid"))

        ir_attachment_obj = self.env["ir.attachment"]
        qso_obj = self.env["ham.award.qso"]

        adif_utility = self.env["ham.utility.adif"]

        qsos = qso_obj.search([
            ("award_id", "=", award.id),
            ("active", "=", True)
        ])

        adif_content = adif_utility.generate_adif(qsos)

        name = "%s %s.adi" % (
            datetime.datetime.now().strftime("%Y%m%d-%H%M%S"),
            award.name
        )

        award.adif_id.unlink()

        award.adif_id = ir_attachment_obj.create({
            "res_model": award._name,
            "res_id": award.id,
            "type": "binary",
            "name": name,
            "store_fname": name,
            "mimetype": "application/text",
            "datas": base64.b64encode(adif_content.encode()),
        })

        if not award.adif_id:
            raise ValidationError(_("Unable to create attachment"))


class AwardCallsign(models.Model):
    _name = "ham.award.callsign"
    _inherit = "mail.thread"
    _description = "Award Callsign"
    _order = "callsign"
    _rec_name = "callsign"

    _sql_constraints = [
        ("award_callsign_uniq", "UNIQUE(award_id, callsign)", _("Callsign already exists in award"))
    ]

    award_id = fields.Many2one(
        string="Award",
        help="Related Award",
        comodel_name="ham.award",
        required=True
    )

    callsign = fields.Char(
        string="Callsign",
        help="Callsign",
        required=True,
        tracking=True
    )

    eqsl_enabled = fields.Boolean(
        string="eQSL",
        help="Enable publishing on eQSL",
        tracking=True
    )

    eqsl_username = fields.Char(
        string="eQSL Username",
        help="Username for eQSL QSO publish",
        tracking=True
    )

    eqsl_password = fields.Char(
        string="eQSL Password",
        help="Password for eQSL QSO publish",
        tracking=True
    )

    hrdlog_enabled = fields.Boolean(
        string="HRDLog",
        help="Enable publishing on HRDLog",
        tracking=True
    )

    hrdlog_callsign = fields.Char(
        string="HRDLog Callsign",
        help="Callsign for HRDLog QSO publish",
        tracking=True
    )

    hrdlog_code = fields.Char(
        string="HRDLog Code",
        help="Code for HRDLog QSO publish",
        tracking=True
    )

    hamqth_enabled = fields.Boolean(
        string="HamQTH",
        help="Enable publishing on HamQTH",
        tracking=True
    )

    hamqth_username = fields.Char(
        string="HamQTH Username",
        help="Username for HamQTH QSO publish",
        tracking=True
    )

    hamqth_password = fields.Char(
        string="HamQTH Password",
        help="Password for HamQTH QSO publish",
        tracking=True
    )

    hamqth_callsign = fields.Char(
        string="HamQTH Callsign",
        help="Callsign for HamQTH QSO publish",
        tracking=True
    )

    @api.model
    def create(self, vals):
        vals = self.sanitize_vals(vals)
        return super().create(vals)

    def write(self, vals):
        vals = self.sanitize_vals(vals)
        return super().write(vals)

    @api.model
    def sanitize_vals(self, vals):
        callsign_utility = self.env["ham.utility.callsign"]

        for field in ["callsign"]:
            if field in vals:
                vals[field] = callsign_utility.uppercase(vals[field])

        return vals
