import time
import math
import threading

from States import States
from Motor import Motor
from Etch_Mode import Etch_Mode
from Properties import Properties
from Hardware import Hardware

# tracks whether the axis has been drawn
axis_drawn = False

# test variables for debugging
y_scale = 1
mm_conv = 1.5

# properties that make calculation of math points more readable
max_x = Properties.max_x
max_y = Properties.max_y

lower_x = -max_x / 2
lower_y = -max_y / 2

upper_x = max_x / 2
upper_y = max_y / 2 

# selection states
linear_select = "linear"
quadratic_select = "quad"
circle_select = "circle"

m_linear_select = "mlinear"
b_linear_select = "blinear"

a_quad_select = "aquad"
b_quad_select = "bquad"
c_quad_select = "cquad"

r_circle_select = "rcircle"

linear_selected = "print linear"
quadratic_selected = "print quad"
circle_selected = "print circ"

printing_mode = "printing"

hovering = linear_select

# values
display_value = 0
m_linear = 0
b_linear = 0
a_quad = 0
b_quad = 0
c_quad = 0
r_circle = 0

# helper function that is called when backing out of the menu 
def switch_state(target_state):
  # switches state
  Properties.current_state = target_state
  # initial print statement
  if target_state == States.etch_state:
    Etch_Mode.initialize()
  elif target_state == States.menu_state:
    Hardware.lcd.clear()
    Hardware.lcd.printout("Math Mode")
  elif target_state == States.math_state:   
    Math_Mode.initialize()

# updates lcd screen with the current information based on what the menu is hovering over
def print_lcd():
  global hovering
  # first clear
  Hardware.lcd.clear()
  Hardware.lcd.setCursor(0,0)

  # then print linear, quadratic, or circle when hovering over those initial function choices
  if hovering == linear_select:
    Hardware.lcd.printout("Linear")
  elif hovering == quadratic_select:
    Hardware.lcd.printout("Quadratic")
  elif hovering == circle_select:
    Hardware.lcd.printout("Circle")
  else: 
    # otherwise, print the letter at the top that is current being given a value
    if hovering == m_linear_select:
      Hardware.lcd.printout("m")
    elif hovering == b_linear_select or hovering == b_quad_select: 
      Hardware.lcd.printout("b")
    elif hovering == a_quad_select:
      Hardware.lcd.printout("a")
    elif hovering == c_quad_select:
      Hardware.lcd.printout("c")
    elif hovering == r_circle_select:
      Hardware.lcd.printout("r")
    elif hovering == linear_selected or hovering == quadratic_selected or hovering == circle_selected:
      # after one of the functions of selected, print the final calibrated(?) screen and stop
      Hardware.lcd.printout("Calibrated?")
      return
    elif hovering == printing_mode:  
      # if it is currently printing a function, print "Printing"
      Hardware.lcd.printout("Printing")
    
    if hovering != printing_mode and hovering != linear_selected and hovering != quadratic_selected and hovering != circle_selected: 
      Hardware.lcd.setCursor(0,1)
      Hardware.lcd.printout(display_value) 
  Hardware.lcd.setCursor(11,1)
  if Properties.power > 10:
      Hardware.lcd.printout("{:.1f}".format(Properties.power) + "W ")
  else:
      Hardware.lcd.printout(" {:.1f}".format(Properties.power) + "W")

# called in the class later, cycles forward through the menu
def math_cycle_next():
    global hovering, display_value
    if hovering == linear_select:
      hovering = quadratic_select  
    elif hovering == quadratic_select:
      hovering = circle_select
    elif hovering == circle_select:
      hovering = linear_select
    else:
      display_value += 1
    print_lcd()  

# called in the class later, cycles back through the menu
def math_cycle_prev():
  global hovering, display_value
  if hovering == linear_select:
    hovering = circle_select  
  elif hovering == quadratic_select:
    hovering = linear_select
  elif hovering == circle_select:
    hovering = quadratic_select
  else:
    display_value -= 1
  print_lcd()   

# increments the display value by 10, called later by class
def increment_up_10():
  global display_value
  if hovering != linear_select and hovering != quadratic_select and hovering != circle_select:
    display_value += 10
    print_lcd()  
    
