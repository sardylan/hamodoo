import base64
import datetime

from odoo import models, fields, api
from odoo.exceptions import ValidationError
from odoo.tools.translate import _


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

    @api.depends("uploads")
    def _compute_counts(self):
        qso_obj = self.env["ham.award.qso"]

        for rec in self:
            rec.uploads_count = len(rec.uploads)
            rec.qsos_count = qso_obj.search_count([("award_id", "=", rec.id)])

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

    hrdlog_callsign = fields.Char(
        string="HRDLog Callsign",
        help="Callsign param for HRDLog QSO publish",
        tracking=True
    )

    hrdlog_code = fields.Char(
        string="HRDLog Code",
        help="Code param for HRDLog QSO publish",
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
