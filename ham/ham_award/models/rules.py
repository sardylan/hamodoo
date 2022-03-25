from odoo import models, fields
from odoo.tools.translate import _


class Rules(models.Model):
    _name = "ham.award.rules"

    _sql_constraints = [
        ("tag_uniq", "UNIQUE(tag)", _("Tag already present, must be unique."))
    ]

    name = fields.Char(
        string="Name",
        help="Rules name",
        required=True
    )

    tag = fields.Char(
        string="Tag",
        help="Tag for code",
        required=True
    )
