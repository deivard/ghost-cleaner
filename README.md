# Ghost Cleaner

## Prerequisites
Keyboard module (https://pypi.org/project/keyboard/)
```
pip install keyboard
```
NumPy
```
pip install numpy
```


## Running the simulator
Run the simulator with 1 cleaner, and post the locations to the default base url + api route (http://127.0.0.1:8000/)
```
python simulator.py [OPTION]...
```

### Options
--cleaners <br/>
&nbsp;&nbsp;&nbsp;&nbsp;Number of simultaneous cleaners to simulate. Default is: 1.

--baseurl <br/>
&nbsp;&nbsp;&nbsp;&nbsp;Specify the base url for the api. Default is: http://127.0.0.1:8000/

### Example
Run the simulator with 10 simultaneous cleaners and send their locations to https://snowcleanassist.herokuapp.com/api/location
```
python simulator.py --cleaners=10 --baseurl="https://snowcleanassist.herokuapp.com/"
```