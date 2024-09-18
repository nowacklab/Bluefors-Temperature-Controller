# bftc
Driver for Bluefors Temperature Controller.

chan1 is 50 K thermometer.

chan4 is 4 K thermometer.

chan5 is still thermometer.

heat1 is heat switch.

heat3 is still heater.
 
# Example code

```py
tempcontroller = bftc()
tempcontroller.heat3.PID(0.2, 250, 0) #Set PID settings for still heater
tempcontroller.heat3.ramp_rate = 0.1 #Set ramp rate for still heater in K/min
tempcontroller.heat3.ramp(4, tempcontroller.chan5) #Ramp still plate temperature to 4 K
tempcontroller.heat1.power = 0.1 #Adjust heat switch current
tempcontroller.chan1.T #Get temperature of 50 K stage
```

```py
#Print messages from thermometers as they arrive. Adapted from Bluefors example code.
def callback_print(client, userdata, msg):
    data = json.loads(msg.payload)
    print('Message: \n{}'.format(json.dumps(data, indent=2)))
subscribe.callback(callback_print, 'channel/measurement/listen', hostname='172.31.255.10')
```