# increments the display value by -10, called later by class
def increment_down_10():
  global display_value
  if hovering != linear_select and hovering != quadratic_select and hovering != circle_select:
    display_value += -10
    print_lcd()

# selects the current hover and moves deeper in ui. if over a variable (m,b,a,b,c,r) save the display value to variable 
def math_select():
  global hovering, display_value, m_linear, b_linear, a_quad, b_quad, c_quad, r_circle
  # linear selections
  if hovering == linear_select:
    hovering = m_linear_select
    display_value = m_linear
  elif hovering == quadratic_select:
    hovering = a_quad_select
    display_value = a_quad
  elif hovering == circle_select:
    hovering = r_circle_select
    display_value = r_circle
  elif hovering == m_linear_select:
    m_linear = display_value
    display_value = b_linear
    hovering = b_linear_select
  elif hovering == b_linear_select:
    b_linear = display_value
    display_value = m_linear
    hovering = m_linear_select
  elif hovering == linear_selected:
    hovering = printing_mode

    # line is selected and printing, update lcd and plot
    print_lcd()
    Math_Mode.linear(m_linear, b_linear)

  # quadratic selections
  elif hovering == a_quad_select:
    a_quad = display_value
    display_value = b_quad
    hovering = b_quad_select  
  elif hovering == b_quad_select:
    b_quad = display_value
    display_value = c_quad
    hovering = c_quad_select
  elif hovering == c_quad_select:
    c_quad = display_value
    display_value = a_quad
    hovering = a_quad_select
  elif hovering == quadratic_selected:
    hovering = printing_mode

    # quadratic is selected and printing, update lcd and plot
    print_lcd()
    Math_Mode.quadratic(a_quad, b_quad, c_quad) 

  # circle selections
  elif hovering == r_circle_select:
    r_circle = display_value
  elif hovering == circle_selected:
    hovering = printing_mode

    # circle is selected, update the lcd and plot
    print_lcd()
    Math_Mode.circle(r_circle)    
  print_lcd()

# goes back and moves one level out of ui
def math_back():
  global hovering, display_value, m_linear, b_linear, a_quad, b_quad, c_quad, r_circle
  print("selected")
  if hovering == linear_select or hovering == quadratic_select or hovering == circle_select:
    # if at the outermose level, go back to menu
    switch_state(States.menu_state)
    hovering = linear_select
  else:
    if hovering == m_linear_select:
      hovering = linear_select
    elif hovering == b_linear_select:
      hovering = m_linear_select
      display_value = m_linear  
    elif hovering == a_quad_select:
      hovering = quadratic_select
    elif hovering == b_quad_select:
      hovering = a_quad_select
      display_value = a_quad
    elif hovering == c_quad_select:
      hovering = b_quad_select
      display_value = b_quad
    elif hovering == r_circle_select:
      hovering = circle_select
    elif hovering == linear_selected or hovering == quadratic_selected or hovering == circle_selected:
      # if at the "calibrated?" screen, calibrate when go back
      Etch_Mode.calibration()

    print_lcd()

# when long press, use the selected variables to move to the selected screen
def math_long_x():
  global hovering, display_value, m_linear, b_linear, a_quad, b_quad, c_quad, r_circle
  if hovering == m_linear_select or hovering == b_linear_select:
    # if hovering over a linear variable

    # save the current value
    if hovering == m_linear_select:
      m_linear = display_value
    else:
      b_linear = display_value

    # move to the selected screen
    hovering = linear_selected
    
  elif hovering == a_quad_select or hovering == b_quad_select or hovering == c_quad_select:
    # if hovering over a quadratic variable

    # save the current value
    if hovering == a_quad_select:
      a_quad = display_value
    elif hovering == b_quad_select:
      b_quad = display_value
    else:
      c_quad = display_value

    # move to the selected screen
    hovering = quadratic_selected
    
  elif hovering == r_circle_select:
    # if hovering over a circle variable
    r_circle = display_value # save the current r
    hovering = circle_selected # move to the selected screen
  
  # after anything is selected, update lcd screen
  print_lcd()

