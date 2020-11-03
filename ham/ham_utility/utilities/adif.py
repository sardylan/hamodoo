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
            raw_content = raw_content.decode()

        items = adif_regex.findall(raw_content)
        if not items:
            raise ValidationError(_("Invalid ADIF file"))

        mode = MODE_HEADER

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
            item_length = 0
            item_type = ""

            if len(item_split) > 1:
                item_length = int(item_split[1].strip())

            if len(item_split) > 2:
                item_type = item_split[2].strip().upper()

            item_value = tag_value.strip()

            if item_length:
                item_value = tag_value[:item_length].strip()

            if item_param in ["TIME_ON", "TIME_OFF"]:
                second = len(item_value) > 4 and int(item_value[4:6]) or 0
                item_value = time(hour=int(item_value[0:2]), minute=int(item_value[2:4]), second=second)
            elif item_param in ["QSO_DATE", "QSO_DATE_OFF", "QSLSDATE"]:
                item_value = date(year=int(item_value[0:4]), month=int(item_value[4:6]), day=int(item_value[6:8]))
            elif item_param in ["FREQ", "FREQ_RX"]:
                item_value = item_value.replace(",", ".")
                item_value = int(float(item_value) * 1000000)
            elif item_param in ["GRIDSQUARE"]:
                item_value = "%s%s" % (item_value[0:4].upper(), item_value[4:8].lower())

            elif item_type == "D":
                item_value = date(year=int(item_value[0:4]), month=int(item_value[4:6]), day=int(item_value[6:8]))
            elif item_type == "T":
                second = len(item_value) > 4 and int(item_value[4:6]) or 0
                item_value = time(hour=int(item_value[0:2]), minute=int(item_value[2:4]), second=second)
            elif item_type == "B":
                item_value = bool(item_value.upper() == "Y")
            elif item_type == "N":
                item_value = int(item_value)

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
    def generate_adif(self, qso_ids):
        adif = ""

        adif += self._generate_adif_header()

        sorted_qso_ids = sorted(qso_ids, key=lambda x: x.ts_start)

        for qso_id in sorted_qso_ids:
            adif += self.generate_adif_qso(qso_id)

        return adif

    @api.model
    def generate_adif_qso(self, qso_id):
        if not qso_id:
            raise ValidationError(_("Invalid qso_id"))

        qso = ""

        qso += self._tag_serialize("TIME_ON", qso_id.ts_start.strftime(FORMAT_TIME))
        qso += self._tag_serialize("TIME_OFF", qso_id.ts_end.strftime(FORMAT_TIME))
        qso += self._tag_serialize("QSO_DATE", qso_id.ts_start.strftime(FORMAT_DATE))
        qso += self._tag_serialize("QSO_DATE_OFF", qso_id.ts_end.strftime(FORMAT_DATE))
        qso += self._tag_serialize("CALL", qso_id.callsign)

        if qso_id.local_callsign:
            qso += self._tag_serialize("STATION_CALLSIGN", qso_id.local_callsign)

        if qso_id.op_name:
            qso += self._tag_serialize("NAME", qso_id.op_name)

        qso += self._tag_serialize("FREQ", float(qso_id.frequency) / 1000000)
        qso += self._tag_serialize("FREQ_RX", float(qso_id.rx_frequency) / 1000000)

        qso += self._tag_serialize("MODE", qso_id.modulation_id.name)
        qso += self._tag_serialize("RST_SENT", qso_id.tx_rst)
        qso += self._tag_serialize("RST_RCVD", qso_id.rx_rst)

        if qso_id.qth:
            qso += self._tag_serialize("QTH", qso_id.qth)

        comment_items = []
        for station_id in qso_id.station_ids:
            comment_items.append(station_id.reference)

        comment = " - ".join(comment_items)
        if comment:
            qso += self._tag_serialize("COMMENT", comment)

        if qso_id.note:
            notes = BeautifulSoup(qso_id.note, features="lxml").text.strip()
            if notes:
                qso += self._tag_serialize("NOTES", notes)

        qso += self._tag_serialize("EOR")

        return qso

    @api.model
    def _generate_adif_header(self):
        header = ""

        header += self._tag_serialize("ADIF_VER", "3.1.0")
        header += self._tag_serialize("CREATED_TIMESTAMP", datetime.datetime.now().strftime("%Y%m%d %H%M%S"))
        header += self._tag_serialize("PROGRAMID", "HAM Utilities for Odoo, by IS0GVH Luca")
        header += self._tag_serialize("PROGRAMVERSION", "1.0.0")
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
