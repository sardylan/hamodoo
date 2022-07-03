from odoo import models
from odoo.exceptions import ValidationError
from odoo.tools.translate import _


class Rules(models.Model):
    _inherit = "ham.award.rules"

    def coastal_qso_points(self, qso) -> int:
        ham_award_qso_obj = self.env["ham.award.qso"]
        ham_award_naval_station_obj = self.env["ham.award.naval.station"]

        if not qso:
            raise ValidationError(_("QSO not valid"))

        dupe_qsos = ham_award_qso_obj.search(
            args=[
                ("award_id", "=", qso.award_id.id),
                ("callsign", "=", qso.callsign),
                ("count_as", "=", qso.count_as),
                ("ts_start", ">=", qso.ts_start.replace(hour=0, minute=0, second=0)),
                ("ts_start", "<=", qso.ts_start.replace(hour=23, minute=59, second=59)),
            ],
            order="ts_start"
        )

        if len(dupe_qsos) < 1:
            raise ValidationError(_("Error searching same-day QSOs"))

        if qso.id != dupe_qsos[0].id:
            return 0

        if qso.award_id.coastal_jolly and qso.award_id.coastal_jolly.callsign in qso.callsign:
            return 25
        elif any([x.callsign in qso.callsign for x in qso.award_id.coastal_station_ids]):
            return 15

        coastal_stations = ham_award_naval_station_obj.search_read(domain=[], fields=["callsign"])
        is_naval_station = any([x["callsign"] in qso.callsign for x in coastal_stations])
        if not is_naval_station:
            return 0

        if qso.count_as == "cw":
            return 5
        elif qso.count_as == "phone":
            return 3
        elif qso.count_as == "digi":
            return 2

        return 0
