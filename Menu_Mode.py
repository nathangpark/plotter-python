from Hardware import Hardware
from Properties import Properties
from States import States # very important here
from Etch_Mode import Etch_Mode
from Math_Mode import Math_Mode
from Calibrate_Mode import Calibrate_Mode
from G_Code import G_Code

# the initial screen will be hovering over the plotter section
hover_state = States.plotter_mode

# local function that class functions can call without instantiation, updates the lcd screen to show where in the ui the user is
def helper_print():
  Hardware.lcd.clear()
  Hardware.lcd.setCursor(0,0)
  if hover_state == States.etch_state:
    Hardware.lcd.printout("Etch-A-Sketch")
    Hardware.lcd.setCursor(0,1)
    Hardware.lcd.printout("Mode")
  elif hover_state == States.math_state:
    Hardware.lcd.printout("Math Mode")
  elif hover_state == States.calibrate_state:
    Hardware.lcd.printout("Calibrate")
  elif hover_state == States.plotter_mode:
    Hardware.lcd.printout("Plotter Mode")
  elif hover_state == States.stop_state:
    Hardware.lcd.printout("Stop")
  elif hover_state == States.reset_state:
    Hardware.lcd.printout("Reset")  
  elif hover_state == States.g_state:
    Hardware.lcd.printout("G-Code")  
  
  Hardware.lcd.setCursor(11,1)
  if Properties.power > 10:
      Hardware.lcd.printout("{:.1f}".format(Properties.power) + "W ")
  else:
      Hardware.lcd.printout(" {:.1f}".format(Properties.power) + "W")

# local function that is called to switch the state, used here to move into a given state that is selected
def switch_state(target_state):
  global hover_state
  Properties.current_state = target_state
  # initializations for each mode
  if Properties.current_state == States.etch_state:
    Etch_Mode.initialize()
  elif Properties.current_state == States.menu_state:
    Menu_Mode.initialize()   
  elif Properties.current_state == States.math_state:   
    Math_Mode.initialize()
  elif Properties.current_state == States.calibrate_state:   
    Calibrate_Mode.initialize()
  elif Properties.current_state == States.g_state:
    G_Code.initialize()
    
# MAIN MENU class, called by Driver, handles the operation of the main menu, including plotter submenus
class Menu_Mode:
  # when the user first enters the main menu, this is called to print and set initial states
  def initialize():
    global hover_state
    helper_print()
    hover_state = States.plotter_mode
    Hardware.h_disable()

  # allows the print function above to be called by other classes
  def menu_print():
    helper_print()

  # cycles forward through the ui, called by Driver when the x-rotary encoder is turned up
  def menu_cycle_next():
    global hover_state
    if hover_state == States.plotter_mode:
      hover_state = States.calibrate_state
    elif hover_state ==  States.calibrate_state:
      hover_state = States.stop_state
    elif hover_state == States.stop_state:
      hover_state = States.reset_state
    elif hover_state == States.reset_state:
      hover_state = States.plotter_mode 
    elif hover_state == States.etch_state:
      hover_state = States.math_state
    elif hover_state == States.math_state:
      hover_state = States.g_state
    elif hover_state == States.g_state:
      hover_state = States.etch_state
    helper_print()

  # cycles back through the ui, called by Driver when the x-rotary encoder is turned down
  def menu_cycle_prev():
    global hover_state
    if hover_state == States.plotter_mode:
      hover_state = States.reset_state
    elif hover_state ==  States.calibrate_state:
      hover_state = States.plotter_mode
    elif hover_state == States.stop_state:
      hover_state = States.calibrate_state
    elif hover_state == States.reset_state:
      hover_state = States.stop_state  
    elif hover_state == States.etch_state:
      hover_state = States.g_state
    elif hover_state == States.math_state:
      hover_state = States.etch_state
    elif hover_state == States.g_state:
      hover_state = States.math_state  
    helper_print()

  # selects the current hover and moves deeper into ui, called by Driver when the x rotary encoder is pressed
  def menu_select():
    global hover_state
    if hover_state == States.plotter_mode:
      hover_state = States.etch_state
      helper_print()
    else:
      switch_state(hover_state)

  # backs out of the current hover and moves out of the ui (only useful when in plotter submenu), called by Driver when the y rotary encoder is pressed
  def menu_back():
    global hover_state
    if hover_state == States.etch_state or hover_state == States.math_state or hover_state == States.g_state:
      hover_state = States.plotter_mode
      helper_print()
      
      
  
