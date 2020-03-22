from odoo import models, fields, api
from odoo.tools.translate import _


class Station(models.Model):
    _name = "ham_award.station"
    _inherit = "mail.thread"
    _description = "Station"
    _order = "callsign ASC"

    _sql_constraints = [
        ("type_callsign_reference_uniq", "UNIQUE(type_id, reference, reference)", _("Already present. Must be unique")),
    ]

    type_id = fields.Many2one(
        string="Type",
        help="Station Type",
        comodel_name="ham_award.station_type",
        required=True,
        tracking=True
    )

    callsign = fields.Char(
        string="Callsign",
        help="Callsign",
        required=True,
        tracking=True
    )

    reference = fields.Char(
        string="Reference",
        help="Reference number or code",
        required=True,
        tracking=True
    )

    active = fields.Boolean(
        string="Active",
        help="Active",
        required=True,
        default=True,
        tracking=True
    )

    name = fields.Char(
        string="Name",
        help="Name",
        readonly=True,
        compute="_compute_name"
    )

    def action_active_toggle(self):
        for rec in self:
            rec.active = not rec.active

        return True

    @api.depends("type_id", "callsign", "reference")
    def _compute_name(self):
        for rec in self:
            rec.name = " - ".join([
                rec.type_id.short_name,
                rec.callsign,
                rec.reference
            ])


class StationType(models.Model):
    _name = "ham_award.station_type"
    _inherit = "mail.thread"
    _description = "Station type"
    _order = "name ASC"

    _sql_constraints = [
        ("name_uniq", "UNIQUE(name)", _("Already present. Must be unique")),
    ]

    name = fields.Char(
        string="Name",
        help="Name",
        required=True,
        tracking=True
    )

    short_name = fields.Char(
        string="Short Name",
        help="Short name",
        required=True,
        tracking=True
    )
