from States import States
from Hardware import Hardware 
from Properties import Properties
from Etch_Mode import Etch_Mode
from Motor import Motor
from GPIO_Pins import GPIO_Pins

# selection states
auto_select = "auto"
paper_select = "paper"
menu_select = "menu"
stop_select = "stop"
reset_select = "reset"
paper_mode = "papermode"

# the current state of the ui (hovering over)
hovering = auto_select

# function is called whenever the lcd needs to be updated
def print_lcd():
  Hardware.lcd.clear()
  Hardware.lcd.setCursor(0,0)
  if hovering == auto_select: # when hovering over auto calibrate mode
    Hardware.lcd.printout("Auto")
    Hardware.lcd.setCursor(0,1)
    Hardware.lcd.printout("Calibrate")
  elif hovering == paper_select: # when hovering over paper position calibrate mode
    Hardware.lcd.printout("Paper Position")
    Hardware.lcd.setCursor(0,1)
    Hardware.lcd.printout("Calibrate")
  elif hovering == menu_select: # when hovering over main menu selection
    Hardware.lcd.printout("Main Menu")	
  elif hovering == stop_select: # when hovering over stop selection
    Hardware.lcd.printout("Stop")		
  elif hovering == reset_select: # when hovering over reset selection
    Hardware.lcd.printout("Reset")
  elif hovering == paper_mode: # after selecting paper position calibrate mode
    Hardware.lcd.printout("Move to ")
    Hardware.lcd.setCursor(0,1)
    Hardware.lcd.printout("Corner")
  Hardware.lcd.setCursor(11,1)
  if Properties.power > 10:
      Hardware.lcd.printout("{:.1f}".format(Properties.power) + "W ")
  else:
      Hardware.lcd.printout(" {:.1f}".format(Properties.power) + "W")

# Calibration Mode Class, is called by Driver as inputs are used
class Calibrate_Mode:
  # is called by Menu_Mode class when switching to calibrate mode, 
  def initialize():
    global hovering 
    hovering = auto_select #sets initial hover to be over auto calibration mode
    print_lcd()

  # called by driver when y rotary is turned up
  def y_rotary_up(): 
    if hovering == paper_mode:
      Etch_Mode.y_rotary_up() # calls the same movement as etch mode when in paper position calibration mode

   # called by driver when y rotary is turned downward
  def y_rotary_down():
    if hovering == paper_mode: 
      Etch_Mode.y_rotary_down() # calls the same movement as etch mode when in paper position calibration mode

  # called by driver when x rotary is turned up
  def cal_cycle_next(): 
    global hovering
    if hovering == auto_select: # when hovering over auto calibrate mode
      hovering = paper_select
    elif hovering == paper_select: # when hovering over paper position calibrate mode
      hovering = menu_select
    elif hovering == menu_select: # when hovering over main menu selection
      hovering = stop_select	
    elif hovering == stop_select: # when hovering over stop selection
      hovering = reset_select	
    elif hovering == reset_select: # when hovering over reset selection
      hovering = auto_select
    elif hovering == paper_mode: # after selecting paper position calibrate mode
      Etch_Mode.x_rotary_up()
    print_lcd()	

  # called by driver when x rotary is turned down
  def cal_cycle_prev(): 
    global hovering
    if hovering == auto_select: # when hovering over auto calibrate mode
      hovering = reset_select
    elif hovering == paper_select: # when hovering over paper position calibrate mode
      hovering = auto_select
    elif hovering == menu_select: # when hovering over main menu selection
      hovering = paper_select
    elif hovering == stop_select: # when hovering over stop selection
      hovering = menu_select
    elif hovering == reset_select: # when hovering over reset selection
      hovering = stop_select	
    elif hovering == paper_mode: # after selecting paper position calibrate mode
      Etch_Mode.x_rotary_down()
    
    print_lcd()

  # when x rotary is pressed, this is called by driver
  def cal_select(): 
    global hovering
    if hovering == menu_select: # main menu hover
      Properties.current_state = States.menu_state
      Hardware.lcd.clear()
      Hardware.lcd.printout("Calibration")
      return
    elif hovering == auto_select: # auto calibration hover
      Etch_Mode.calibration()
    elif hovering == paper_select: # paper calibration hover
      hovering = paper_mode
      Hardware.h_enable()
    
      # move until limit switch is pressed for y
      while Hardware.pi.read(GPIO_Pins.sw_y) == 0:
        Motor.forwardStep(Motor.y_motor, 1)
  
      # move until limit switch is pressed for x
      while Hardware.pi.read(GPIO_Pins.sw_x) == 0:
        Motor.backwardStep(Motor.x_motor, 1)

      Properties.pos_x = 0
      Properties.pos_y = 0

      # move to the current corner of page
      Motor.moveToPosX(Properties.max_x,1)
      Motor.moveToPosY(-Properties.max_y,1)
    
    elif hovering == paper_mode: # paper position mode
      # saves max values
      Properties.max_x = Properties.pos_x
      Properties.max_y = Properties.pos_y
      # sets correct axis position
      Properties.pos_x = Properties.max_x/2
      Properties.pos_y = Properties.max_y/2
      hovering = paper_select
      Hardware.h_disable()
      
    print_lcd()
    
 # when y rotary is pressed, this is called by driver     
  def cal_back():
    global hovering
    if hovering == paper_mode: # when in paper posotion calibration mode
      hovering = paper_select
      Hardware.disable()
    else:
      Properties.current_state = States.menu_state
      Hardware.lcd.clear()
      Hardware.lcd.printout("Calibration")
