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
    def upload_qso(self, username: str = "", password: str = "", qth_nickname: str = "", adif_data: str = ""):
        if not username or not password or not qth_nickname:
            _logger.error("Invalid login data. Username: %s - Password: %s - QTH Nickname: %s" % (
                username, password, qth_nickname
            ))
            raise ValidationError(_("Invalid login data"))

        if not adif_data:
            _logger.error("Invalid login data. ADIF data: %s" % adif_data)
            raise ValidationError(_("Invalid data"))

        url = EQSL_API_UPLOAD_QSO

        data = {
            "EQSL_USER": username,
            "EQSL_PSWD": password,
            "APP_EQSL_QTH_NICKNAME": qth_nickname,
            "ADIFData": adif_data
        }

        response = requests.post(url=url, data=data)

        if response.status_code != 200:
            _logger.error("Unable to upload QSO to eQSL. Status code %d: %s" % (
                response.status_code, response.content
            ))
            _logger.error("Data: %s" % data)
            raise ValidationError(_("Unable to upload QSO to eQSL"))

        if b"error" in response.content.lower():
            root = etree.fromstring(response.content.decode())
            for comment in root.xpath('//comment()'):
                parent = comment.getparent()
                parent.remove(comment)

            html_content = etree.tostring(root)
            message = BeautifulSoup(html_content, "lxml").text.strip()

            _logger.error("Error publishing QSO: %s" % message)
            _logger.error("Data: %s" % data)
            raise ValidationError(_("Error publishing QSO"))
