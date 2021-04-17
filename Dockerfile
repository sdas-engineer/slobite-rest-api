FROM python:3.8-slim-buster


# COPY ./requirements.txt /requirements.txt
COPY ./Pipfile /Pipfile
# COPY ./Pipfile.lock /Pipfile.lock

# Install system packages required by Wagtail and Django.
RUN apt-get update --yes --quiet && apt-get install --yes --quiet --no-install-recommends \
    build-essential \
    libpq-dev \
    libmariadbclient-dev \
    libjpeg62-turbo-dev \
    zlib1g-dev \
    libwebp-dev \
    netcat \
 && rm -rf /var/lib/apt/lists/*

# RUN pip install -r /requirements.txt
RUN pip install --no-cache-dir -q 'pipenv==2020.11.15' && pipenv install --deploy --system --skip-lock


RUN mkdir /backend
COPY ./ /backend
WORKDIR /backend


RUN chmod +x /backend/entrypoint.sh


CMD ["/backend/entrypoint.sh"]