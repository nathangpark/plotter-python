import pigpio
import time
import threading
import math

from Hardware import Hardware
from Properties import Properties
from GPIO_Pins import GPIO_Pins

# shortest delay possible without breaking the motor
delay = 0.00125

# this is the sequence of steps needed for the stepper motors to step (forwards is forward and backward is backwards)
steps = [[1,0,1,0], [0,1,1,0], [0,1,0,1], [1,0,0,1]]

# exec_time is updated dynamically to account for execution time of motors of varying speeds
exec_time = 0.00075

threshold = 0.25
step_size = 0.65 # the numerical increment of 1 step to the position

# Main Function that drives the motors. This is called to set the individual pins of the motor to high and low 
def setStepper(in1, in2, in3, in4, motor_type, factor):
  global exec_time
  current_time = time.time()
  Hardware.pi.write(motor_type[0], in1)
  Hardware.pi.write(motor_type[1], in2)
  Hardware.pi.write(motor_type[2], in3)
  Hardware.pi.write(motor_type[3], in4)
  exec_time = time.time() - current_time
  time.sleep(delay * factor + (factor - 1) * exec_time)

# Motor Class, called by almost every class, used to move the motors, but also used for a lot of calcuation for the speeds of each motor
class Motor:
  # lists that represent the pins of the motor, ordered for implementation in loops
  y_motor = [GPIO_Pins.P1_A1, GPIO_Pins.P1_A2, GPIO_Pins.P1_B1, GPIO_Pins.P1_B2]
  x_motor = [GPIO_Pins.P2_A1, GPIO_Pins.P2_A2, GPIO_Pins.P2_B1, GPIO_Pins.P2_B2]
  z_motor = [GPIO_Pins.P3_A1, GPIO_Pins.P3_A2, GPIO_Pins.P3_B1, GPIO_Pins.P3_B2]

  # dynamic parameters
  moving_slope = 1 # represents the current desired slope of the motors
 
  factorx = 1 # represents the current speed of the x motor, (higher is slower)
  factory = 1 # represents the current speed of the y motor, (higher is slower)

  # quadratic parameters, updated by Math_Mode class
  a = 0
  b = 0
  c = 0

  # circle parameters, updated by Math_Mode class
  r = 0
  deg = 0
    
  quad_offset = 1 # used for debugging
  
# Standard Step Functions (this is when the slope is not changing)
  def backwardStep(motor_type,factor):
    for i in range(4):
      setStepper(steps[i][0], steps[i][1], steps[i][2], steps[i][3], motor_type, factor)
      Motor.incrementPosition(motor_type, -step_size/4)
      

  def forwardStep(motor_type, factor):
    for i in range(3,-1,-1):
      setStepper(steps[i][0], steps[i][1], steps[i][2], steps[i][3], motor_type, factor)
      Motor.incrementPosition(motor_type, step_size/4)  
      
# Dynamic Slope Functions (this is when the slope is changing, using moving_slope and factorx/factory)
  def backwardStepSlopeX():
    for i in range(4):
      if Motor.factorx >= 0:
        return
      setStepper(steps[i][0], steps[i][1], steps[i][2], steps[i][3], Motor.x_motor, abs(Motor.factorx))
      Motor.incrementPosition(Motor.x_motor, -step_size/4)
      

  def forwardStepSlopeX():
    for i in range(3,-1,-1):
      #print("(" + str(Properties.pos_x) + "," + str(Properties.pos_y) + ") slope:" + str(Motor.moving_slope))
      if Motor.factorx <= 0:
        print("returned")
        return
      setStepper(steps[i][0], steps[i][1], steps[i][2], steps[i][3], Motor.x_motor, abs(Motor.factorx))
      Motor.incrementPosition(Motor.x_motor, step_size/4)  
 
  def backwardStepSlopeY():
    for i in range(4):
      if Motor.factory >= 0:
        return
      setStepper(steps[i][0], steps[i][1], steps[i][2], steps[i][3], Motor.y_motor, abs(Motor.factory))
      Motor.incrementPosition(Motor.y_motor, -step_size/4)
      

  def forwardStepSlopeY():
    for i in range(3,-1,-1):
      if Motor.factory <= 0:
        return
      setStepper(steps[i][0], steps[i][1], steps[i][2], steps[i][3], Motor.y_motor, abs(Motor.factory))
      Motor.incrementPosition(Motor.y_motor, step_size/4)    
      

# helper function 
  def incrementPosition(motor_type, increment):
    if motor_type == Motor.x_motor:
      Properties.pos_x += increment
    elif motor_type == Motor.y_motor:
      Properties.pos_y += increment

