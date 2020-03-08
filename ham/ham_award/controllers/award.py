import logging

from odoo import http
from odoo.addons.portal.controllers.portal import pager as portal_pager
from odoo.http import route, request

_logger = logging.getLogger(__name__)

QSO_PAGE_SIZE = 10


class AwardController(http.Controller):

    @route(
        route="/ham_award/public/award",
        type="http",
        auth="public",
        methods=["GET"],
        csrf=True,
        website=True
    )
    def public_award(self):
        award_obj = request.env["ham_award.award"].sudo()

        award_ids = award_obj.search([
            ("public", "=", True)
        ])

        values = {
            "award_ids": award_ids
        }

        return request.render("ham_award.template_award_public_awards", values)

    @route(
        route=[
            "/ham_award/public/award/<int:awardid>",
            "/ham_award/public/award/<int:awardid>/page/<int:page>"
        ],
        type="http",
        auth="public",
        methods=["GET"],
        csrf=True,
        website=True
    )
    def public_award_qso(self, awardid, page=1):
        award_obj = request.env["ham_award.award"].sudo()
        qso_obj = request.env["ham_award.qso"].sudo()

        award_id = award_obj.search([
            ("id", "=", awardid),
            ("public", "=", True),
        ], limit=1)

        qso_count = qso_obj.search_count([
            ("award_id", "=", award_id.id)
        ])

        country_count = len(qso_obj.read_group(
            domain=[("award_id", "=", award_id.id)],
            fields=["country_id"],
            groupby=["country_id"]
        ))

        qso_ids = qso_obj.search(
            args=[("award_id", "=", award_id.id)],
            offset=((page - 1) * QSO_PAGE_SIZE),
            limit=QSO_PAGE_SIZE
        )

        pager = portal_pager(
            url="/ham_award/public/award/%d" % award_id.id,
            total=qso_count,
            page=page,
            step=QSO_PAGE_SIZE
        )
        values = {
            "award_id": award_id,
            "qso_count": qso_count,
            "country_count": country_count,
            "qso_ids": qso_ids,
            "pager": pager
        }

        return request.render("ham_award.template_award_public_award_qsos", values)

    @route(
        route="/ham_award/private/award",
        type="http",
        auth="user",
        methods=["GET"],
        csrf=True,
        website=True
    )
    def list(self, **data):
        operator_obj = request.env["ham_award.operator"]
        award_obj = request.env["ham_award.award"]

        partner_id = request.env.user.partner_id

        operator_id = operator_obj.search([
            ("partner_id.id", "=", partner_id.id)
        ])

        award_ids = award_obj.search([
            ("operator_ids", "in", [operator_id.id])
        ])

        values = {
            "error": {},
            "error_message": [],
            "page_name": "award_list",
            "award_ids": award_ids
        }

        return request.render("ham_award.template_award_list", values)

    @route(
        route="/ham_award/private/award/<int:awardid>",
        type="http",
        auth="user",
        methods=["GET"],
        csrf=True,
        website=True
    )
    def single(self, awardid=0, **data):
        operator_obj = request.env["ham_award.operator"]
        award_obj = request.env["ham_award.award"]
        upload_obj = request.env["ham_award.upload"]

        partner_id = request.env.user.partner_id

        operator_id = operator_obj.search([
            ("partner_id.id", "=", partner_id.id)
        ])

        award_id = award_obj.search([
            ("id", "=", awardid),
            ("operator_ids", "in", [operator_id.id]),
        ])

        upload_ids = upload_obj.search([
            ("award_id.id", "in", award_id.ids),
            ("operator_id.id", "=", operator_id.id)
        ])

        values = {
            "error": {},
            "error_message": [],
            "page_name": "award_single",
            "award_id": award_id,
            "upload_ids": upload_ids
        }

        return request.render("ham_award.template_award_single", values)
