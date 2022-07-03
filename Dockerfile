FROM python:3.10-bullseye AS base
ENV DEBIAN_FRONTENT=noninteractive
RUN apt update \
    && apt -y dist-upgrade \
    && apt -y install \
      patch \
      libpng16-16 \
      libtiff5 \
      libffi7 \
      libpq5 \
      libfontconfig1 \
      libfreetype6 \
      libgif7 \
      libjpeg62-turbo \
      zlib1g \
      liblcms2-2 \
      libwebp6 \
      libtcl8.6 \
      libimagequant0 \
      libfribidi0 \
      libharfbuzz0b \
      libopenjp2-7 \
      libssl1.1 \
      libevent-2.1-7 \
      libxml2  \
      libldap-2.4-2 \
      libusb-0.1-4 libusb-1.0-0 \
      libxslt1.1 \
      libsasl2-2 \
      libexpat1 \
      libmpdec3 \
      libreadline8 \
      libncurses6 libncursesw6 \
      libmagic1 \
    && rm -R /var/lib/apt/*

FROM base AS base-dev
ENV DEBIAN_FRONTENT=noninteractive
RUN apt update \
    && apt -y dist-upgrade \
    && apt -y install \
      build-essential automake autoconf libtool pkg-config cmake swig rustc cargo \
      libpng-dev \
      libtiff-dev \
      libffi-dev \
      libpq-dev \
      libfontconfig1-dev \
      libfreetype-dev \
      libgif-dev \
      libjpeg-dev \
      zlib1g-dev \
      liblcms2-dev \
      libwebp-dev \
      tcl-dev \
      libimagequant-dev \
      libfribidi-dev \
      libharfbuzz-dev \
      libopenjp2-7-dev \
      libssl-dev \
      libevent-dev \
      libxml2-dev \
      libldap2-dev \
      libusb-dev libusb-1.0-0-dev \
      libxslt1-dev \
      libsasl2-dev \
      libexpat1-dev \
      libmpdec-dev \
      libreadline-dev \
      libncurses-dev \
      libmagic-dev

FROM base-dev AS venv
COPY odoo/requirements.txt requirements-odoo.txt
COPY web/requirements.txt requirements-web.txt
COPY ham/requirements.txt requirements-ham.txt
COPY requirements.txt requirements.txt
ENV MAKEFLAGS=8
RUN python3 -m venv /venv
RUN /venv/bin/pip3 install --upgrade pip setuptools \
    && /venv/bin/pip3 install \
      --requirement requirements-odoo.txt \
      --requirement requirements-web.txt \
      --requirement requirements-ham.txt \
      --requirement requirements.txt

FROM base AS odoo
RUN apt update \
    && apt -y dist-upgrade \
    && apt -y install wget \
    && wget "https://github.com/wkhtmltopdf/packaging/releases/download/0.12.6.1-2/wkhtmltox_0.12.6.1-2.bullseye_amd64.deb" \
    && wget "https://github.com/jgm/pandoc/releases/download/2.18/pandoc-2.18-1-amd64.deb" \
    && ( dpkg -i *.deb; apt -y install -f ) \
    && rm -Rf /var/lib/apt/* *.deb
COPY --from=venv /venv /venv
RUN mkdir /odoo /addons /data

FROM odoo AS dev
RUN groupadd -g 1000 odoo \
    && useradd --home-dir /odoo --gid 1000 --no-create-home --shell /bin/false --uid 1000 odoo \
    && chown 1000:1000 /odoo /addons /data
USER 1000:1000
ENTRYPOINT ["/venv/bin/python3", "/odoo/odoo-bin"]

FROM odoo AS prod
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
COPY web/web_notify /odoo/addons/web_notify
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
