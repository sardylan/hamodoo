from odoo import models, fields


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


class QSOPublish(models.Model):
    _name = "ham.award.qso.publish"
    _description = "QSO Sending to external sites"

    qso_id = fields.Many2one(
        string="QSO",
        help="QSO",
        comodel_name="ham.award.qso",
        required=True
    )

    website_tag = fields.Char(
        string="Website tag",
        help="External website tag",
        required=True
    )

    website = fields.Char(
        string="Website",
        help="External website",
        required=True
    )

    ts = fields.Datetime(
        string="Date & Time",
        help="QSO publishing Date & Time",
        readonly=True,
        default=lambda self: fields.Datetime.now()
    )
