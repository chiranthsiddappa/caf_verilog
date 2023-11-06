FROM python:3.9.18

COPY --from=verilator/verilator:4.204 /usr/local/bin /usr/local/bin
COPY --from=verilator/verilator:4.204 /usr/local/share/verilator /usr/local/share/verilator

RUN apt-get update \
    && DEBIAN_FRONTEND=noninteractive \
    && apt-get install --no-install-recommends -y \
    ccache

RUN python3 -m venv venv
RUN /venv/bin/pip install cocotb==1.8.1