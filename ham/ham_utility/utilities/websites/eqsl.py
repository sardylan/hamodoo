import logging

import requests
from bs4 import BeautifulSoup
from lxml import etree

from odoo import models, api
from odoo.exceptions import ValidationError
from odoo.tools.translate import _

_logger = logging.getLogger(__name__)

EQSL_API_UPLOAD_QSO = "https://www.eQSL.cc/qslcard/ImportADIF.cfm"
EQSL_API_APP_NAME = "ham.thehellnet.org"


class EQSLWebsiteUtility(models.AbstractModel):
    _name = "ham.utility.websites.eqsl"
    _description = "Integration with eQSL API"

    @api.model
    def upload_qso(self, qso, username: str = "", password: str = "", qth_nickname: str = ""):
        if not username or not password or not qth_nickname:
            _logger.error("Invalid login data. Username: %s - Password: %s - QTH Nickname: %s" % (
                username, password, qth_nickname
            ))
            raise ValidationError(_("Invalid login data"))

        if not qso:
            _logger.error("Invalid QSO")
            raise ValidationError(_("Invalid QSO"))

        adif_utility = self.env["ham.utility.adif"]

        extra_fields = {
            "EQSL_USER": username,
            "EQSL_PSWD": password,
        }
        adif_content = adif_utility.generate_adif_header(extra_fields=extra_fields)

        extra_fields = {
            "APP_EQSL_QTH_NICKNAME": qth_nickname
        }
        adif_content += adif_utility.generate_adif_qso(qso, extra_fields=extra_fields)

        data = {
            "EQSL_USER": username,
            "EQSL_PSWD": password,
        }

        files = {
            "Filename": ("file.adi", adif_content)
        }

        url = EQSL_API_UPLOAD_QSO

        response = requests.post(url=url, files=files)

        if response.status_code != 200:
            _logger.error("Unable to upload QSO to eQSL. Status code %d: %s" % (
                response.status_code, response.content
            ))
            _logger.error("Data: %s" % data)
            raise ValidationError(_("Unable to upload QSO to eQSL"))

        if b"error" in response.content.lower():
            root = etree.fromstring(response.content.decode(), parser=etree.HTMLParser(remove_comments=True))
            html_content = etree.tostring(root)
            raw_message = BeautifulSoup(html_content, "lxml").text.strip()
            message = "\n".join([x.strip() for x in raw_message.splitlines() if x.strip()])

            _logger.error("Error publishing QSO: %s" % message)
            _logger.error("Data: %s" % data)
            raise ValidationError("%s.\n%s" % (_("Error publishing QSO"), message))
