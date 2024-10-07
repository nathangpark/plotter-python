from Properties import Properties
from Motor import Motor
from G_Motor import G_Motor

import math
import threading
import time

threshold = 0.5

actual_max_speed = 2000 # upper limit 4000, set to 400 to be accurate to project description 

slow_speed = 4000/actual_max_speed

# calculates and returns the factors of each motor needed given two points
def calculate_factors(start_x, start_y, final_x, final_y):
  factors = [1,1]
  if (final_x - start_x == 0 ) or (final_y - start_y == 0):
    return factors
  
  slope = (final_y - start_y) / (final_x - start_x)
  if abs(slope) > 1:
    factors[0] = abs(slope)
    factors[1] = 1
  else:
    factors[0] = 1
    factors[1] = 1/abs(slope) 

  if abs(factors[0]) > 10:
    factors[0] = 10
  if abs(factors[1]) > 10:
    factors[1] = 10

  factors[0] *= (final_x - start_x) / abs(final_x - start_x)
  factors[1] *= (final_y - start_y) / abs(final_y - start_y)

  return factors

# simple continuous function (meant to be called in thread) that moves the x motor such that the position is the argument
def move_to_x(x):
  while abs(Properties.pos_x - x) > threshold:
    #print("x: " + str(Properties.pos_x))
    if Properties.pos_x < x:
      G_Motor.backward_step(Motor.x_motor)
    else:
      G_Motor.forward_step(Motor.x_motor) 
  return

# simple continuous function (meant to be called in thread) that moves the y motor such that the position is the argument
def move_to_y(y):
  while abs(Properties.pos_y - y) > threshold:
    #print("y: " + str(Properties.pos_y))
    if Properties.pos_y < y:
      G_Motor.forward_step(Motor.y_motor)
    else:
      G_Motor.backward_step(Motor.y_motor) 
  return

# function that is called in thread to move the x motor such that the coordinates approach the desired coordinate point from the target degree
def move_to_deg_x(target_degrees):
  deg_threshold = 1
  while abs(G_Functions.current_degrees - target_degrees) > deg_threshold:
    if G_Motor.factors[0]  < 0:
      G_Motor.forward_step(Motor.x_motor)
    else:
      G_Motor.backward_step(Motor.x_motor) 
  return

# function that is called in thread to move the y motor such that the coordinates approach the desired coordinate point from the target degree
def move_to_deg_y(target_degrees):
  deg_threshold = 1
  while abs(G_Functions.current_degrees- target_degrees) > deg_threshold:
    if G_Motor.factors[1] < 0:
      G_Motor.backward_step(Motor.y_motor)
    else:
      G_Motor.forward_step(Motor.y_motor) 
  return

# a function that is meant to be called within a thread that continuously updates values needed for the speed/direction of both motors 
def update_circle_values(target_degrees, center_point, radius, deg_increment):
  deg_threshold = 1
  while abs(G_Functions.current_degrees - target_degrees) > deg_threshold:
    # calculate current degrees
    G_Functions.current_degrees = calculate_degrees(center_point, [Properties.pos_x, Properties.pos_y])
    # find next point
    
    next_point = find_next_point_circle(G_Functions.current_degrees + deg_increment, center_point, radius)

    factors = calculate_factors(Properties.pos_x, Properties.pos_y, next_point[0], next_point[1])
    
    if radius > 20:
      speed = 1
    else: 
      speed = 20 / radius
    
    factors = [factor * speed * slow_speed for factor in factors]

    #print("factors: " + str(factors))
    G_Motor.factors = factors
    
    time.sleep(Properties.delay)

  return

# simple function that calculates the coordinate points of a point on the circle given the center, radius, and degrees
def find_next_point_circle(next_degrees, center_point, radius):
  x = radius * math.cos(math.radians(next_degrees)) + center_point[0]
  y = radius * math.sin(math.radians(next_degrees)) + center_point[1]
  return [x,y]

# checks whether the curent position and desired position is the same distance away from the designated center
def verify_radius(x,y,i,j):
  r_threshold = 2

  target_point = [x,y]
  current_point = [Properties.pos_x, Properties.pos_y]
  center_point = [Properties.pos_x + i, Properties.pos_y + j]
  
  current_radius = math.sqrt((center_point[0] - current_point[0]) ** 2 + (center_point[1] - current_point[1]) ** 2 )
  target_radius = math.sqrt((center_point[0] - target_point[0]) ** 2 + (center_point[1] - target_point[1]) ** 2 )
  
  print("current radius: " + str(current_radius) + ". target radius: " + str(target_radius))
  return (abs(current_radius - target_radius) < r_threshold)

