FROM python:3.7
LABEL luigid
CMD ["/bin/sh"]
RUN pip install
EXPOSE 8082/tcp
ENTRYPOINT ["luigid --remove_delay 3600"]