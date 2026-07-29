# Builds Odoo 17.0 from this local checkout for local development with Docker.
FROM python:3.12-slim-bookworm

SHELL ["/bin/bash", "-o", "pipefail", "-c"]

RUN apt-get update && apt-get install -y --no-install-recommends \
        build-essential \
        curl \
        fontconfig \
        libfreetype6-dev \
        libfribidi-dev \
        libharfbuzz-dev \
        libjpeg-dev \
        libldap2-dev \
        liblcms2-dev \
        libpq-dev \
        libsasl2-dev \
        libssl-dev \
        libwebp-dev \
        libxml2-dev \
        libxslt1-dev \
        xfonts-75dpi \
        xfonts-base \
        zlib1g-dev \
    && curl -sSL -o /tmp/wkhtmltox.deb \
        "https://github.com/wkhtmltopdf/packaging/releases/download/0.12.6.1-3/wkhtmltox_0.12.6.1-3.bookworm_$(dpkg --print-architecture).deb" \
    && apt-get install -y --no-install-recommends /tmp/wkhtmltox.deb \
    && rm /tmp/wkhtmltox.deb \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /odoo

COPY requirements.txt /odoo/requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

COPY . /odoo

RUN useradd -ms /bin/bash odoo \
    && mkdir -p /var/lib/odoo \
    && chown -R odoo:odoo /var/lib/odoo /odoo

USER odoo

EXPOSE 8069 8072

ENTRYPOINT ["/odoo/odoo-bin"]
CMD ["-c", "/etc/odoo/odoo.conf"]
