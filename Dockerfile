FROM python:3.7.4-slim-buster AS deps

# Install the Python deps (common across worker & web server, for now)
RUN mkdir /app
WORKDIR /app

# Install Firefox deps (and curl, xvfb, vnc). Debian Buster has Firefox v68;
# we'll install its dependencies and hope they satisfy _our_ Firefox version.
RUN apt-get update \
    && bash -c 'apt-get install -y --no-install-recommends $(apt-cache depends firefox-esr | awk "/Depends:/{print\$2}")' \
    && apt-get install --no-install-recommends -y \
        curl \
        wget \
        xauth \
        xvfb \
        xz-utils \
        bzip2 \
        postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Install Firefox. It's a separate step so it's easier to resume docker build.
RUN curl -L https://download-installer.cdn.mozilla.net/pub/firefox/releases/71.0/linux-x86_64/en-US/firefox-71.0.tar.bz2 \
        | tar jx -C /opt \
        && ln -s /opt/firefox/firefox /usr/bin/firefox

# Install geckodriver. It's a separate step so it's easier to resume docker build.
RUN curl -L https://github.com/mozilla/geckodriver/releases/download/v0.26.0/geckodriver-v0.26.0-linux64.tar.gz \
        | tar zx -C /usr/bin/ \
        && chmod +x /usr/bin/geckodriver

# Install the Python deps we use for integration tests.
#
# Integration tests don't rely on the Django stack, and that makes this
# Dockerfile compile faster and cache better.
#RUN pip install psycopg2-binary capybara-py selenium minio

FROM deps AS pydeps

COPY requirements.txt /app/
RUN pip install -r /app/requirements.txt

COPY requirements.api.txt /app/
RUN pip install -r /app/requirements.api.txt

FROM pydeps as base

COPY autoscrape/ /app/autoscrape/

# Flask API server
COPY autoscrape-server.py /app/

# Build AutoScrape WWW
# Install Node.js

RUN \
  cd /tmp && \
  curl https://nodejs.org/dist/v12.16.1/node-v12.16.1-linux-x64.tar.xz -o node-js.tar.xz && \
  tar xvf node-js.tar.xz && \
  rm -f node-js.tar.xz && \
  cp -rfv node-v*/* / && \
  rm -rf /tmp/node-* && \
  npm install -g npm && \
  printf '\n# Node.js\nexport PATH="node_modules/.bin:$PATH"' >> /root/.bashrc

# Remember: this is a git submodule!
COPY www/ /app/www/
RUN echo REACT_APP_API_HOST="http://localhost:5000" >> .env
RUN cd /app/www && npm install && npm run download-hextractor && npm run build

FROM autoscrape-worker-deps AS autoscrape-worker
CMD [ "celery", "-A", "autoscrape.tasks", "worker", "--loglevel=info" ]

FROM autoscrape-server-deps AS autoscrape-server
EXPOSE 5000
CMD [ "python", "autoscrape-server.py" ]

FROM rabbitmq:3.7.8-management as rabbitmq
EXPOSE 15672

