import pigpio
import time

from Hardware import Hardware
from Properties import Properties


PWM_PIN = 19
CPRT_PIN = 11

# creates a new wave at a certain duty cycle at the PWM pin
def set_PWM(pi, pin, frequency, duty_cycle):
    pi.set_mode(pin, pigpio.OUTPUT)
    period = 1.0 / frequency
    
    on_time_us = int(period * duty_cycle /100 * 1e6)
    off_time_us = int(period * (100 - duty_cycle)/100 * 1e6)
    # Create a square wave
    square_wave = [
        pigpio.pulse(1 << pin, 0, on_time_us),
        pigpio.pulse(0, 1 << pin, off_time_us)
    ]
    pi.wave_clear()  # Clear existing waveforms
    pi.wave_add_generic(square_wave)  # Add square wave
    waveform = pi.wave_create()  # Create waveform
    pi.wave_send_repeat(waveform)  # Send waveform repeatedly
    time.sleep(0)
    
# stops the current wave, meant for when program terminates    
def stop_PWM(pi):
    pi.wave_tx_stop()  # Stop sending waveform
    pi.set_PWM_dutycycle(PWM_PIN, 0)  # Set duty cycle to 0
    pi.stop()  # Cleanup pigpio resources
    

# class holds the main function run() that is executed within a thread in Driver.py
class ADC:
    def run():
        try:
            pi = Hardware.pi
            pi.set_mode(CPRT_PIN, pigpio.INPUT)
            pi.set_pull_up_down(CPRT_PIN, pigpio.PUD_UP)
            freq = 1000
            duty_cycle = 0
            detected_duty_cycle = None
            index = 0
            voltage_list = [0,0,0,0,0]
            expected_voltage = 0
            
            while True:
                
                CPRT_STATE = pi.read(CPRT_PIN)
                
                if CPRT_STATE == 1:
                    
                    detected_duty_cycle = duty_cycle
                    
                    if duty_cycle > 6:
                        duty_cycle -= 6
                    else:
                        duty_cycle = 0
                    
                    if detected_duty_cycle <= 2:
                        expected_voltage == 0
                    else:
                        expected_voltage = 0.056 * detected_duty_cycle

                    
                    voltage_list[index] = expected_voltage
                    
                    if (index == 4):
                        index = 0
                        Properties.power = max(voltage_list) * 12
                        print(str(max(voltage_list)) + "A ")
                        Hardware.lcd.setCursor(11,1)
                        if Properties.power > 10:
                            Hardware.lcd.printout("{:.1f}".format(Properties.power) + "W ")
                        else:
                            Hardware.lcd.printout(" {:.1f}".format(Properties.power) + "W")
                        time.sleep(0.1)
                    else:
                        index += 1
                    
     
                        
                set_PWM(pi, PWM_PIN, freq,duty_cycle)
                duty_cycle += 1
                if duty_cycle > 100:
                    pi.wave_clear()
                    duty_cycle = 0
        
                time.sleep(0.05)
                  
        except KeyboardInterrupt:
            stop_PWM(pi)  # Clean up when done or if an exception occurs
