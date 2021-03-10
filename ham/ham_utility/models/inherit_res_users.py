from odoo import models, fields


class ResUsers(models.Model):
    _inherit = "res.users"

    qrzcom_username = fields.Char(
        string="QRZ.com Username",
        help="QRZ.com Username"
    )

    qrzcom_password = fields.Char(
        string="QRZ.com Password",
        help="QRZ.com Password"
    )

    def __init__(self, pool, cr):
        super().__init__(pool, cr)

        self_fields_add = [
            "qrzcom_username",
            "qrzcom_password"
        ]

        type(self).SELF_READABLE_FIELDS = type(self).SELF_READABLE_FIELDS + self_fields_add
        type(self).SELF_WRITEABLE_FIELDS = type(self).SELF_WRITEABLE_FIELDS + self_fields_add

    def action_qrzcom_verify_credentials(self):
        qrzcom_utility = self.env["ham.utility.websites.qrzcom"]
        for rec in self:
            qrzcom_utility.verify_credentials(
                username=rec.qrzcom_username,
                password=rec.qrzcom_password
            )
