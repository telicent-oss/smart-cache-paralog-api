FROM python:3.12-alpine

ENV PATH="${PATH}:/home/worker/.local/bin/"

#to build confluent kafka
RUN sed -i -e 's/v3\.18/edge/g' /etc/apk/repositories \
    && apk upgrade --update-cache --available
RUN apk add gcc g++ librdkafka-dev

COPY start.sh . 
RUN chmod +x start.sh
COPY paralog_server.py .
COPY ies_functions.py .
COPY decode_token.py .
COPY config.py .
COPY errors.py . 
COPY jena.py . 
COPY logger.py .
COPY queries.py . 
COPY utils.py .
COPY ies4.ttl .
COPY iesExtensions.ttl .
COPY pyproject.toml .

RUN pip3 install pip-tools \
    && python3 -m piptools compile -o requirements.txt pyproject.toml \
    && pip3 install -r requirements.txt --no-cache-dir

CMD ["sh", "start.sh"]