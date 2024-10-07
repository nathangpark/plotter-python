from Hardware import Hardware
from Properties import Properties
from Motor import Motor
from GPIO_Pins import GPIO_Pins
from States import States
from G_Functions import G_Functions

import os

# menu states
root_menu = "root menu"
file_selection_menu = "file selection menu"
current_menu = root_menu

# root menu hover options
file_hover = "Select a File"
start_hover = "Start"
main_menu_hover = "Main Menu"
current_root_hover = file_hover

# file selection
filenames = []
hover_index = 0
hover_filename = ""
startname = "---"
filename = startname
cur_dir = "/home/team7"

# start screen
start_screen = "Calibrate Ready?"

# updates screen when called
def print_lcd():
  Hardware.lcd.clear()
  Hardware.lcd.setCursor(0,0)
  if current_menu == root_menu:
    Hardware.lcd.printout(current_root_hover)
    Hardware.lcd.setCursor(0,1)
    Hardware.lcd.printout("<" + filename.replace(".gcode","") + ">")
  elif current_menu == file_selection_menu:
    Hardware.lcd.printout(hover_filename.replace(".gcode","") )
  Hardware.lcd.setCursor(11,1)
  if Properties.power > 10:
      Hardware.lcd.printout("{:.1f}".format(Properties.power) + "W ")
  else:
      Hardware.lcd.printout(" {:.1f}".format(Properties.power) + "W") 

# cycles forward through files when browsing
def file_cycle_next():
  global hover_filename, hover_index
  if hover_index == len(filenames) - 1:
    hover_index = 0
  else:
    hover_index += 1
  hover_filename = filenames[hover_index]  
  print_lcd()
  return

# cycles back through files when browsing
def file_cycle_prev():
  global hover_filename, hover_index
  if hover_index == 0:
    hover_index = len(filenames) - 1
  else:
    hover_index -= 1
  hover_filename = filenames[hover_index]  
  print_lcd()
  return

# selects the file that is current being hovered over
def file_select():
  global filename, current_menu
  filename = hover_filename
  current_menu = root_menu
  print_lcd()
  return

# when in the root menu of the g-code mode, cycles forward through options (file select, start, main menu)
def root_cycle_next():
  global current_root_hover
  if current_root_hover == file_hover:
    current_root_hover = start_hover
  elif current_root_hover == start_hover:
    current_root_hover = main_menu_hover
  elif current_root_hover == main_menu_hover:
    current_root_hover = file_hover
  print_lcd()  
  return

# when in the root menu of the g-code mode, cycles back through options (file select, main menu, start)
def root_cycle_prev():
  global current_root_hover
  if current_root_hover == file_hover:
    current_root_hover = main_menu_hover
  elif current_root_hover == start_hover:
    current_root_hover = file_hover
  elif current_root_hover == main_menu_hover:
    current_root_hover = start_hover
  print_lcd()
  return

# selects the option in the root that is being hovered over
def root_select():
  global current_menu, current_root_hover, filenames, hover_filename
  if current_root_hover == file_hover:
    filenames = create_list()
    if len(filenames) == 0:
      Hardware.lcd.setCursor(0,1)
      Hardware.lcd.printout("No files found")
      return
    hover_filename = filenames[0]
    current_menu = file_selection_menu
  elif current_root_hover == start_hover:
    if (filename != startname):
      current_root_hover = start_screen
  elif current_root_hover == start_screen:  
    if (filename != startname):
      start_execution()
    return
  elif current_root_hover == main_menu_hover:
    Properties.current_state = States.menu_state
    Hardware.lcd.clear()
    Hardware.lcd.printout("G-Code")
  print_lcd()
  return

# looks in current directory for files that end with g code, returns list of filenames
def create_list():
  filenames = []
  search_for = ".gcode"
  file_list = os.listdir(cur_dir)
  for filename in file_list:
    if search_for in filename:
      filenames.append(filename)
  return filenames

# auto calibrate to home position
def calibrate():
  Hardware.h_enable()
  Hardware.lcd.clear()
  Hardware.lcd.printout("Calibrating...")
  # move until both limit switches are pressed
  while Hardware.pi.read(GPIO_Pins.sw_y) == 0:
    Motor.forwardStep(Motor.y_motor, 1)
  while Hardware.pi.read(GPIO_Pins.sw_x) == 0:
    Motor.backwardStep(Motor.x_motor, 1)

  Properties.pos_x = 0
  Properties.pos_y = 0

  # move to the current corner of page
  Motor.moveToPosX(Properties.max_x,1)
  Motor.moveToPosY(-Properties.max_y,1)

  Properties.pos_x = 0
  Properties.pos_y = 0
  
  Hardware.h_disable()
  print_lcd()

  return  

