from odoo import models, fields


class QSO(models.Model):
    _name = "ham_award.qso"

    _inherit = [
        "ham_utility.qso",
        "mail.thread"
    ]

    award_id = fields.Many2one(
        string="Award",
        help="Related award",
        comodel_name="ham_award.award",
        required=True,
        tracking=True
    )

    operator_id = fields.Many2one(
        string="Award",
        help="Related award",
        comodel_name="ham_award.operator",
        required=True,
        tracking=True
    )
