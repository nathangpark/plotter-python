import time
import threading
from pigpio_encoder.rotary import Rotary

from Hardware import Hardware
from Properties import Properties
from GPIO_Pins import GPIO_Pins
from States import States
from Motor import Motor
from Etch_Mode import Etch_Mode
from Menu_Mode import Menu_Mode
from Math_Mode import Math_Mode
from Calibrate_Mode import Calibrate_Mode
from G_Code import G_Code
from G_Functions import G_Functions
from adc import ADC

# helper variables for button press function
sw_pressed1 = False
sw_pressed2 = False
ready_for_press = True
press_start_time = time.time()
long_press_time = 1

# placeholder functions (these are called when the corresponding inputs are pressed)
def x_rotary_up(counter):
  if Properties.current_state == States.menu_state:
    Menu_Mode.menu_cycle_prev()
  elif Properties.current_state == States.etch_state:
    Etch_Mode.y_rotary_up()
  elif Properties.current_state == States.math_state:
    Math_Mode.x_rotary_up()
  elif Properties.current_state == States.calibrate_state:
    Calibrate_Mode.cal_cycle_prev()
  elif Properties.current_state == States.g_state:
    G_Code.x_rotary_up()  


def y_rotary_up(counter):
  if Properties.current_state == States.menu_state:
    empty_function()
  elif Properties.current_state == States.etch_state:
    Etch_Mode.x_rotary_up()
  elif Properties.current_state == States.math_state:
    Math_Mode.y_rotary_up()
  elif Properties.current_state == States.calibrate_state:
    Calibrate_Mode.y_rotary_up()
  elif Properties.current_state == States.g_state:
    G_Code.y_rotary_up() 

def x_rotary_down(counter):
  if Properties.current_state == States.menu_state:
    Menu_Mode.menu_cycle_next()
  elif Properties.current_state == States.etch_state:
    Etch_Mode.y_rotary_down()
  elif Properties.current_state == States.math_state:
    Math_Mode.x_rotary_down()  
  elif Properties.current_state == States.calibrate_state:
    Calibrate_Mode.cal_cycle_next()  
  elif Properties.current_state == States.g_state:
    G_Code.x_rotary_down() 

def y_rotary_down(counter):
  if Properties.current_state == States.menu_state:
    empty_function()
  elif Properties.current_state == States.etch_state:
    Etch_Mode.x_rotary_down()
  elif Properties.current_state == States.math_state:
    Math_Mode.y_rotary_down()
  elif Properties.current_state == States.calibrate_state:
    Calibrate_Mode.y_rotary_down()
  elif Properties.current_state == States.g_state:
    empty_function()

def x_press():
  if Properties.current_state == States.menu_state:
    Menu_Mode.menu_select()
  elif Properties.current_state == States.etch_state:
    Etch_Mode.x_press()
  elif Properties.current_state == States.math_state:
    Math_Mode.x_press()
  elif Properties.current_state == States.calibrate_state:
    Calibrate_Mode.cal_select()
  elif Properties.current_state == States.g_state:
    G_Code.x_press()   

def y_press():
  if Properties.current_state == States.menu_state:
    Menu_Mode.menu_back()
  elif Properties.current_state == States.etch_state:
    Etch_Mode.y_press()
  elif Properties.current_state == States.math_state:
    Math_Mode.y_press()  
  elif Properties.current_state == States.calibrate_state:
    Calibrate_Mode.cal_back()
  elif Properties.current_state == States.g_state:
    G_Code.y_press()     

def placeholder_simultaneous_press_callback():
  if Properties.current_state == States.menu_state:
    empty_function()
  elif Properties.current_state == States.etch_state:
    Etch_Mode.both_press()
    
def x_long_press():
  if Properties.current_state == States.math_state:
    Math_Mode.x_long_press()

def y_long_press():
  if Properties.current_state == States.math_state:
    Math_Mode.y_long_press()

# button press check, determines the input of the user, used to deal with simultaneous press and long/short press without rotary package callbacks
def button_press():
  global sw_pressed1, sw_pressed2, ready_for_press, press_start_time
  if not sw_pressed1 and not sw_pressed2 and ready_for_press:
    if not Hardware.pi.read(GPIO_Pins.sw1):
      sw_pressed1 = True
      press_start_time = time.time()
    elif not Hardware.pi.read(GPIO_Pins.sw2):
      sw_pressed2 = True
      press_start_time = time.time()
    
  if sw_pressed1 and ready_for_press:
    if not Hardware.pi.read(GPIO_Pins.sw2):
      # simulataneous
      placeholder_simultaneous_press_callback()
      ready_for_press = False
    elif Hardware.pi.read(GPIO_Pins.sw1):
      # x was pressed
      x_press()
      sw_pressed1 = False
      ready_for_press = False
    elif time.time() - press_start_time > long_press_time:
      # x was long pressed
      x_long_press()
      sw_pressed1 = False
      ready_for_press = False
  elif sw_pressed2 and ready_for_press:
    if not Hardware.pi.read(GPIO_Pins.sw1):
      # simultaneous
      placeholder_simultaneous_press_callback()
      ready_for_press = False
    elif Hardware.pi.read(GPIO_Pins.sw2):
      # y was short pressed
      y_press()
      sw_pressed2 = False
      ready_for_press = False
    elif time.time() - press_start_time > long_press_time:
      # y was long pressed
      y_long_press()
      sw_pressed2 = False
      ready_for_press = False
  if not ready_for_press and Hardware.pi.read(GPIO_Pins.sw1) and Hardware.pi.read(GPIO_Pins.sw2):
    sw_pressed1 = False
    sw_pressed2 = False
    ready_for_press = True

# helper functions

def empty_function():
  # empty
  return

# rotary encoder set callback
rotary1 =  Rotary(GPIO_Pins.clk1,GPIO_Pins.dt1,GPIO_Pins.dt1)
rotary1.setup_rotary(
  up_callback= x_rotary_up,
  down_callback = x_rotary_down,
)
rotary1.setup_switch(
  sw_short_callback = empty_function
)
rotary2 = Rotary(GPIO_Pins.clk2,GPIO_Pins.dt2,GPIO_Pins.dt1)
rotary2.setup_rotary(
  up_callback= y_rotary_up,
  down_callback = y_rotary_down,
)
rotary2.setup_switch(
  sw_short_callback = empty_function
)

# execution

Properties.current_state = States.menu_state # sets current state to main menu
Hardware.setup() # initializes the pins
Hardware.h_disable() # disables the current flowing to the motors if any
Menu_Mode.menu_print() # updates the screen with the main menu print
adc_thread = threading.Thread(target = ADC.run, args = ()) 
adc_thread.start();

try:
  while True:
    button_press() # needs to be called constantly to check button inputs without callbacks
    time.sleep(0.1)
    
# when program stops
except KeyboardInterrupt:
  Hardware.h_disable() # stop motor current
  Hardware.pi.stop() # close pi object
  Hardware.lcd.noDisplay() # removes characters from lcd display
  Hardware.lcd.setRGB(0,0,0) # turns lcd screen color from white to off (black)
  
