from odoo import models, fields, api

SELECTION_INFORMATION = [
    ("N", "N - No transmitted information"),
    ("A", "A - Aural telegraphy, intended to be decoded by ear, such as Morse code"),
    ("B", "B - Electronic telegraphy, intended to be decoded by machine (radioteletype and digital modes)"),
    ("C", "C - Facsimile (still images)"),
    ("D", "D - Data transmission, telemetry or telecommand (remote control)"),
    ("E", "E - Telephony (voice or music intended to be listened to by a human)"),
    ("F", "F - Video (television signals)"),
    ("W", "W - Combination of any of the above"),
    ("X", "X - None of the above")
]

SELECTION_SIGNAL = [
    ("0", "0 - No modulating signal"),
    ("1", "1 - One channel containing digital information, no subcarrier"),
    ("2", "2 - One channel containing digital information, using a subcarrier"),
    ("3", "3 - One channel containing analog information"),
    ("7", "7 - More than one channel containing digital information"),
    ("8", "8 - More than one channel containing analog information"),
    ("9", "9 - Combination of analog and digital channels"),
    ("X", "X - None of the above")
]

SELECTION_MODULATION = [
    ("N", "N - Unmodulated carrier"),
    ("A", "A - Double-sideband amplitude modulation (e.g. AM broadcast radio)"),
    ("H", "H - Single-sideband with full carrier (e.g. as used by CHU)"),
    ("R", "R - Single-sideband with reduced or variable carrier"),
    ("J", "J - Single-sideband with suppressed carrier (e.g. Shortwave utility and amateur stations)"),
    ("B", "B - Independent sideband (two sidebands containing different signals)"),
    ("C", "C - Vestigial sideband (e.g. NTSC)"),
    ("F", "F - Frequency modulation (e.g. FM broadcast radio)"),
    ("G", "G - Phase modulation"),
    ("D", "D - Combination of AM and FM or PM"),
    ("P", "P - Sequence of pulses without modulation"),
    ("K", "K - Pulse amplitude modulation"),
    ("L", "L - Pulse width modulation (e.g. as used by WWVB)"),
    ("M", "M - Pulse position modulation"),
    ("Q", "Q - Sequence of pulses, phase or frequency modulation within each pulse"),
    ("V", "V - Combination of pulse modulation methods"),
    ("W", "W - Combination of any of the above"),
    ("X", "X - None of the above")
]


class Modulation(models.Model):
    _name = "hamutility.modulation"
    _inherit = "mail.thread"
    _description = "Modulation"
    _rec_name = "complete_name"
    _order = "name ASC"

    _sql_constraints = [
        ("name_uniq", "UNIQUE(name)", "Modulation already exists. Name must be unique.")
    ]

    name = fields.Char(
        string="Name",
        required=True,
        translate=False,
        tracking=True
    )

    description = fields.Char(
        string="Description",
        tracking=True
    )

    modulation = fields.Selection(
        string="Modulation",
        required=True,
        selection=SELECTION_MODULATION,
        tracking=True
    )

    signal = fields.Selection(
        string="Signal",
        required=True,
        selection=SELECTION_SIGNAL,
        tracking=True
    )

    information = fields.Selection(
        string="Information",
        required=True,
        selection=SELECTION_INFORMATION,
        tracking=True
    )

    bandwidth = fields.Integer(
        string="Bandwidth",
        help="Bandwidth in Hz",
        tracking=True
    )

    emission = fields.Char(
        string="Emission",
        compute="_compute_emission",
        translate=False,
        store=True
    )

    complete_name = fields.Char(
        string="Complete name",
        compute="_compute_complete_name",
        translate=False,
        store=True
    )

    note = fields.Html(
        string="Note"
    )

    @api.model
    def create(self, vals):
        if "name" in vals and vals["name"]:
            vals["name"] = vals["name"].strip().upper()

        return super().create(vals)

    def write(self, vals):
        if "name" in vals and vals["name"]:
            vals["name"] = vals["name"].strip().upper()

        return super().write(vals)

    @api.onchange("name")
    def _onchange_name(self):
        for rec in self:
            if rec.name:
                rec.name = rec.name.strip().upper()

    @api.depends("emission", "name")
    def _compute_complete_name(self):
        for rec in self:
            rec.complete_name = "%s (%s)" % (rec.name, rec.emission)

    @api.depends("bandwidth", "modulation", "signal", "information")
    def _compute_emission(self):
        modulation_utility = self.env["hamutility.utility_modulation"]

        for rec in self:
            bandwidth = ""
            if rec.bandwidth:
                bandwidth = modulation_utility.compute_bandwidth_tag(rec.bandwidth)

            rec.emission = "%s%s%s%s" % (bandwidth, rec.modulation, rec.signal, rec.information)
