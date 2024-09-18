#Code for Bluefors temperature controller

import json
import time
import paho.mqtt.publish as publish
import paho.mqtt.subscribe as subscribe

class bftc:
    
    _label = 'Bluefors Temperature Controller'
    _strip = '\r'
    _channel_names = {
        1: '50K',
        2: '4K',
        5: 'Still'
    }
    _heater_names = {
        1: 'Heatswitch Still',
        3: 'Still-heater'
    }

    def __init__(self, host = '172.31.255.10'):

        # Make channel objects
        for c, n in self._channel_names.items():
            setattr(self, 'chan%i' %c, bftcChannel(c, n))
            
         # Make heater objects
        for c, n in self._heater_names.items():
            setattr(self, 'heat%i' %c, bftcHeater(c, n))

        # Set properties to get/set all params
        params = ['R', 'T', 'status', *self.chan1._insets]
        for p in params:
            setattr(self, '_' + p, {}) # empty dictionary for later
            setattr(bftc, p,
                property(fget = eval("lambda self: self._get_param('%s')" %p),
                    fset = eval('lambda self, v: self._set_param("%s", v)' %p)
                )
            )
        #Set heatswitch power to default 0.108 W (60 mA)
        self.heat1.power = 0.108

    def __getstate__(self):
        self._save_dict = {
            'chan%i' %i: getattr(self, 'chan%i' %i)
            for i in self._channel_names.keys()
        }

        return self._save_dict

#
#
#
#
#

class bftcChannel:
    
    _label = 'LakeshoreChannel'
    _num = 0
    #_strip = '\r'
    _insets = ['rez', 'enabled', 'angle', 'settings_nr', 'timestamp','datetime', 'reactance', 'magnitude', 'status_flags', 'imz']
    
    def __init__(self, num, label):
        '''
        Arguments:
            num: Channel number.
            label: Channel label.
        '''
        self._num = num
        self._label = label
        
        counter = 0
        while counter == 0:
            msg = subscribe.simple('channel/measurement/listen', msg_count=1, hostname='172.31.255.10')
            jsonstr = json.loads(msg.payload)
            if self._num == int(self.read_value(jsonstr, 'channel_nr')):
                self.rez = float(self.read_value(jsonstr, 'rez'))
                self.status = self.read_value(jsonstr, 'status')
                self.angle = float(self.read_value(jsonstr, 'angle'))
                #self.T = float(self.read_value(jsonstr, 'temperature'))
                self.settings_nr = int(self.read_value(jsonstr, 'settings_nr'))
                self.timestamp = float(self.read_value(jsonstr, 'timestamp'))
                #self.R = float(self.read_value(jsonstr, 'resistance'))
                #self._num = int(self.read_value(jsonstr, 'channel_nr'))
                self.datetime = self.read_value(jsonstr, 'datetime')
                self.reactance = float(self.read_value(jsonstr, 'reactance'))
                self.magnitude = float(self.read_value(jsonstr, 'magnitude'))
                self.status_flags = self.read_value(jsonstr, 'status_flags')
                self.imz = float(self.read_value(jsonstr, 'imz'))
                counter = 1

        # Properties for all the channel settings
        #for i, var in enumerate(self._insets):
        #    setattr(bftcChannel, var, property(
        #        fget = eval('lambda self: self._get_inset()[%i]' %i),
        #        fset = eval('lambda self, value: self._set_inset(%s = value)'
        #        %var)
        #    ))

    def read_value(self, endpoint, key):
        if key in endpoint:
            value = endpoint[key]
        else:
            value = "Key not found"
        return value

    @property
    def R(self):
        '''
        Get the resistance (R) of this input channel.
        '''
        counter = 0
        while counter == 0:
            msg = subscribe.simple('channel/measurement/listen', msg_count=1, hostname = '172.31.255.10')
            jsonstr = json.loads(msg.payload)
            if self._num == int(self.read_value(jsonstr, 'channel_nr')):
                self.R = float(self.read_value(jsonstr, 'resistance'))
                counter = 1
        return self._R
    
    @property
    def T(self):
        counter = 0
        while counter == 0:
            msg = subscribe.simple('channel/measurement/listen', msg_count=1, hostname = '172.31.255.10')
            jsonstr = json.loads(msg.payload)
            if self._num == int(self.read_value(jsonstr, 'channel_nr')):
                temper = self.read_value(jsonstr, 'temperature')
                #setattr(self, 'T', temper)
                counter = 1
        return temper

