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

    callsigns = fields.Many2many(
        string="Callsigns",
        help="Callsigns used by all stations in the award",
        comodel_name="ham.award.callsign",
        column1="award_id",
        column2="callsign_id",
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

    def action_produce_adif(self):
        for rec in self:
            self.produce_adif(rec)

        return {
            "type": "ir.actions.client",
            "tag": "reload"
        }

    @api.model
    def produce_adif(self, award):
        if not award:
            raise ValidationError(_("Award not valid"))

        ir_attachment_obj = self.env["ir.attachment"]
        qso_obj = self.env["ham.award.qso"]

        adif_utility = self.env["ham.utility.adif"]

        qso_ids = qso_obj.search([
            ("award_id", "=", award.id),
            ("active", "=", True)
        ])

        adif_content = adif_utility.generate_adif(qso_ids)

        name = "%s %s.adi" % (
            datetime.datetime.now().strftime("%Y%m%d-%H%M%S"),
            award.name
        )

        ir_attachment_id = ir_attachment_obj.create({
            "res_model": award._name,
            "res_id": award.id,
            "type": "binary",
            "name": name,
            "store_fname": name,
            "mimetype": "application/text",
            "datas": base64.b64encode(adif_content.encode()),
        })

        if not ir_attachment_id:
            raise ValidationError(_("Unable to create attachment"))


class AwardCallsign(models.Model):
    _name = "ham.award.callsign"
    _inherit = "mail.thread"
    _description = "Award Callsign"
    _order = "callsign"
    _rec_name = "callsign"

    _sql_constraints = [
        ("callsign_uniq", "UNIQUE(callsign)", _("Callsign already exists"))
    ]

    callsign = fields.Char(
        string="Callsign",
        help="Callsign",
        required=True,
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
