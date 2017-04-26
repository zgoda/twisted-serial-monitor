# Serial Monitor with Twisted

This is an example of routing serial communication to network protocols (websocket, MQTT, etc).

## Usage instructions

* install dependencies, best done in virtualenv so it's a matter of issuing simple `pip install -U -r requirements.txt` in your terminal
* connect the device you want to monitor to your computer
* update `service/settings.py` with your own configuration: serial port to listen to and MQTT settings (host and port)
* run the application with `python server.py`, if you want to debug using pdb/ipdb then export `DEBUG` variable to your environment (eg. `DEBUG=1 python server.py`)
* to test websocket channel open `http://127.0.0.1:8080` in browser
