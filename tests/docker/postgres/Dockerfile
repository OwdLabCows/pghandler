FROM postgres:latest

# Time Zone
ENV TZ Asia/Tokyo

# update
RUN apt-get update

# Language
RUN apt-get install -y locales locales-all
RUN locale-gen ja_JP.UTF-8
ENV LANG ja_JP.UTF-8
ENV LANGUAGE ja_JP:ja
ENV LC_ALL ja_JP.UTF-8