# moveToPoint Functions (constant slope), but are called for other uses as well
  # moves the x motor to a position
  def moveToPosX(pos, factor):
    while Properties.pos_x < pos - threshold:
      Motor.forwardStep(Motor.x_motor, factor)
    while Properties.pos_x  > pos + threshold:
      Motor.backwardStep(Motor.x_motor, factor)
    return
  # moves the y motor to a position    
  def moveToPosY(pos, factor):
    while Properties.pos_y < pos - threshold:  
      Motor.forwardStep(Motor.y_motor, factor)
      #Properties.pos_y += 1
    while Properties.pos_y > pos + threshold:
      Motor.backwardStep(Motor.y_motor, factor)
      #Properties.pos_y += -1
       
  # the main function that the linear plot uses 
  def moveToPoint(target_x, target_y, factor):
    # calculate factors:
    xfactor = 1
    yfactor = 1
    dx = target_x - Properties.pos_x
    dy = target_y - Properties.pos_y
    
    if dx == 0 or dy == 0:
      if dx == 0:
        dx = 1
      if dy == 0:
        dy = 1
      xfactor = 1
      yfactor = 1
    elif abs(dx) > abs(dy):
      xfactor = 1
      yfactor = abs(dx/dy) 
    elif abs(dx) < abs(dy):
      xfactor = abs(dy/dx) 
      yfactor = 1

    # start threads
    x_thread = threading.Thread(target = Motor.moveToPosX, args = (target_x, xfactor * factor)) # x motor moves simultaneously
    y_thread = threading.Thread(target = Motor.moveToPosY, args = (target_y, yfactor * factor)) # y motor moves simultaneously

    x_thread.start()
    y_thread.start()
         
    x_thread.join()
    y_thread.join()

  # quadratic functions for dynamic slope (different stopping condition), called by threads
  def moveWithSlopeX():
    while abs(Properties.pos_x) <= Properties.max_x/2 and abs(Properties.pos_y) <= Properties.max_y/2:
      if Motor.factorx < 0:
        Motor.backwardStepSlopeX()
      else:
        Motor.forwardStepSlopeX()
  def moveWithSlopeY():
    while abs(Properties.pos_x) <= Properties.max_x/2 and abs(Properties.pos_y) <= Properties.max_y/2:
      if (Motor.moving_slope != 0):
        if Motor.factory < 0:
          Motor.backwardStepSlopeY()
        else:
          Motor.forwardStepSlopeY()

  # updates the moving_slope and updates the factors by looking forward a certain increment and calculating AROC (called by slope thread)
  def updateMovingSlopeQuad():
    while abs(Properties.pos_x) <= Properties.max_x/2 and abs(Properties.pos_y) <= Properties.max_y/2:
      #Motor.moving_slope = 2 * Motor.a * Properties.pos_x + Motor.b
      increment = 0.5
      targety = Motor.a * (Properties.pos_x + increment)* (Properties.pos_x + increment) + Motor.b *  (Properties.pos_x + increment) + Motor.c
      Motor.moving_slope = (targety - Properties.pos_y)/increment
      Motor.calculateFactors()
      time.sleep(2 * delay)
  # calculates the x and y factors needed and updates them based on the moving_slope
  def calculateFactors():
    if Motor.moving_slope != 0:
      if Motor.moving_slope > 1:
        Motor.factory = 1
        Motor.factorx = Motor.moving_slope #* Motor.quad_offset
      elif Motor.moving_slope < -1:
        Motor.factory = -1
        Motor.factorx = abs(Motor.moving_slope) #* Motor.quad_offset
      elif Motor.moving_slope < 0:
        Motor.factorx = 1
        Motor.factory = -1/abs(Motor.moving_slope) #* Motor.quad_offset
      else:
        Motor.factorx = 1 
        Motor.factory = 1/abs(Motor.moving_slope) #* Motor.quad_offset
    Motor.factorx *= 2
    Motor.factory *= 2

  # calculates the moving slope needed by looking forward by a certain increment in degrees and calculating AROC (called by slope thread)
  def updateMovingSlopeCirc():
    while (Motor.deg < 359):
      if (Properties.pos_x == 0):
        if (Properties.pos_y > 0):
          Motor.deg = 90
        else: 
          Motor.deg = 270
      else:
        Motor.deg = math.degrees(math.atan((Properties.pos_y / Properties.pos_x)))
        if (Properties.pos_x < 0):
          Motor.deg += 180
        elif (Properties.pos_x > 0 and Properties.pos_y < 0):
          Motor.deg += 360
        if Motor.deg >= 360:
          Motor.deg -= 360
      
      increment_deg = 5
      target_x = Motor.r * math.cos(math.radians(Motor.deg + increment_deg))
      target_y = Motor.r * math.sin(math.radians(Motor.deg + increment_deg))
      #print("current deg: " + str(Motor.deg))
      #print("(" + str(Properties.pos_x) + "," + str(Properties.pos_y) + ") to (" + str(target_x) + "," + str(target_y) + ")")
      dx = target_x - Properties.pos_x
      dy = target_y - Properties.pos_y
      
      if dx == 0 or dy == 0:
        if (dx == 0):
          Motor.factorx = 0
          Motor.factory = 1
        else:
          Motor.factorx = 0
          Motor.factorx = 1
      elif abs(dy) > abs(dx):
        if dy < 0:
          Motor.factory = -1
        else:
          Motor.factory = 1
        if dx < 0:
          Motor.factorx = -abs(dy/dx)
        else:
          Motor.factorx = abs(dy/dx)
      else:
        if dx < 0:
          Motor.factorx = -1
        else:
          Motor.factorx = 1
        if dy < 0:
          Motor.factory = -abs(dx/dy)
        else:
          Motor.factory = abs(dx/dy)
      
      Motor.factorx *= 2
      Motor.factory *= 2
      
      if (abs(Motor.factorx) > 30):
        Motor.factorx = Motor.factorx/abs(Motor.factorx) * 30
        
      if (abs(Motor.factory) > 30):
        Motor.factory = Motor.factory/abs(Motor.factory) * 30
        
      #print("xfactor: " + str(Motor.factorx) + ", yfactor: " + str(Motor.factory))
      
      time.sleep(2 * delay)
 # circle functions for dynamic slope (different stopping condition), called by threads  
  def moveWithSlopeXCirc():
    while (Motor.deg < 359):
      if Motor.factorx < 0:
        Motor.backwardStepSlopeX()
      else:
        Motor.forwardStepSlopeX()
        
  def moveWithSlopeYCirc():
    while (Motor.deg < 359):
      if Motor.factory < 0:
        Motor.backwardStepSlopeY()
      else:
        Motor.forwardStepSlopeY()    
      
      
