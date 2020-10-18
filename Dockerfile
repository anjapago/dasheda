FROM python:3.6

USER root

WORKDIR /app

ADD ./app.py /app

RUN pip install --trusted-host pypi.python.org dash==1.16.3 Flask pandas numpy plotly==4.11.0 geopy
# RUN pip install --trusted-host pypi.python.org -r requirements.txt

# EXPOSE 8050

ENV NAME World

CMD ["python", "app.py"]

