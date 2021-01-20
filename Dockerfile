FROM python:3.7
LABEL maintainer="joseph.lefebvre@etu.imt-lille-douai.fr"
CMD ["/bin/sh"]
RUN pip install luigi
EXPOSE 8082/tcp
ENTRYPOINT ["luigid"]