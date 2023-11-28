FROM python:3.9.18

COPY --from=verilator/verilator:v5.016 /usr/local/bin /usr/local/bin
COPY --from=verilator/verilator:v5.016 /usr/local/share/verilator /usr/local/share/verilator

RUN apt-get update \
    && DEBIAN_FRONTEND=noninteractive \
    && apt-get install --no-install-recommends -y \
    ccache \
    perl-doc

ARG developer
ARG uid
ENV developer $developer
ENV uid $uid
ARG gid
ENV gid $gid

RUN adduser $developer && \
        usermod -u $uid $developer
RUN groupmod $developer -g $gid

USER $developer
WORKDIR /home/$developer/

COPY requirements.txt requirements.txt
RUN python3 -m venv venv
RUN /home/$developer/venv/bin/pip install "cocotb>=1.8,<1.9" "pytest>=7.4,<7.5"
RUN /home/$developer/venv/bin/pip install -r requirements.txt

CMD su - $developer