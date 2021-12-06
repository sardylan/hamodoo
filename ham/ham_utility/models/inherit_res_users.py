from odoo import models, fields

SELF_FIELDS_ADD = [
    "qrzcom_username",
    "qrzcom_password"
]


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

    @property
    def SELF_READABLE_FIELDS(self):
        return super().SELF_READABLE_FIELDS + SELF_FIELDS_ADD

    @property
    def SELF_WRITEABLE_FIELDS(self):
        return super().SELF_WRITEABLE_FIELDS + SELF_FIELDS_ADD

    def action_qrzcom_verify_credentials(self):
        qrzcom_utility = self.env["ham.utility.websites.qrzcom"]
        for rec in self:
            qrzcom_utility.verify_credentials(
                username=rec.qrzcom_username,
                password=rec.qrzcom_password
            )
