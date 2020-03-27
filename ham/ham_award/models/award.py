import base64
import datetime

from odoo import models, fields, api
from odoo.exceptions import ValidationError
from odoo.tools.translate import _


class Award(models.Model):
    _name = "ham_award.award"
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

    common_callsign = fields.Char(
        string="Common Callsign",
        help="Common Callsign used by all stations in the award",
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
        comodel_name="ham_award.operator",
        relation="ham_award_operator_award_rel",
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
    def produce_adif(self, award_id):
        if not award_id:
            raise ValidationError(_("Award not valid"))

        ir_attachment_obj = self.env["ir.attachment"]
        qso_obj = self.env["ham_award.qso"]

        adif_utility = self.env["ham_utility.utility_adif"]

        qso_ids = qso_obj.search([
            ("award_id", "=", award_id.id),
            ("active", "=", True)
        ])

        adif_content = adif_utility.generate_adif(qso_ids)

        name = "%s %s" % (
            datetime.datetime.now().strftime("%Y%m%d-%H%M%S"),
            award_id.name
        )

        ir_attachment_id = ir_attachment_obj.create({
            "res_model": award_id._name,
            "res_id": award_id.id,
            "type": "binary",
            "name": name,
            "store_fname": name,
            "datas_fname": "%s.adi" % name,
            "datas": base64.b64encode(adif_content.encode()),
        })

        if not ir_attachment_id:
            raise ValidationError(_("Unable to create attachment"))