#
#
#
#
        
class bftcHeater:
    
    def __init__(self, num, label):
        '''
        Arguments:
            num: Heater number.
            label: Heater label.
        '''
        self._num = num
        self._label = label
        self.ramp_rate = 1
        self.heater_status = True
        
        publish.single('heater/update/in', json.dumps({"heater_nr": self._num, "active": True}), hostname='172.31.255.10')
   
    def __getstate__(self):
        '''Get state of heater'''
        #Publish message that doesn't change heater settings
        publish.single('heater/update/in', json.dumps({"heater_nr": self._num}), hostname='172.31.255.10')
        #Receive message with settings
        msg = subscribe.simple('heater/update/out', hostname='172.31.255.10')
        jsonstr = json.loads(msg.payload)
        #self.status = self.read_value(jsonstr, 'status')
        #self.PID = self.read_value(jsonstr, 'control_algorithm_settings')
        #self._label = self.read_value(jsonstr, 'name')
        #self.P = float(self.read_value(jsonstr, 'power'))
        #self.relay_mode = self.read_value(jsonstr, 'relay_mode')
        #self.tts = self.read_value(jsonstr, 'target_temperature_shown')
        #self._num = int(self.read_value(jsonstr, 'heater_nr'))
        #self.R = float(self.read_value(jsonstr, 'resistance'))
        #self.datetime = self.read_value(jsonstr, 'datetime')
        #self.control_algorithm = float(self.read_value(jsonstr, 'control_algorithm'))
        #self.max_power = float(self.read_value(jsonstr, 'max_power'))
        #self.pid_mode = int(self.read_value(jsonstr, 'pid_mode'))
        #self.heater_status = bool(self.read_value(jsonstr, 'active'))
        #self.target_temperature = float(self.read_value(jsonstr, 'target_temperature'))
        #self.temperature = float(self.read_value(jsonstr, 'setpoint'))
        #self.relay_status = self.read_value(jsonstr, 'relay_status')
        
        self._save_dict = {
            #'status': self.status,
            'PID': self.PID,
            'ramp rate': self.ramp_rate,
            'heater status': self.heater_status,
            'setpoint': self.temperature
        }
        #return self._save_dict
        return print('State: \n{}'.format(json.dumps(jsonstr)), '\nramp rate:', self.ramp_rate)
    
    def ramp(self, toramp, channel):
        '''
        Set the controller to ramp from fromramp to toramp
        '''
        temporary = float(channel.T)
        while temporary + self.ramp_rate < toramp:
            temporary = temporary + self.ramp_rate
            self.temperature = temporary
            time.sleep(60)
            
        while temporary - self.ramp_rate > toramp:
            temporary = temporary - self.ramp_rate
            self.temperature = temporary
            time.sleep(60)
        
        self.temperature = toramp
        while float(channel.T)>(toramp+0.01) or float(channel.T)<(toramp-0.01):
            time.sleep(60)

    @property
    def ramp_rate(self):
        '''
        Returns ramp rate in kelvin per minute.
        '''
        return self.ramp_rate
    
    #@ramp_rate.setter
    def ramp_rate(self, rate):
        '''
        Set the ramp rate in kelvin per minute.
        '''
        self.ramp_rate = rate
        
    @property
    def heater_status(self):
        '''Returns the status of the heater'''
        msg = subscribe.simple('heater/listen', hostname='172.31.255.10')
        jsonstr = json.loads(msg.payload)
        active = bool(self.read_value(jsonstr, 'active'))
        return active
    
    @heater_status.setter
    def heater_status(self, active):
        '''Turns heater on or off'''
        active = bool(active)
        publish.single('heater/update/in', json.dumps({"heater_nr": self._num, "active":active, 'power':0}), hostname='172.31.255.10')
        #msg = subscribe.simple('heater/update/out', hostname='172.31.255.10')
        #jsonstr = json.loads(msg.payload)
        #Error handling
        #if self.read_value(jsonstr, 'active') == active:
        #    return self.read_value(jsonstr, 'active')
        #else:
        #    return "Error in bftcHeater.heater_status"

    def read_value(self, endpoint, key):
        '''
        Reads value of a given key in a message.
        '''
        if key in endpoint:
            value = endpoint[key]
        else:
            value = "Key not found"
        return value
    
    @property
    def temperature(self):
        '''
        Returns temperature setpoint. Identical to the setpoint getter.
        '''
        msg = subscribe.simple('heater/listen', hostname='172.31.255.10')
        jsonstr = json.loads(msg.payload)
        setpoint = float(self.read_value(jsonstr, 'setpoint'))
        return setpoint
    
    @temperature.setter
    def temperature(self, temp):
        '''
        Set the current setpoint. Identical to the setpoint setter.
        '''
        publish.single('heater/update/in', json.dumps({"heater_nr": self._num, 'active':True, 'pid_mode': 1, 'setpoint': temp}), hostname='172.31.255.10')
        #msg=subscribe.simple('heater/update/out', hostname='172.31.255.10')
        #jsonstr = json.loads(msg.payload)
        #if self.read_value(jsonstr, 'status') == True:
            #subscribe.callback(callback_set_temp, 'channel/measurement/listen', hostname)
        #    pass
        #else:
        #    print("Error in bftcHeater.temperature")
        
        #setpoint is the actual target temperature
    
    @property
    def setpoint(self):
        '''
        Returns temperature setpoint. Identical to the temperature getter.
        '''
        msg = subscribe.simple('heater/listen', hostname='172.31.255.10')
        jsonstr = json.loads(msg.payload)
        setpoint = float(self.read_value(jsonstr, 'setpoint'))
        return setpoint
    
    @setpoint.setter
    def setpoint(self, temp):
        '''
        Set the current setpoint. Identical to the temperature setter.
        '''
        self.temperature=temp
    
    @property
    def power(self):
        '''
        Gets the applied manual power in Watts. Doesn't work when heater is in PID mode.
        '''
        publish.single('heater/update/in', json.dumps({"heater_nr": self._num}), hostname='172.31.255.10')
        msg=subscribe.simple('heater/update/out', hostname='172.31.255.10')
        jsonstr = json.loads(msg.payload)
        newpower = float(self.read_value(jsonstr, 'power'))
        #setattr(self, 'P', newpower)
        return float(self.read_value(jsonstr, 'power'))

    @power.setter
    def power(self, power):
        '''
        Sets the applied manual power in Watts. Turns off PID mode.
        '''
        publish.single('heater/update/in', json.dumps({"heater_nr": self._num, 'pid_mode': 0, 'power': power}), hostname='172.31.255.10')
    
    @property
    def PID_mode(self):
        '''
        Returns 1 when the heater is in PID mode, and 0 when it is in manual mode.
        '''
        publish.single('heater/update/in', json.dumps({"heater_nr": self._num}), hostname='172.31.255.10')
        msg=subscribe.simple('heater/update/out', hostname='172.31.255.10')
        jsonstr = json.loads(msg.payload)
        newpower = float(self.read_value(jsonstr, 'pid_mode'))
        return self.read_value(jsonstr, 'pid_mode')

    @PID_mode.setter
    def PID_mode(self, mode):
        '''
        Sets the heater to PID mode (1) or manual mode (0).
        '''
        publish.single('heater/update/in', json.dumps({"heater_nr": self._num, 'pid_mode': mode}), hostname='172.31.255.10')   
    
    def PID(self, P=0.1, I=1, D=0):
        '''
        Set the values for proportional, integral, and derivative for PID.
        '''
        dictionary = {"heater_nr": self._num, "control_algorithm_settings": {"proportional": P, "integral": I, "derivative": D}}
        publish.single('heater/update/in', json.dumps(dictionary), hostname='172.31.255.10')
        #msg=subscribe.simple('heater/update/out', hostname='172.31.255.10')