# starts execution of each line within the file, runs execute_command() for each command in file
def start_execution():
  file1 = open(filename, 'r')
  lines = file1.readlines()

  for line in lines:
    if len(line) != 0:
      string_arguments = line.split()
      arguments = get_values(string_arguments)
      execute_command(arguments)
  Hardware.h_disable()

  file1.close()

  return

# extract the values from a command line within a file (string to floats), returns list in order of [command,x,y,f,i,j]
def get_values(arguments):
  command = ""
  x = 0.0
  y = 0.0
  f = 400.0
  i = 0.0
  j = 0.0
  end = False

  for argument in arguments:
    if not end:
      if len(argument) != 0:
        if argument[0] == '(':
          return [command,x,y,f,i,j]
        elif "(" in argument:
          argument = argument[0:argument.find("(")]
      if argument[len(argument) - 1] == ";":
        end = True
        if len(argument) == 1:
          return [command,x,y,f,i,j]
        argument = argument.replace(";","")

      if argument[0] == "G" or argument[0] == "M":
        command = argument
      elif argument[0] == "X":
        x = float(argument[1:])
      elif argument[0] == "Y":
        y = float(argument[1:])
      elif argument[0] == "F":
        f = float(argument[1:])
        if f > 400:
          f = 400
      elif argument[0] == "I":
        i = float(argument[1:])  
      elif argument[0] == "J":
        j = float(argument[1:])       
  return [command,x,y,f,i,j]

# executes a command given the command and numerical arguments
def execute_command(arguments): # [command, x, y, f, i, j]
  global current_menu, current_root_hover
  command = arguments[0]
  x = arguments[1]
  y = arguments[2]
  f = arguments[3]
  i = arguments[4]
  j = arguments[5]

  Hardware.lcd.clear()
  Hardware.lcd.setCursor(0,0)
  Hardware.lcd.printout(command)
  Hardware.lcd.setCursor(11,1)
  if Properties.power > 10:
      Hardware.lcd.printout("{:.1f}".format(Properties.power) + "W ")
  else:
      Hardware.lcd.printout(" {:.1f}".format(Properties.power) + "W") 
  
  
  Hardware.h_enable()

  if (command == "G00"):
    G_Functions.G00(x,y)   
  elif (command == "G01"):
    G_Functions.G01(x,y,f)
  elif (command == "G02"):  
    G_Functions.G02(x,y,i,j) 
  elif (command == "G03"):  
    G_Functions.G03(x,y,i,j)
  elif (command == "G28"):
    G_Functions.G28()
  elif (command == "M02"):
    G_Functions.M02()
  elif (command == "M03"):
    G_Functions.M03()
  elif (command == "M04"):
    G_Functions.M04()    

  current_menu = root_menu
  current_root_hover = file_hover
  print_lcd()
  
  return  

# functions that are called by menu mode (initialize) and driver (rotary controls)
class G_Code:
  def initialize():
    # set coordinates to g code format
    Properties.pos_x = abs(Properties.pos_x - Properties.max_x/2)
    Properties.pos_y = abs(Properties.pos_y + Properties.max_y/2)
    print_lcd()
    os.chdir(cur_dir)

  def x_rotary_up():
    if current_menu == root_menu:
      root_cycle_prev()
    elif current_menu == file_selection_menu:
      file_cycle_prev()
    return
  
  def x_rotary_down():
    if current_menu == root_menu:
      root_cycle_next()
    elif current_menu == file_selection_menu:
      file_cycle_next()
    return
  
  def x_press():
    if current_menu == root_menu:
      root_select()
    elif current_menu == file_selection_menu:
      file_select()
    return
  
  def y_press():
    global current_menu
    if current_menu == root_menu:
      if current_root_hover == start_screen:
        calibrate()
      else:  
        Properties.current_state = States.menu_state
        Hardware.lcd.clear()
        Hardware.lcd.printout("G-Code")
    elif current_menu == file_selection_menu:
      current_menu = root_menu
      print_lcd()
    return
