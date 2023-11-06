FROM python:3.9.18

COPY --from=verilator/verilator:4.204 /usr/local/bin /usr/local/bin
COPY --from=verilator/verilator:4.204 /usr/local/share/verilator /usr/local/share/verilator

RUN apt-get update \
    && DEBIAN_FRONTEND=noninteractive \
    && apt-get install --no-install-recommends -y \
    ccache \
    perl-doc

RUN python3 -m venv venv
RUN /venv/bin/pip install cocotb==1.8.1

ARG developer
ARG uid
ENV developer $developer
ENV uid $uid
ARG gid
ENV gid $gid

RUN adduser $developer && \
        usermod -u $uid $developer

RUN groupmod $developer -g $gid
CMD su - $developer