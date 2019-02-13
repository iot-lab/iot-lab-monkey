iot-lab-monkey

needs an installation of `iot-lab-client`

to launch integration tests on `devwww.iot-lab.info` :

```
pip install -r requirements.txt
pytest
```

you can modify the target master server using the IOTLAB_HOST environement variable, e.g.

IOTLAB_HOST=www.iot-lab.info/api pytest 
