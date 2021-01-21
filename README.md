# Luigi Project - IBD

As part of a universitary course, we choose to try and test a pipeline package.
Luigi is developped by Spotify and his purpose is ton address all the plumbing of batch processes.

## Setup Environnement

### Install Python (3.7 or higher)

https://www.python.org/downloads/ 

### Install luigi

```
pip install luigi
```

### Install others python dependencies

```
pip install pandas
pip install sqlalchemy
pip install gmplot
pip install osmapi
```
## Use luigi

### Run Central Luigi Scheduler

#### Directly on your computer
```
luigid
```

### Using docker (image from docker hub)

```
docker run --name luigid --restart always -p 8082:8082 -d tenshiroque/luigid:1.3
```

### Using docker (build image locally)

```
docker build -t luigid .
docker run --name luigid --restart always -p 8082:8082 -d luigid
```

### Run luigi modules

#### Run luigi modules locally
```
python -m luigi --module module_name TaskName --local-scheduler --remove_delay 3600
```

#### Run luigi modules in localhost Central scheduler
```
python -m luigi --module module_name TaskName --scheduler-host localhost --remove_delay 3600
```

#### Run luigi modules in distant Central scheduler (GKE)
```
python -m luigi --module module_name TaskName --scheduler-host 34.76.39.92 --remove_delay 3600
```

## Use Project

### Run project

#### Run all tasks about cinemas
```
python -m luigi --module cine_idf allEndTasks --scheduler-host localhost --scheduler-remove-delay 3600  
```

## References

https://cloud.google.com/kubernetes-engine/docs/tutorials/hello-app?hl=fr 
https://luigi.readthedocs.io/en/stable/index.html 
https://kapernikov.com/using-luigi-to-power-a-reporting-pipeline/ 
