FROM python:3.8-alpine3.14 AS base
RUN apk add --no-cache --upgrade \
    libpng \
    tiff \
    libffi \
    libpq \
    fontconfig \
    freetype \
    giflib \
    jpeg libjpeg-turbo \
    zlib \
    lcms2 \
    libwebp \
    tcl \
    libimagequant \
    fribidi \
    harfbuzz \
    openjpeg \
    openssl \
    libevent \
    libxml2 \
    libldap \
    libusb \
    libxslt \
    libsasl \
    expat \
    mpdecimal \
    readline \
    ncurses \
    libmagic

FROM base AS base-dev
RUN apk add --no-cache --upgrade \
    build-base swig rust cargo \
    libpng-dev \
    tiff-dev \
    libffi-dev \
    postgresql-dev \
    fontconfig-dev \
    freetype-dev \
    giflib-dev \
    jpeg-dev libjpeg-turbo-dev \
    zlib-dev \
    lcms2-dev \
    libwebp-dev \
    tcl-dev \
    libimagequant-dev \
    fribidi-dev \
    harfbuzz-dev \
    openjpeg-dev \
    openssl-dev \
    libevent-dev \
    libxml2-dev \
    openldap-dev \
    libusb-dev \
    libxslt-dev \
    expat-dev \
    mpdecimal-dev \
    readline-dev \
    ncurses-dev \
    file-dev

FROM base-dev AS wkhtmltopdf
RUN apk add --no-cache --upgrade \
      git \
      libxv libxv-dev \
      libxinerama libxinerama-dev \
      libxcursor libxcursor-dev \
      libxrandr libxrandr-dev \
      libxi libxi-dev \
      alsa-lib alsa-lib-dev \
      gstreamer gstreamer-dev \
      gst-plugins-base gst-plugins-base-dev \
      gst-plugins-good \
      gst-plugins-ugly \
      gst-plugins-bad gst-plugins-bad-dev \
    && git config --global advice.detachedHead false
RUN git clone --depth=1 --branch=0.12.6 https://github.com/wkhtmltopdf/wkhtmltopdf.git /build/wkhtmltopdf
RUN ( cd /build/wkhtmltopdf \
    && git submodule init \
    && git submodule update --depth=1 )
RUN ( mkdir /build/qt-build \
    && cd /build/qt-build \
    && /build/wkhtmltopdf/qt/configure \
      -prefix /build/qt-patched \
      -nomake demos \
      -nomake examples \
      -confirm-license \
      -release \
      -opensource \
      -static \
      -largefile \
      -svg \
      -webkit \
      -javascript-jit \
      -qt-zlib \
      -qt-libtiff \
      -qt-libpng \
      -qt-libmng \
      -qt-libjpeg \
      -fontconfig )

FROM base-dev AS venv
ENV MAKEFLAGS=6
RUN python3 -m venv /venv
RUN /venv/bin/pip3 install --no-binary :all: \
    "Babel==2.6.0" \
    "chardet==3.0.4" \
    "decorator==4.4.2" \
    "docutils==0.16" \
    "ebaysdk==2.1.5"
RUN /venv/bin/pip3 install --no-binary :all: \
    "freezegun==0.3.15" \
    "gevent==20.9.0" \
    "greenlet==0.4.17" \
    "idna==2.8" \
    "Jinja2==2.11.2"
RUN /venv/bin/pip3 install --no-binary :all: \
    "libsass==0.18.0" \
    "lxml==4.6.1" \
    "MarkupSafe==1.1.0" \
    "num2words==0.5.6" \
    "ofxparse==0.19"
RUN /venv/bin/pip3 install --no-binary :all: \
    "passlib==1.7.2" \
    "Pillow==8.1.2" \
    "polib==1.1.0" \
    "psutil==5.6.6" \
    "psycopg2==2.8.6"
RUN /venv/bin/pip3 install --no-binary :all: \
    "pydot==1.4.1" \
    "pyopenssl==19.0.0" \
    "PyPDF2==1.26.0" \
    "pyserial==3.4" \
    "python-dateutil==2.7.3"
RUN /venv/bin/pip3 install --no-binary :all: \
    "python-ldap==3.2.0" \
    "python-stdnum==1.13" \
    "pytz==2019.3" \
    "pyusb==1.0.2" \
    "qrcode==6.1"
RUN /venv/bin/pip3 install --no-binary :all: \
    "reportlab==3.5.59" \
    "requests==2.22.0" \
    "vobject==0.9.6.1" \
    "Werkzeug==0.16.1" \
    "xlrd==1.2.0"
RUN /venv/bin/pip3 install --no-binary :all: \
    "XlsxWriter==1.1.2" \
    "xlwt==1.3.*" \
    "zeep==3.4.0"
RUN /venv/bin/pip3 install --no-binary :all: \
    "openpyxl==3.0.9" \
    "python-magic==0.4.25" \
    "geopy==2.2.0" \
    "mock==4.0.3"

FROM venv AS venv-project
RUN /venv/bin/pip3 install --no-binary :all: \
    "openpyxl==3.0.9" \
    "python-magic==0.4.25" \
    "geopy==2.2.0"

FROM base AS odoo
COPY --from=venv-project /venv /venv
RUN mkdir /odoo /addons /data
RUN addgroup -g 1000 odoo \
    && adduser -h /odoo -s /bin/false -S -D -H -u 1000 odoo \
    && chown -R 1000:1000 /data
USER 1000:1000
ENTRYPOINT ["/venv/bin/python3", "/odoo/odoo-bin"]