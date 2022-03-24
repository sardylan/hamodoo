from odoo import models, fields
from odoo.tools.translate import _


class NavalClub(models.Model):
    _name = "ham.award.naval.club"
    _description = "Naval Club"

    _sql_constraints = [
        ("tag_uniq", "UNIQUE(tag)", _("Tag already exists. Must be unique."))
    ]

    name = fields.Char(
        string="Name",
        help="Club name",
        required=True
    )

    short_name = fields.Char(
        string="Short name",
        help="Short name",
        required=True
    )

    tag = fields.Char(
        string="Tag",
        help="Tag",
        required=True
    )
