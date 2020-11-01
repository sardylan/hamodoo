import datetime
import logging

from odoo import models, api
from odoo.exceptions import ValidationError

_logger = logging.getLogger(__name__)


class QsoUtility(models.AbstractModel):
    _name = "ham.utility.qso"
    _description = "QSO Utilities"

    @api.model
    def values_from_adif_record(self, adif_record):
        modulation_obj = self.env["ham.modulation"]

        ts_time = adif_record["TIME_ON"]
        ts_date = adif_record["QSO_DATE"]
        ts_start = datetime.datetime.combine(ts_date, ts_time)

        if "TIME_OFF" in adif_record:
            ts_time = adif_record["TIME_OFF"]
        if "QSO_DATE_OFF" in adif_record:
            ts_date = adif_record["QSO_DATE_OFF"]
        ts_end = datetime.datetime.combine(ts_date, ts_time)

        callsign = adif_record["CALL"]

        if "STATION_CALLSIGN" in adif_record:
            local_callsign = adif_record["STATION_CALLSIGN"]
        elif "OWNER_CALLSIGN " in adif_record:
            local_callsign = adif_record["OWNER_CALLSIGN"]
        else:
            local_callsign = callsign

        op_name = "NAME" in adif_record and adif_record["NAME"].strip() or ""

        frequency = adif_record["FREQ"]

        rx_frequency = "FREQ_RX" in adif_record and adif_record["FREQ_RX"] or frequency

        modulation_name = adif_record["MODE"]

        modulation = modulation_obj.search([("name", "=", modulation_name)])
        if not modulation:
            modulation = modulation_obj.search([("name", "ilike", modulation_name)])

        if not modulation:
            raise ValidationError("Modulation not found for value: %s" % modulation_name)

        tx_rst = "RST_SENT" in adif_record and adif_record["RST_SENT"].strip() or ""
        rx_rst = "RST_RCVD" in adif_record and adif_record["RST_RCVD"].strip() or ""
        qth = "QTH" in adif_record and adif_record["QTH"].strip() or ""

        note = ""

        for key in ["NOTES", "NOTES_INTL", "SRX", "SRX_STRING", "STX", "STX_STRING"]:
            if key in adif_record:
                note += adif_record[key]

        values = {
            "ts_start": ts_start,
            "ts_end": ts_end,
            "local_callsign": local_callsign,
            "callsign": callsign,
            "op_name": op_name,
            "frequency": frequency,
            "rx_frequency": rx_frequency,
            "modulation_id": modulation.id,
            "tx_rst": tx_rst,
            "rx_rst": rx_rst,
            "qth": qth,
            "note": note
        }

        return values
