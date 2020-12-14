import datetime
import re
from datetime import time, date

from bs4 import BeautifulSoup

from odoo import models, api
from odoo.exceptions import ValidationError
from odoo.tools.translate import _

MODE_HEADER = 0
MODE_QSO = 1

FORMAT_DATE = "%Y%m%d"
FORMAT_TIME = "%H%M%S"


class AdifUtility(models.AbstractModel):
    _name = "ham.utility.adif"
    _description = "ADIF log format parsing utilities"

    @api.model
    def parse_file_adif(self, raw_content=""):
        adif_regex = re.compile(r"<([a-zA-Z0-9:_]+)>([^<\t\f\v\r\n]*)")

        if isinstance(raw_content, bytes):
            raw_content = self._bytes_to_str(raw_content)

        raw_content = self._sanitize_raw_content(raw_content)

        items = adif_regex.findall(raw_content)
        if not items:
            raise ValidationError(_("Invalid ADIF file"))

        mode = MODE_HEADER
        if "<EOH>" not in raw_content.upper():
            mode = MODE_QSO

        adif_dict = {
            "headers": {},
            "qso": []
        }

        qso_item = {}

        for item in items:
            tag_param = item[0].upper()
            tag_value = item[1]

            item_split = tag_param.split(":")

            item_param = item_split[0].strip()
            item_length = False
            item_type = ""

            if len(item_split) > 1:
                item_length = int(item_split[1].strip())

            if len(item_split) > 2:
                item_type = item_split[2].strip().upper()

            item_value = tag_value.strip()

            if isinstance(item_length, int):
                item_value = tag_value[:item_length].strip()

            if item_param in ["TIME_ON", "TIME_OFF"]:
                second = len(item_value) > 4 and int(item_value[4:6]) or 0
                item_value = time(hour=int(item_value[0:2]), minute=int(item_value[2:4]), second=second)
            elif item_param in ["QSO_DATE", "QSO_DATE_OFF", "QSLSDATE"]:
                item_value = date(year=int(item_value[0:4]), month=int(item_value[4:6]), day=int(item_value[6:8]))
            elif item_param in ["FREQ", "FREQ_RX"]:
                item_value = item_value.replace(",", ".")
                item_value = re.sub("[^0-9.]", "", item_value)
                item_value = int(float(item_value) * 1000000)
            elif item_param in ["GRIDSQUARE"]:
                item_value = "%s%s" % (item_value[0:4].upper(), item_value[4:8].lower())
            elif item_param in ["CALL"]:
                item_value = re.sub("[^A-Z0-9/]", "", item_value.upper())

            elif item_type == "D":
                item_value = date(year=int(item_value[0:4]), month=int(item_value[4:6]), day=int(item_value[6:8]))
            elif item_type == "T":
                second = len(item_value) > 4 and int(item_value[4:6]) or 0
                item_value = time(hour=int(item_value[0:2]), minute=int(item_value[2:4]), second=second)
            elif item_type == "B":
                item_value = bool(item_value.upper() == "Y")
            elif item_type == "N":
                item_value = int(item_value)
            else:
                item_value = item_value.replace("\";\"", "")

            if mode == MODE_HEADER:
                if item_param == "EOH":
                    mode = MODE_QSO
                    continue

                adif_dict["headers"][item_param] = item_value
                continue

            if item_param == "EOR":
                adif_dict["qso"].append(dict(qso_item))
                qso_item.clear()
                continue

            qso_item[item_param] = item_value

        return adif_dict

    @api.model
    def generate_adif(self, qsos, dt: datetime.datetime = datetime.datetime.utcnow()) -> str:
        adif: str = ""

        adif += self._generate_adif_header(dt=dt)

        sorted_qso_ids = sorted(qsos, key=lambda x: x.ts_start)

        for qso_id in sorted_qso_ids:
            adif += self.generate_adif_qso(qso_id)

        return adif

    @api.model
    def generate_adif_qso(self, qso):
        if not qso:
            raise ValidationError(_("Invalid qso_id"))

        band_obj = self.env["ham.band"]

        qso_string = ""

        qso_string += self._tag_serialize("TIME_ON", qso.ts_start.strftime(FORMAT_TIME))
        qso_string += self._tag_serialize("TIME_OFF", qso.ts_end.strftime(FORMAT_TIME))
        qso_string += self._tag_serialize("QSO_DATE", qso.ts_start.strftime(FORMAT_DATE))
        qso_string += self._tag_serialize("QSO_DATE_OFF", qso.ts_end.strftime(FORMAT_DATE))
        qso_string += self._tag_serialize("CALL", qso.callsign)

        if qso.local_callsign:
            qso_string += self._tag_serialize("STATION_CALLSIGN", qso.local_callsign)

        if qso.op_name:
            qso_string += self._tag_serialize("NAME", qso.op_name)

        qso_string += self._tag_serialize("FREQ", float(qso.frequency) / 1000000)

        band = band_obj.get_band(qso.frequency)
        if not band:
            raise ValidationError(_("Band not found for frequency %d") % qso.frequency)
        qso_string += self._tag_serialize("BAND", band.name)

        qso_string += self._tag_serialize("FREQ_RX", float(qso.rx_frequency) / 1000000)

        band = band_obj.get_band(qso.rx_frequency)
        if not band:
            raise ValidationError(_("Band not found for frequency %d") % qso.rx_frequency)
        qso_string += self._tag_serialize("BAND_RX", band.name)

        qso_string += self._tag_serialize("MODE", qso.modulation_id.name)
        qso_string += self._tag_serialize("RST_SENT", qso.tx_rst)
        qso_string += self._tag_serialize("RST_RCVD", qso.rx_rst)

        if qso.qth:
            qso_string += self._tag_serialize("QTH", qso.qth)

        comment_items = []
        # for station_id in qso_id.station_ids:
        #     comment_items.append(station_id.reference)

        comment = " - ".join(comment_items)
        if comment:
            qso_string += self._tag_serialize("COMMENT", comment)

        extra_content = self.generate_adif_qso_extra_fields(qso)
        if extra_content:
            qso_string += extra_content

        if qso.note:
            notes = BeautifulSoup(qso.note, features="lxml").text.strip()
            if notes:
                qso_string += self._tag_serialize("NOTES", notes)

        qso_string += self._tag_serialize("EOR")

        return qso_string

    @api.model
    def generate_adif_qso_extra_fields(self, qso) -> str:
        qso_string: str = ""
        return qso_string

    @api.model
    def _generate_adif_header(self, dt: datetime.datetime = datetime.datetime.utcnow()) -> str:
        header = ""

        header += self._tag_serialize("ADIF_VER", "3.1.1")
        header += self._tag_serialize("CREATED_TIMESTAMP", dt.strftime("%Y%m%d %H%M%S"))
        header += self._tag_serialize("PROGRAMID", "HAM Utilities for Odoo, by IS0GVH Luca")
        header += self._tag_serialize("PROGRAMVERSION", "2.3.0")
        header += self._tag_serialize("EOH")

        return header

    @api.model
    def _tag_serialize(self, raw_key, raw_value=None):
        key = raw_key.strip().upper()

        value = None

        if raw_value is not None:
            if isinstance(raw_value, int):
                value = "%d" % raw_value
            elif isinstance(raw_value, float):
                value = "%.03f" % raw_value
            else:
                value = raw_value.strip()

        if value is not None:
            tag = "<%s:%d>%s" % (key, len(value), value)
        else:
            tag = "<%s>" % key

        if key in ["EOH", "EOR"]:
            tag += "\n"

        return tag

    @staticmethod
    def _sanitize_raw_content(raw_content: str = ""):
        raw_content = raw_content.replace("<eh>", "<EOH>")  # Bug of WSJT-X
        return raw_content

    @staticmethod
    def _bytes_to_str(data: bytes):
        string: str = ""

        for codec_name in ["utf8", "iso8859-15", "ascii"]:
            try:
                string = data.decode(codec_name)
                break
            except UnicodeDecodeError:
                continue

        if not string:
            raise ValidationError(_("Unable to convert bytes to string"))

        return string
