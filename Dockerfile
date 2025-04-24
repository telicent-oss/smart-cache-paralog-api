FROM telicent/telicent-python3.12 AS builder

USER user

COPY ./pyproject.toml .
RUN python3 -m pip install --upgrade pip && \
    python3 -m pip install pip-tools && \
    python3 -m piptools compile -o requirements.txt pyproject.toml && \
    python3 -m pip install -r requirements.txt --no-cache-dir

FROM telicent/telicent-python3.12
COPY --from=builder /home/user/app-venv/ /home/user/app-venv/

COPY sbom.json /opt/telicent/sbom/
WORKDIR /app
COPY paralog/ ./paralog
COPY ./pyproject.toml .

CMD ["fastapi", "run", "paralog/app.py"]
