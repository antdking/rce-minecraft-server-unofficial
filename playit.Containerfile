FROM debian:bookworm-slim
RUN apt update && apt install -y curl gpg net-tools dumb-init bind9-dnsutils python3 python3-pip

RUN curl -SsL https://playit-cloud.github.io/ppa/key.gpg | gpg --dearmor | tee /etc/apt/trusted.gpg.d/playit.gpg >/dev/null
RUN echo "deb [signed-by=/etc/apt/trusted.gpg.d/playit.gpg] https://playit-cloud.github.io/ppa/data ./" | tee /etc/apt/sources.list.d/playit-cloud.list

RUN apt update && apt install -y playit

RUN pip install --break-system-packages mcstatus

RUN playit version

WORKDIR /app
COPY playit_healthcheck.py ./

HEALTHCHECK --timeout=3s CMD python3 /app/playit_healthcheck.py
