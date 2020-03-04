from odoo import models, fields, api
from odoo.tools.translate import _


class QSO(models.AbstractModel):
    _name = "ham_utility.qso"
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

    frequency = fields.Integer(
        string="Frequency",
        help="Frequency of TX",
        required=True,
        tracking=True
    )

    rx_frequency = fields.Integer(
        string="RX Frequency",
        help="Frequency of RX",
        required=True,
        tracking=True
    )

    modulation_id = fields.Many2one(
        string="Modulation",
        help="Modulation",
        comodel_name="ham_utility.modulation",
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

    def create(self, vals):
        vals = self.sanitize_vals(vals)
        return super().create(vals)

    def write(self, vals):
        vals = self.sanitize_vals(vals)
        return super().write(vals)

    @api.onchange("callsign", "local_callsign")
    def uppercase_onchange(self):
        callsign_utility = self.env["ham_utility.utility_callsign"]

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
    def sanitize_vals(self, vals):
        callsign_utility = self.env["ham_utility.utility_callsign"]

        if "rx_frequency" not in vals or not vals["rx_frequency"]:
            vals["rx_frequency"] = vals["frequency"]

        for field in ["callsign", "local_callsign"]:
            if field in vals:
                vals[field] = callsign_utility.uppercase(vals[field])

        return vals
