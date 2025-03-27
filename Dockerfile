FROM python:3.11-slim
RUN apt-get update && apt-get install -y libnss3 libatk-bridge2.0-0 libxcomposite1 libxcursor1 libxdamage1 libxi6 libgbm1 libasound2 libxrandr2 fonts-liberation libappindicator3-1 libdbusmenu-glib4 libdbusmenu-gtk3-4 libx11-xcb1 libxtst6 xdg-utils libpangocairo-1.0-0 libatk1.0-0 libcups2 libgtk-4-dev libgraphene-1.0-0
