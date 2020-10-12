# dasheda

Based off example at https://community.plotly.com/t/running-dash-app-in-docker-container/16067
Helm charts based off of https://docs.bitnami.com/tutorials/deploy-go-application-kubernetes-helm/

# Dash App Instructions

Run the following do ensure that your docker images will be located in a place
where minikube can find them.
- ```eval $(minikube docker-env)```

To run the app with docker.
- ```docker build -t michael/dash-test:0.1.0 .```
- ```docker run -p 8050:8050 michael/dash-test:0.1.0```

To check the available images in docker.
- ```docker images```

To stop the app with docker.
- ```docker stop michael/dash-test:0.1.0```

Run the following to run the docker image with minikube.
- ```minikube start --driver=hyperv```
- ```helm install dash-release ./helm-chart/dash-test/```
 
Then retrieve the ip address and port number for accessing the app. It is in the URL column.
- ```minikube service list``` 

Enter the URL in your browser and you will see the app.

To stop the pod, run.
- ```helm delete dash-release1```

To check active pods.
- ```kubectl get pods```
