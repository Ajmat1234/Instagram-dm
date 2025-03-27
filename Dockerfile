# सिर्फ जरूरी packages install करें (Debian-based)
FROM node:20-bullseye

# Apt cache को write करने से बचें
RUN echo 'Acquire::Check-Valid-Until "false";' > /etc/apt/apt.conf.d/99no-check-valid-until && \
    echo 'Acquire::Check-Date "false";' >> /etc/apt/apt.conf.d/99no-check-valid-until

# Chrome install करने का नया तरीका
RUN mkdir -p /tmp/chrome && cd /tmp/chrome && \
    wget https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb && \
    dpkg -x google-chrome-stable_current_amd64.deb . && \
    mv ./opt/google/chrome/chrome /usr/bin/google-chrome-stable && \
    rm -rf /tmp/chrome

# Python dependencies
RUN python3 -m pip install --no-cache-dir --upgrade pip && \
    python3 -m pip install --no-cache-dir virtualenv
