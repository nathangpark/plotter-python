from States import States

# Properties class, referenced by every class, used to keep track of the current properties of the motor
class Properties:
  # coordinate position of gantry
  pos_x = 0
  pos_y = 0
  # whether the pen is down
  pen_down = False
  # the physical limits of the paper
  max_y = 240
  max_x = 180
  # the current state (uses States class)
  current_state = States.menu_state
  delay = 0.00125
  power = 0.0
