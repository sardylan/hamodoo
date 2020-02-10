import re
from datetime import time, date

from odoo import models, api

MODE_HEADER = 0
MODE_QSO = 1


class AdifUtility(models.AbstractModel):
    _name = "hamutility.adif"
    _description = "ADIF log format parsing utilities"

    @api.model
    def parse_file_adif(self, raw_content=""):
        adif_regex = re.compile(r"<([a-zA-Z0-9:_]+)>([^<\t\f\v\r\n]*)")

        items = adif_regex.findall(raw_content)

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
            elif item_param in ["QSO_DATE", "QSLSDATE"]:
                item_value = date(year=int(item_value[0:4]), month=int(item_value[4:6]), day=int(item_value[6:8]))
            elif item_param in ["FREQ", "FREQ_RX"]:
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