# simple function that calculates the degrees of a certian point given that point and the center
def calculate_degrees(center_point, target_point):
  if (target_point[0] - center_point[0] == 0):
    if target_point[1] > center_point[1]:
      degrees = 90
    else:
      degrees = 270
    return degrees
    
  degrees = math.degrees(math.atan((target_point[1] - center_point[1])/ (target_point[0] - center_point[0])))
  
  
  if (target_point[0] > center_point[0]):
    degrees = degrees
  elif (target_point[0] < center_point[0] and target_point[1] >= center_point[1]):
    degrees += 180
  elif (target_point[0] < center_point[0] and target_point[1] < center_point[1]):
    degrees -= 180
    
    
  if degrees > 360:
    degrees -= 360
  if degrees< 0:
    degrees += 360  
    
  return degrees

# class holds the main functions that are called in G_Code.py, such as the commands and the draw arc function
class G_Functions:
  current_degrees = 0

  def G00(x,y):
    # line straight to point
    G_Functions.G01(x,y,400)
    return

  def G01(x,y,f):
    factors = calculate_factors(Properties.pos_x, Properties.pos_y, x,y)

    # adjust speed
    factors = [factor * (400 / f)*slow_speed for factor in factors]

    G_Motor.factors = factors

    # start threads
    x_thread = threading.Thread(target = move_to_x, args = (x,)) # x motor moves simultaneously
    y_thread = threading.Thread(target = move_to_y, args = (y,)) # y motor moves simultaneously

    x_thread.start()
    y_thread.start()

    x_thread.join()
    y_thread.join()

    G_Motor.factors = [1,1]

    return 

  # draws arc cw
  def G02(x,y,i,j):
    G_Functions.draw_arc(x,y,i,j,5)
    return
  # draws arc ccw
  def G03(x,y,i,j):
    G_Functions.draw_arc(x,y,i,j,-5)
    return
  # moves to home position
  def G28():
    move_to_x(0)
    move_to_y(0)
    return
  # stops program, pen up move to home
  def M02():
    G_Functions.M04()
    G_Functions.G28()
    return
  # pen down if not down
  def M03():
    if not Properties.pen_down:
      G_Motor.toggle_pen()
    return
  # pen up if down
  def M04():
    if Properties.pen_down:
      G_Motor.toggle_pen()
    return 
  
  def draw_arc(x,y,i,j,deg_increment):
    if not verify_radius(x,y,i,j):
      # cannot be done
      print("points do not have equal radius")
      return
    
    radius = math.sqrt(i ** 2 + j ** 2)
    
    target_point = [x,y]
    center_point = [Properties.pos_x + i, Properties.pos_y + j]
    
    G_Functions.current_degrees = calculate_degrees(center_point, [Properties.pos_x, Properties.pos_y])
    target_degrees = calculate_degrees(center_point, target_point)
    print("target degrees: " + str(target_degrees))
    
    # update circle values initially
    # find next point
    
    next_point = find_next_point_circle(G_Functions.current_degrees + deg_increment, center_point, radius)

    factors = calculate_factors(Properties.pos_x, Properties.pos_y, next_point[0], next_point[1])
    
    if radius > 20:
      speed = 1
    else: 
      speed = 20 / radius
    
    factors = [factor * speed * slow_speed for factor in factors]

    #print("factors: " + str(factors))
    G_Motor.factors = factors

    x_thread = threading.Thread(target = move_to_deg_x, args = (target_degrees,)) # x motor moves simultaneously
    y_thread = threading.Thread(target = move_to_deg_y, args = (target_degrees,)) # y motor moves simultaneously
    val_thread = threading.Thread(target = update_circle_values, args = (target_degrees, center_point, radius, deg_increment)) # values update simultaneously

    x_thread.start()
    y_thread.start()
    val_thread.start()

    x_thread.join()
    y_thread.join()
    val_thread.join()

    G_Motor.factors = [1,1]
    G_Functions.current_degrees = 361

    return
