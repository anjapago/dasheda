# Based off example at https://community.plotly.com/t/running-dash-app-in-docker-container/16067
# Helm charts based off of https://docs.bitnami.com/tutorials/deploy-go-application-kubernetes-helm/

# eval $(minikube docker-env)

## With Docker

# docker build -t michael/dash-test:0.1.0 .
# docker images
# docker run -p 8050:8050 michael/dash-test:0.1.0
# docker stop michael/dash-test:0.1.0

##  Run with helm and minikube

# minikube start --driver=hyperv
# helm install dash-release ./helm-chart/dash-test/
# kubectl get pods

## To find port numbers
# minikube service list

## Enter the address into your browser

# helm delete dash-release

## To find errors in deployment

# kubectl get pods

FROM python:3.6

USER root

WORKDIR /app

ADD ./app.py /app

RUN pip install --trusted-host pypi.python.org dash==1.16.3 Flask
# RUN pip install --trusted-host pypi.python.org -r requirements.txt

# EXPOSE 8050

ENV NAME World

CMD ["python", "app.py"]

