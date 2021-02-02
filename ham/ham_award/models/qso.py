import datetime
import os

from odoo import models, fields, api


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

    publish_ids = fields.One2many(
        string="Pubblications",
        help="QSO pubblications in online websites",
        comodel_name="ham.award.qso.publish",
        inverse_name="qso_id",
    )

    @api.model
    def compute_adif_filename(self, dt: datetime.datetime, qsos) -> str:
        award_obj = self.env["ham.award"]

        ret = super().compute_adif_filename(dt, qsos)

        award_ids = []

        for rec in self:
            if rec.award_id.id not in award_ids:
                award_ids.append(rec.award_id.id)

        if len(award_ids) == 1:
            award = award_obj.browse(award_ids[0])
            award_name: str = award.name
            name, ext = os.path.splitext(ret)
            ret = f"{name} {award_name}{ext}"

        return ret


class QSOPublish(models.Model):
    _name = "ham.award.qso.publish"
    _description = "QSO Sending to external sites"

    qso_id = fields.Many2one(
        string="QSO",
        help="QSO",
        comodel_name="ham.award.qso",
        required=True
    )

    website_id = fields.Many2one(
        string="Website",
        help="External website",
        comodel_name="ham.website",
        required=True
    )

    ts = fields.Datetime(
        string="Date & Time",
        help="QSO publishing Date & Time",
        readonly=True,
        default=lambda self: fields.Datetime.now()
    )
