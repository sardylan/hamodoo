FROM hamodoo-venv:latest AS prod
COPY odoo/odoo /odoo/odoo
CMD rm -rf /odoo/odoo/addons/test*
COPY odoo/odoo-bin /odoo

COPY odoo/addons/auth_signup /odoo/addons/auth_signup
COPY odoo/addons/base_setup /odoo/addons/base_setup
COPY odoo/addons/base_import /odoo/addons/base_import
COPY odoo/addons/bus /odoo/addons/bus
COPY odoo/addons/contacts /odoo/addons/contacts
COPY odoo/addons/digest /odoo/addons/digest
COPY odoo/addons/http_routing /odoo/addons/http_routing
COPY odoo/addons/mail /odoo/addons/mail
COPY odoo/addons/portal /odoo/addons/portal
COPY odoo/addons/resource /odoo/addons/resource
COPY odoo/addons/social_media /odoo/addons/social_media
COPY odoo/addons/utm /odoo/addons/utm
COPY odoo/addons/web /odoo/addons/web
COPY odoo/addons/web_editor /odoo/addons/web_editor
COPY odoo/addons/web_tour /odoo/addons/web_tour
COPY odoo/addons/website /odoo/addons/website

COPY web/web_advanced_search /odoo/addons/web_advanced_search
COPY web/web_domain_field /odoo/addons/web_domain_field
COPY web/web_group_expand /odoo/addons/web_group_expand
COPY web/web_listview_range_select /odoo/addons/web_listview_range_select
COPY web/web_m2x_options /odoo/addons/web_m2x_options
COPY web/web_no_bubble /odoo/addons/web_no_bubble
COPY web/web_refresher /odoo/addons/web_refresher
COPY web/web_responsive /odoo/addons/web_responsive

COPY docker/odoo.patch /patch/
RUN patch --directory=/odoo -Np1 -i /patch/odoo.patch

COPY ham /addons/

COPY run.sh /odoo
RUN chmod 0755 /odoo/run.sh

VOLUME /data

RUN groupadd -g 1000 odoo \
    && useradd --home-dir /data --gid 1000 --no-create-home --shell /bin/false --uid 1000 odoo \
    && chown -R 1000:1000 /data

ENTRYPOINT ["/bin/bash", "/odoo/run.sh"]
