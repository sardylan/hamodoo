from odoo import models, fields


class AwardReject(models.TransientModel):
    _name = "ham.wizard.upload.reject"
    _description = "Wizard for rejecting ADIF upload"

    upload_id = fields.Many2one(
        string="Upload",
        help="Related Upload",
        comodel_name="ham.award.upload",
        required=True,
        readonly=True
    )

    errors = fields.Html(
        string="Errors",
        help="Errors or message for uploader"
    )

    def action_reject(self):
        self.ensure_one()

        self.upload_id.write({
            "errors": self.errors,
            "state": "error"
        })

        return {
            "type": "ir.actions.client",
            "tag": "reload"
        }
