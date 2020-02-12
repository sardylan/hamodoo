from odoo import models, fields


class QSO(models.AbstractModel):
    _name = "ham_utility.qso"
    _inherit = "mail.thread"
    _description = "Abstract QSO"
    _order = "ts_start DESC"

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
        required=True
    )

    rx_frequency = fields.Integer(
        string="RX Frequency",
        help="Frequency of RX"
    )

    modulation_id = fields.Many2one(
        string="Modulation",
        help="Modulation",
        comodel_name="ham_utility.modulation",
        required=True
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
