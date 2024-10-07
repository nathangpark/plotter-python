import pigpio
import rgb1602

from GPIO_Pins import GPIO_Pins

# the Hardware class allows all the other classes to use the same instance of the pi and lcd objects, and also has functions that deal with the hardware as a whole
class Hardware:
  pi = pigpio.pi()
  lcd = rgb1602.RGB1602(16,2)

  # sets a HIGH output to the h_enable pin, which is connected to the enable pins of both h-bridges
  def h_enable():
      Hardware.pi.write(GPIO_Pins.h_enable, 1)
  
   # sets a LOW output to the h_enable pin, which is connected to the enable pins of both h-bridges
  def h_disable():
      Hardware.pi.write(GPIO_Pins.h_enable, 0)    

  # does the initial setup for the lcd screen and sets the mode of all the pins to overwrite default state (sometimes redundant)
  def setup():
    Hardware.lcd.setRGB(255,255,255)
    
    Hardware.pi.set_mode(GPIO_Pins.h_enable, pigpio.OUTPUT)
    
    Hardware.pi.set_mode(GPIO_Pins.clk1, pigpio.INPUT)
    Hardware.pi.set_pull_up_down(GPIO_Pins.clk1, pigpio.PUD_UP) 
    
    Hardware.pi.set_mode(GPIO_Pins.dt1, pigpio.INPUT)
    Hardware.pi.set_pull_up_down(GPIO_Pins.dt1, pigpio.PUD_UP) 
    
    Hardware.pi.set_mode(GPIO_Pins.sw_x, pigpio.INPUT)
    Hardware.pi.set_mode(GPIO_Pins.sw_y, pigpio.INPUT)
    # stepper
    Hardware.pi.set_mode(GPIO_Pins.P1_A1, pigpio.OUTPUT)
    Hardware.pi.set_mode(GPIO_Pins.P1_A2, pigpio.OUTPUT)
    Hardware.pi.set_mode(GPIO_Pins.P1_B1, pigpio.OUTPUT)	
    Hardware.pi.set_mode(GPIO_Pins.P1_B2, pigpio.OUTPUT)

    Hardware.pi.set_mode(GPIO_Pins.P2_A1, pigpio.OUTPUT)
    Hardware.pi.set_mode(GPIO_Pins.P2_A2, pigpio.OUTPUT)
    Hardware.pi.set_mode(GPIO_Pins.P2_B1, pigpio.OUTPUT)	  
    Hardware.pi.set_mode(GPIO_Pins.P2_B2, pigpio.OUTPUT)

    Hardware.pi.set_mode(GPIO_Pins.P3_A1, pigpio.OUTPUT)
    Hardware.pi.set_mode(GPIO_Pins.P3_A2, pigpio.OUTPUT)
    Hardware.pi.set_mode(GPIO_Pins.P3_B1, pigpio.OUTPUT)	
    Hardware.pi.set_mode(GPIO_Pins.P3_B2, pigpio.OUTPUT)

