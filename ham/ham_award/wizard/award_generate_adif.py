from odoo import models, fields, api

SELECTION_WEBSITE = [
    ("hrdlog", "HRDLog"),
    ("eqsl", "eQSL"),
]


class AwardPublish(models.TransientModel):
    _name = "ham.wizard.award.generate.adif"
    _description = "Wizard for generating ADIF from Award Log"

    award_id = fields.Many2one(
        string="Award",
        help="Related Award",
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

    @api.onchange("award_id")
    def onchange_award_id(self):
        return {
            "domain": {
                "callsign_id": [("id", "in", self.award_id.callsigns.ids)]
            }
        }

    def action_publish(self):
        self.ensure_one()

        award_generate_adif_utility = self.env["ham.utility.award.generate.adif"]
        award_generate_adif_utility.generate(self.award_id, self.callsign_id)

        return {
            "type": "ir.actions.client",
            "tag": "reload"
        }
