# dasheda

Based off example at https://community.plotly.com/t/running-dash-app-in-docker-container/16067
	and https://medium.com/@megah_f/build-a-covid-19-map-with-python-and-plotly-dash-91a9fe58dfde
	and https://plotly.com/python/choropleth-maps/
Helm charts based off of https://docs.bitnami.com/tutorials/deploy-go-application-kubernetes-helm/

# Dash App Instructions

Run the following do ensure that your docker images will be located in a place
where minikube can find them.
- ```eval $(minikube docker-env)```

To run the app with docker.
- ```docker build -t michael/dash-test:0.1.0 .```
- ```docker run -p 8050:8050 --name dash_test michael/dash-test:0.1.0```

To check the available images in docker.
- ```docker images```

To check the available containers in docker.
- ```docker container ls```

To stop the app with docker.
- ```docker container stop dash_test```

To remove the app with docker.
- ```docker container rm dash_test```

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
