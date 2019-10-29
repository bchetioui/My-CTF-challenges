FROM debian:stretch-20180831
ARG DEBIAN_FRONTEND=noninteractive

# hardening
RUN chmod o-x /usr/bin/wall
RUN chmod o-rx /var/log /run/*
RUN sed -i 's/664/660/g' /var/lib/dpkg/info/base-files.postinst
RUN chmod 773 /tmp

# date
RUN ln -fs /usr/share/zoneinfo/Europe/Paris /etc/localtime
RUN dpkg-reconfigure -f noninteractive tzdata

RUN addgroup --gid 999 theoryofbe
RUN adduser --disabled-password --gecos '' --gid 999 --uid 999 theoryofbe

WORKDIR /home/theoryofbe

# node + npm
RUN apt update
RUN apt install -y curl gnupg
RUN apt install -y build-essential
RUN curl -sL https://deb.nodesource.com/setup_11.x  | bash -
RUN apt install -y nodejs

COPY ./package.json /home/theoryofbe

#npm
RUN npm install

RUN npm install express
RUN npm install sleep
RUN npm install puppeteer
RUN npm install request
RUN npm install --save body-parser

COPY ./index.html /home/theoryofbe
COPY ./check.html /home/theoryofbe
COPY ./app.js /home/theoryofbe
COPY ./public /home/theoryofbe/public

USER theoryofbe

EXPOSE 8080

ENV NAME World

CMD ["node", "app.js"]
