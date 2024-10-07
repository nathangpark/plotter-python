from Properties import Properties
from Hardware import Hardware
from Motor import Motor

import time


# shortest delay possible without breaking the motor
delay = 0.00125
exec_time = 0.00075

# this is the sequence of steps needed for the stepper motors to step (forwards is forward and backward is backwards)
steps = [[1,0,1,0], [0,1,1,0], [0,1,0,1], [1,0,0,1]]
steps_down = 18

# the numerical increment of 1 step to the position
step_size = 0.65

# global factors

# Main Function that drives the motors. This is called to set the individual pins of the motor to high and low 
def set_stepper(in1, in2, in3, in4, motor_type, factor):
  global exec_time
  current_time = time.time()
  Hardware.pi.write(motor_type[0], in1)
  Hardware.pi.write(motor_type[1], in2)
  Hardware.pi.write(motor_type[2], in3)
  Hardware.pi.write(motor_type[3], in4)
  exec_time = time.time() - current_time
  time.sleep(delay * abs(factor) + (abs(factor) - 1) * exec_time)
  return

# increments the position on the designated axis
def increment_position(motor_type, increment):
  if motor_type == Motor.x_motor:
    Properties.pos_x -= increment
  elif motor_type == Motor.y_motor:
    Properties.pos_y += increment

# class holds functions that are called by G_Functions.py that move the motors one step (backward and forward functions) and toggle the pen
class G_Motor:
  factors = [1,1]

  def backward_step(motor_type):
    if motor_type == Motor.x_motor:
      index = 0
    else:
      index = 1
    for i in range(4):
      set_stepper(steps[i][0], steps[i][1], steps[i][2], steps[i][3], motor_type, G_Motor.factors[index])
      increment_position(motor_type, -step_size/4)
    return


  def forward_step(motor_type):
    if motor_type == Motor.x_motor:
      index = 0
    else:
      index = 1
    for i in range(3,-1,-1):
      set_stepper(steps[i][0], steps[i][1], steps[i][2], steps[i][3], motor_type, G_Motor.factors[index])
      increment_position(motor_type, step_size/4)  
    return  
  
  def toggle_pen():
    time.sleep(0.3)
    for i in range(steps_down): # run steps_down times
      if (Properties.pen_down): # if the pen is already down, move up (forward) at 1/5 speed
        Motor.forwardStep(Motor.z_motor, 5)
      else:   # if the pen is up, move down (backward) at 1/5 speed
        Motor.backwardStep(Motor.z_motor,5)
        time.sleep(0.01)
    Properties.pen_down = not Properties.pen_down # update boolean variable   
    time.sleep(0.3) 
