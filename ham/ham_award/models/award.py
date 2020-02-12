from odoo import models, fields
from odoo.tools.translate import _


class Award(models.Model):
    _name = "ham_award.award"
    _inherit = "mail.thread"
    _description = "Award"
    _order = "ts_start DESC"

    _sql_constraints = [
        ("name_uniq", "UNIQUE(name)", _("Already present. Must be unique"))
    ]

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

    name = fields.Char(
        string="Name",
        help="Name of the award",
        required=True,
        tracking=True
    )
