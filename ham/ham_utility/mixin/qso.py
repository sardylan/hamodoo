from odoo import models, fields, api
from odoo.exceptions import ValidationError
from odoo.tools.translate import _


class QSO(models.AbstractModel):
    _name = "ham.mixin.qso"
    _inherit = "mail.thread"
    _description = "Abstract QSO"
    _order = "ts_start DESC"
    _rec_name = "footprint"

    _sql_constraints = [
        ("footprint_uniq", "UNIQUE(footprint)", _("QSO Already present"))
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

    local_callsign = fields.Char(
        string="Local Callsign",
        help="Callsign used for QSO",
        required=True,
        tracking=True
    )

    callsign = fields.Char(
        string="Callsign",
        help="Callsign of remote station",
        required=True,
        tracking=True
    )

    op_name = fields.Char(
        string="Operator name",
        help="Name of remote operator",
        tracking=True
    )

    frequency = fields.Float(
        string="Frequency",
        help="Frequency of TX",
        digits=(12, 0),
        group_operator=False,
        required=True,
        tracking=True
    )

    rx_frequency = fields.Float(
        string="RX Frequency",
        help="Frequency of RX",
        digits=(12, 0),
        group_operator=False,
        required=True,
        tracking=True
    )

    modulation_id = fields.Many2one(
        string="Modulation",
        help="Modulation",
        comodel_name="ham.modulation",
        required=True,
        tracking=True
    )

    tx_rst = fields.Char(
        string="RST TX",
        help="RST sent",
        required=True,
        tracking=True
    )

    rx_rst = fields.Char(
        string="RST RX",
        help="RST received",
        required=True,
        tracking=True
    )

    qth = fields.Char(
        string="QTH",
        help="QTH of remote station",
        tracking=True
    )

    footprint = fields.Char(
        string="Footprint",
        help="QSO Footprint",
        readonly=True,
        compute="compute_footprint",
        store=True
    )

    country_id = fields.Many2one(
        string="Country",
        help="HAM Country",
        comodel_name="ham.country",
        readonly=True,
        compute="_compute_country_id",
        store=True
    )

    band_id = fields.Many2one(
        string="Band",
        help="HAM Band",
        comodel_name="ham.band",
        readonly=True,
        compute="_compute_band_id",
        store=True
    )

    note = fields.Html(
        string="Note",
        help="Note",
        tracking=True
    )

    @api.model_create_multi
    def create(self, vals):
        if isinstance(vals, dict):
            self.sanitize_vals(vals)
        else:
            for item in vals:
                self.sanitize_vals(item)

        return super().create(vals)

    def write(self, vals):
        self.sanitize_vals(vals)
        return super().write(vals)

    @api.onchange("callsign", "local_callsign")
    def uppercase_onchange(self):
        callsign_utility = self.env["ham.utility.callsign"]

        for rec in self:
            rec.callsign = callsign_utility.uppercase(rec.callsign)
            rec.local_callsign = callsign_utility.uppercase(rec.local_callsign)

    @api.depends("ts_start", "local_callsign", "callsign", "modulation_id", "frequency")
    def compute_footprint(self):
        for rec in self:
            footprint = self.footprint_value(
                rec.ts_start,
                rec.local_callsign,
                rec.callsign,
                rec.modulation_id,
                rec.frequency
            )

            rec.footprint = footprint.strip().upper()

    @api.depends("callsign")
    def _compute_country_id(self):
        country_utility = self.env["ham.utility.country"]

        for rec in self:
            country_id = country_utility.get_country(rec.callsign)
            rec.country_id = country_id and country_id.id or False

    @api.depends("frequency")
    def _compute_band_id(self):
        band_obj = self.env["ham.band"]

        for rec in self:
            band_id = band_obj.get_band(rec.frequency)
            rec.band_id = band_id and band_id.id or False

    @api.model
    def footprint_value(self, ts_start, local_callsign, callsign, modulation_id, frequency):
        if not ts_start or not local_callsign or not callsign or not modulation_id or not frequency:
            return ""

        footprint = "%s-%s-%s-%s-%d" % (
            ts_start.strftime("%Y%m%d%H%M%S"),
            local_callsign.strip().upper(),
            callsign.strip().upper(),
            modulation_id.name.strip().upper(),
            frequency
        )

        return footprint

    @api.model
    def sanitize_vals(self, vals: dict):
        modulation_obj = self.env["ham.modulation"]

        callsign_utility = self.env["ham.utility.callsign"]

        if "rx_frequency" not in vals or not vals["rx_frequency"]:
            if "frequency" in vals:
                vals["rx_frequency"] = vals["frequency"]

        modulation = modulation_obj.browse(vals["modulation_id"])
        if not modulation:
            raise ValidationError(_("Modulation not found when creating QSO"))

        if "tx_rst" not in vals or not vals["tx_rst"].strip():
            vals["tx_rst"] = modulation.default_rst
        if "rx_rst" not in vals or not vals["rx_rst"].strip():
            vals["rx_rst"] = modulation.default_rst

        for field in ["callsign", "local_callsign"]:
            if field in vals:
                vals[field] = callsign_utility.uppercase(vals[field])
