from odoo import models, fields


class Upload(models.Model):
    _name = "ham_award.upload"
    _inherit = "mail.thread"
    _description = "Upload"
    _order = "ts DESC"

    ts = fields.Datetime(
        string="Date & Time of upload",
        required=True,
        tracking=True
    )

    file_name = fields.Char(
        string="File name",
        tracking=True
    )

    file_content = fields.Binary(
        string="File",
        help="Uploaded file",
        required=True,
        attachment=True,
        tracking=True
    )

    operator_id = fields.Many2one(
        string="Operator",
        help="Operator",
        comodel_name="ham_award.operator",
        required=True,
        tracking=True
    )

    award_id = fields.Many2one(
        string="Award",
        help="Related award",
        comodel_name="ham_award.award",
        required=True,
        tracking=True
    )
