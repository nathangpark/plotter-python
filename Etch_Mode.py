import pigpio
import rgb1602
import time

from States import States
from Hardware import Hardware
from Motor import Motor
from Properties import Properties
from GPIO_Pins import GPIO_Pins

# parameters
fast_turn = 8
slow_turn = 1
rot_per_turn = fast_turn
steps_down = 18
hold_all_input = False

# Etch-A-Sketch Mode Class, holds the functionality of inputs when in Etch-A-Sketch Mode
class Etch_Mode:
  # called by Menu_Mode class when switching to Etch Mode
  def initialize():
    global hold_all_input, rot_per_turn, fast_turn, slow_turn
    hold_all_input = False
    Etch_Mode.both_press()
    Etch_Mode.print_lcd()
    Hardware.h_disable()
    rot_per_turn = slow_turn

  # when called, this updates the lcd to the current state of the ui
  def print_lcd():
    Hardware.lcd.clear()
    Hardware.lcd.setCursor(0,0)
    if hold_all_input: # when in wait mode
      Hardware.lcd.printout("Wait Mode")
    else: # otherwise, print to the first line
 
      if Properties.pen_down: # for printing pen is up/down
        Hardware.lcd.printout("Pen down")
      else:
        Hardware.lcd.printout("Pen up")

      # always print at the top right the speed (rot_per_turn)
      Hardware.lcd.setCursor(15,0)
      Hardware.lcd.printout(str(rot_per_turn))
      
    Hardware.lcd.setCursor(11,1)
    if Properties.power > 10:
        Hardware.lcd.printout("{:.1f}".format(Properties.power) + "W ")
    else:
        Hardware.lcd.printout(" {:.1f}".format(Properties.power) + "W")

  # this calibration is called everywhere, and is the auto calibration. 
  def calibration():
    Hardware.lcd.clear()
    Hardware.lcd.printout("Calibrating...")

    # enable current running through motors
    Hardware.h_enable()

    # move until limit switch is pressed for y
    while Hardware.pi.read(GPIO_Pins.sw_y) == 0:
      Motor.forwardStep(Motor.y_motor, 1)

    # move until limit switch is pressed for x
    while Hardware.pi.read(GPIO_Pins.sw_x) == 0:
      Motor.backwardStep(Motor.x_motor, 1)

    # sets that position as 0
    Properties.pos_x = 0
    Properties.pos_y = 0

    # move to the right halfway of max_x
    Motor.moveToPosX(Properties.max_x/2,1)

    # move down halfy of max_y
    Motor.moveToPosY(-Properties.max_y/2,1)

    # set this position as the origin
    Properties.pos_x = 0
    Properties.pos_y = 0

    # disable current running through motors
    Hardware.h_disable()
 
  # this is the "universal" toggle pen function, called by math mode class and this class
  def toggle_pen():
    for i in range(steps_down): # run steps_down times
      if (Properties.pen_down): # if the pen is already down, move up (forward) at 1/5 speed
        Motor.forwardStep(Motor.z_motor, 5)
      else:   # if the pen is up, move down (backward) at 1/5 speed
        Motor.backwardStep(Motor.z_motor,5)
        time.sleep(0.01)
    Properties.pen_down = not Properties.pen_down # update boolean variable  

  # called by driver when x rotary encoder is turned "up", which moves the position right left
  def x_rotary_up():
    global rot_per_turn, pos_x, hold_all_input
     # if in wait mode, do nothing
    if hold_all_input:
      return

    # run rot_per_turn times every turn
    for i in range(rot_per_turn):
      # if the x-limit switch is pressed, set coordinate and do nothing
      if Hardware.pi.read(GPIO_Pins.sw_x) == 1:
        Properties.pos_x = -Properties.max_x/2
        return
      # otherwise, execute step
      Motor.backwardStep(Motor.x_motor, 1)
    #print("x: " + str(Properties.pos_x)) # print statement for debugging

  # called by driver when x rotary encoder is turned "down", which moves the position right
  def x_rotary_down():
    global rot_per_turn, pos_x, hold_all_input
    # if in wait mode, do nothing
    if hold_all_input:
      return
    # run rot_per_turn times every turn
    for i in range(rot_per_turn):
      # if the x upper limit is reached, do nothing
      if Properties.pos_x >= Properties.max_x/2:
        return
      # otherwise, execute the step
      Motor.forwardStep(Motor.x_motor, 1)
    #print("x: " + str(Properties.pos_x)) # print statement for debugging

  # called by driver when y rotary encoder is turned "up", which move the position up
  def y_rotary_up():
    global rot_per_turn, pos_y, hold_all_input
    # if in wait mode, do nothing
    if hold_all_input:
      return
    # run rot_per_turn times every turn
    for i in range(rot_per_turn):
      # if the y lower limit is reached, do nothing
      if Properties.pos_y <= -Properties.max_y/2:
        return
      
      # otherwise, execute the step
      Motor.backwardStep(Motor.y_motor, 1)
    #print("y: " + str(Properties.pos_y)) # print statement for debugging

  # called by driver when y rotary encoder is turned "down", which moves the position down
  def y_rotary_down():
    global rot_per_turn, pos_y, hold_all_input
    # if in wait mode, do nothing
    if hold_all_input:
      return
    # run rot_per_turn times every turn
    for i in range(rot_per_turn):
      # if the y-limit switch is pressed, save coordinate and do nothing
      if Hardware.pi.read(GPIO_Pins.sw_y) == 1:
        Properties.pos_y = Properties.max_y/2
        return
      # otherwise, execute the step
      Motor.forwardStep(Motor.y_motor,1)
    #print("y: " + str(Properties.pos_y)) # print statement for debugging

  # called by driver when x rotary encoder is short pressed, which toggles the pen
  def x_press():
    global steps_down, pen_down, sw_pressed1, hold_all_input
    # if in wait mode, do nothing
    if hold_all_input:
      return
    Etch_Mode.toggle_pen()
    Etch_Mode.print_lcd()
    
  # called by driver when y rotary encoder is short pressed, which toggles the speed
  def y_press():
    global rot_per_turn, fast_turn, slow_turn, hold_all_input
    # if in wait mode, go back into the menu
    if hold_all_input:
      Properties.current_state = States.menu_state

      # print the display in main menu when hovering over etch-a-sketch-mode
      Hardware.lcd.clear()
      Hardware.lcd.printout("Etch-A-Sketch")
      Hardware.lcd.setCursor(0,1)
      Hardware.lcd.printout("Mode")

      # update hold_all_input for other classes that use etch functions
      hold_all_input = False
      rot_per_turn = fast_turn

      return
    # toggle speed
    if rot_per_turn == fast_turn:
      rot_per_turn = slow_turn
    else:
      rot_per_turn = fast_turn

    # update screen
    Etch_Mode.print_lcd()

  # called by driver when both rotary encoders are pressed simultaneously, which would toggle wait mode here
  def both_press():
    global hold_all_input
    if Properties.pen_down:
      Etch_Mode.toggle_pen()
    hold_all_input = not hold_all_input  
    Etch_Mode.print_lcd()
    if hold_all_input:
      Hardware.h_disable()
    else:
      Hardware.h_enable()