# Math Mode Class, is called by driver after inputs and holds the main functions (linear, quadratic, circle)
class Math_Mode:
  # called when state is initially switched to math mode
  def initialize():
    global diplay_value, hovering
    print_lcd()
    hovering = linear_select
    display_value = 0
    Hardware.h_disable()

  # placeholder class functions, called by Driver, that call the local functions above after an input
  def x_rotary_up():
    math_cycle_prev()

  def x_rotary_down():
    math_cycle_next()
    
  def y_rotary_up():
    increment_down_10()
  
  def y_rotary_down():
    increment_up_10()     

  def x_press():
    math_select()
    
  def y_press():
    math_back()  
    
  def x_long_press():
    math_long_x()

  def y_long_press():
    return

  # LINEAR function
  def linear(m,b):
    global hovering
    Hardware.h_enable()

    # if not (0,0), move to (0,0)
    if Properties.pos_x != 0 or Properties.pos_y != 0:
      Motor.moveToPosX(0,1)
      Motor.moveToPosY(0,1)

    # draw axis if not already drawn
    if axis_drawn == False:
      Math_Mode.draw_axis()

    # adjust variables for scale
    m *= 1/y_scale
    b *= 1/y_scale 

    # find first point
    y_left = m * lower_x + b
    first_point = [0,0]

    if y_left > lower_y  and y_left < upper_y:
      # hits left first
      first_point[0] = lower_x
      first_point[1] = y_left
    else:
      if y_left < lower_y:
        # hits bottom first
        first_point[1] = lower_y
        first_point[0] = (first_point[1] - b)/m
      elif y_left > upper_y :
        # hits top first
        first_point[1] = upper_y 
        first_point[0] = (first_point[1] - b)/m  

    # find second point
    y_right = m * upper_x  + b
    second_point = [0,0]

    if y_right < upper_y  and y_right > lower_y :
      # hits right first
      second_point[0] = upper_x
      second_point[1] = y_right
    else:
      if y_right > upper_y :
        # hits top first
        second_point[1] = upper_y 
        second_point[0] = (second_point[1] - b)/m    
      elif y_right < lower_y :
        # hits bottom first
        second_point[1] = lower_y 
        second_point[0] = (second_point[1] - b)/m    
      

    # move to first point
    Motor.moveToPosX(first_point[0], 1)
    Motor.moveToPosY(first_point[1], 1)
    # toggle pen
    time.sleep(0.5)
    Etch_Mode.toggle_pen()
    time.sleep(0.5)
    # move to second point using slope function (moveToPoint)
    Motor.moveToPoint(second_point[0], second_point[1],2)
    # toggle pen
    time.sleep(0.5)
    Etch_Mode.toggle_pen()
    # hover back over the initial linear select screen
    hovering = linear_select
    print_lcd()
    
    Hardware.h_disable()

  # QUADRATIC function
  def quadratic(a,b,c):
    global hovering
    Hardware.h_enable()

    # check if the function is in the bounds at all, print and go back if not
    if (Math_Mode.check_in_bounds(a,b,c) == False):
      Hardware.lcd.clear()
      Hardware.lcd.printout("Exceeded")
      time.sleep(1)
      
      hovering = quadratic_select
      print_lcd()
      Hardware.h_disable()
      return

    # draw axis if not already drawn
    if axis_drawn == False:
      Math_Mode.draw_axis()

    # when the y_scale is different than the x-scale (for debugging and measurement)
    a *= 1/y_scale
    b *= 1/y_scale
    c *= 1/y_scale

    # updates the class variables that are in the motor class, used for calculation of slopes there
    Motor.a = a
    Motor.b = b
    Motor.c = c
    
    # find starting point and move to it
    left_y = a * lower_x * lower_x + b * lower_x + c
    first_point = [0,0]
    if left_y > upper_y:
      # hit top
      first_point[1] = upper_y - 1
      first_point[0] = math.ceil((-b - math.sqrt(b*b - 4 * a * (c - upper_y))) / (2 * abs(a)))
    elif left_y < lower_y:
      # hit bottom
      first_point[1] = lower_y + 1
      first_point[0] = math.ceil((-b + math.sqrt(b*b - 4 * a * (c - lower_y))) / (2 * a))
    else:
      # hit left
      first_point[0] = lower_x + 1
      first_point[1] = left_y 
      
    print("(" + str(first_point[0]) + "," + str(first_point[1]) + ")")  # debugging

    # move to first point
    Motor.moveToPosX(first_point[0],1)
    Motor.moveToPosY(first_point[1],1)  
    # toggle pen
    time.sleep(0.5)
    Etch_Mode.toggle_pen()
    time.sleep(0.5)
    # update the slope initially
    Motor.moving_slope = 2 * Motor.a * Properties.pos_x + Motor.b
    Motor.calculateFactors()
    
    # start threads
    x_thread = threading.Thread(target = Motor.moveWithSlopeX, args = ()) # moves x motor simultaneously
    y_thread = threading.Thread(target = Motor.moveWithSlopeY, args = ()) # moves y motor simultaneously
    slope_thread = threading.Thread(target = Motor.updateMovingSlopeQuad, args = ()) # updates slope / motor speeds simulatenously 
    
    x_thread.start()
    y_thread.start()
    slope_thread.start()
    
    x_thread.join()
    y_thread.join()  
    slope_thread.join()

    # fixes case in which the initial slope causes the plot to move out of bounds initially
    Motor.moving_slope = 0 

    # toggle pen to be back up
    time.sleep(0.5)
    Etch_Mode.toggle_pen()
    print("ended")
    # move back to function selection screen, hovering over quadratic
    hovering = quadratic_select
    print_lcd()
    
    Hardware.h_disable()
    return      

  # CIRCLE function
  def circle(r):
    global hovering
    Hardware.h_enable()

    # if the radius exceeds the upper limits of the x-axis, then cannot plot. print and return to selection
    if r > Properties.max_x/2:
      Hardware.lcd.clear()
      Hardware.lcd.printout("Exceeded")
      time.sleep(1)
      
      hovering = circle_select
      print_lcd()
      Hardware.h_disable()
      return

    # updates r value in Motor class for calculation there
    Motor.r = r

    # if axis is not already drawn, draw it
    if axis_drawn == False:
      Math_Mode.draw_axis()
  
    # find first point, pen down
    Motor.moveToPosX(r, 1)
    Motor.moveToPosY(0,1)
    # toggle pen
    time.sleep(0.5)
    Etch_Mode.toggle_pen()
    time.sleep(0.5)
    # set a high initial moving slope
    Motor.moving_slope = 50
    

    # start threads
    x_thread = threading.Thread(target = Motor.moveWithSlopeXCirc, args = ()) # move x motor simultaneously 
    y_thread = threading.Thread(target = Motor.moveWithSlopeYCirc, args = ()) # move y motor simultaneously 
    slope_thread = threading.Thread(target = Motor.updateMovingSlopeCirc, args = ()) # update slopes simultaenously
    
    x_thread.start()
    y_thread.start()
    slope_thread.start()
    
    x_thread.join()
    y_thread.join()
    slope_thread.join()
    
    Motor.deg = 0
    Motor.moving_slope = 0
    
    # end, pen up
    time.sleep(0.5)
    Etch_Mode.toggle_pen()
    
    
    hovering = circle_select
    print_lcd()
    Hardware.h_disable()
    
    return

  # draws the axis
  def draw_axis():
    global axis_drawn

    # make sure pen is up
    if Properties.pen_down: 
      Etch_Mode.toggle_pen()
      time.sleep(0.6)
      
    # x-axis
    Motor.moveToPoint(lower_x,0, 1)
    
    time.sleep(0.6)
    Etch_Mode.toggle_pen()
    time.sleep(0.6)
    
    Motor.moveToPoint(upper_x,0, 1)
    
    time.sleep(0.6)
    Etch_Mode.toggle_pen()
    time.sleep(0.6)

    # y-axis
    Motor.moveToPoint(0,0,1)
    Motor.moveToPoint(0,lower_y, 1)
    
    time.sleep(0.6)
    Etch_Mode.toggle_pen()
    time.sleep(0.6)

    Motor.moveToPoint(0,upper_y, 1)

    time.sleep(0.6)
    Etch_Mode.toggle_pen()

    # update boolean
    axis_drawn = True

  # for quadratic, checks if the given coefficients are within the bounds of the plot
  def check_in_bounds(a,b,c):
    x_pos = lower_x
    y_pos = -100000
    
    while x_pos < upper_x:
      y_pos = a * (x_pos * x_pos) + b * x_pos + c
      if abs(y_pos) < upper_y:
        print(str(y_pos) + " is within the bounds at x = " + str(x_pos))
        return  True
      x_pos += 1
    
    return False
      
    
