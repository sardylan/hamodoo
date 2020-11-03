from odoo import models, fields
from odoo.tools.translate import _


class HamWebsite(models.Model):
    _name = "ham.website"
    _inherit = "mail.thread"
    _description = "HAM Website for QSOs publishing"

    _sql_constraints = [
        ("tag_uniq", "UNIQUE(tag)", _("Tag already exists"))
    ]

    name = fields.Char(
        string="Name",
        help="Name",
        required=True,
        tracking=True
    )

    tag = fields.Char(
        string="Tag",
        help="Tag",
        required=True,
        tracking=True
    )

    publish_enabled = fields.Boolean(
        string="Publish enabled",
        help="Checked if QSOs publish is enabled",
        required=True
    )
