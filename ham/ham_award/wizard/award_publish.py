from odoo import models, fields, api

SELECTION_WEBSITE = [
    ("hrdlog", "HRDLog"),
    ("eqsl", "eQSL"),
]


class AwardPublish(models.TransientModel):
    _name = "ham.wizard.award.publish"
    _description = "Wizard for publishing Award QSOs to websites"

    award_id = fields.Many2one(
        string="Award",
        Help="Related Award",
        comodel_name="ham.award",
        required=True,
        readonly=True
    )

    callsign_id = fields.Many2one(
        string="Callsign",
        help="Select callsign to publish",
        comodel_name="ham.award.callsign",
        required=True
    )

    website = fields.Selection(
        string="Website",
        help="Choose website for uploading",
        selection=SELECTION_WEBSITE,
        required=True,
        default="hrdlog"
    )

    @api.onchange("award_id")
    def onchange_award_id(self):
        return {
            "domain": {
                "callsign_id": [("id", "in", self.award_id.callsigns.ids)]
            }
        }

    def action_publish(self):
        self.ensure_one()

        award_publish_utility = self.env["ham.utility.award.publish"]
        award_publish_utility.publish_not_published_qsos(self.award_id, self.callsign_id, self.website)
