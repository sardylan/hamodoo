from datetime import datetime

from odoo import models, api
from odoo.exceptions import ValidationError


class Cabrillo(models.AbstractModel):
    _name = "hamutility.cabrillo"
    _description = "Cabrillo log format parsing utilities"

    @api.model
    def parse_qso_line(self, line=""):
        if not line \
                or len(line) < 73 \
                or not line.startswith("QSO: "):
            raise ValidationError("Wrong line length for Cabrillo format")

        frequency_string = line[5:10].strip().upper()
        if frequency_string.upper() == "LIGHT":
            raise ValidationError("Light frequency not implemented!!!! :D")

        if len(frequency_string) >= 4:
            frequency = int(frequency_string) * 1000
        elif "G" in frequency_string:
            frequency = int(frequency_string.replace("G", "")) * 1000000000
        else:
            frequency = int(frequency_string) * 1000000

        mode = line[11:13].strip().upper()

        datetime_string = line[14:29].upper().strip()
        ts = datetime.strptime(datetime_string, "%Y-%m-%d %H%M")

        tx_callsign = line[30:43].upper().strip()

        tx_r = line[44:45]
        tx_s = line[45:46]
        tx_t = line[46:47] if line[46:47] != " " else None

        tx_exchange = line[48:54].upper().strip()

        rx_callsign = line[55:68].upper().strip()

        rx_r = line[69:70]
        rx_s = line[70:71]
        rx_t = line[71:72] if line[71:72] != " " else None

        rx_exchange = line[73:79].upper().strip()

        transmitter = line[80:81] if len(line) == 81 and line[80:81] != " " else None

        return {
            "frequency": frequency,
            "mode": mode,
            "ts": ts,
            "tx_callsign": tx_callsign,
            "tx_r": tx_r,
            "tx_s": tx_s,
            "tx_t": tx_t,
            "tx_exchange": tx_exchange,
            "rx_callsign": rx_callsign,
            "rx_r": rx_r,
            "rx_s": rx_s,
            "rx_t": rx_t,
            "rx_exchange": rx_exchange,
            "transmitter": transmitter
        }
