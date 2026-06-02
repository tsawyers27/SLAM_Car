from machine import Pin, PWM
from time import sleep

# Motor Pins
in3 = Pin(19, Pin.OUT) #IN3 connected to GPIO 19
in4 = Pin(20, Pin.OUT) #IN4 connected to GPIO 20
enb = PWM(Pin(18))     #ENB connected to GPIO 18
enb.freq(1000)

#Motor functions
def motor_forward(speed):
    in3.high()
    in4.low()
    enb.duty_u16(speed)
    
def motor_backward(speed):
    in3.low()
    in4.high()
    enb.duty_u16(speed)
    
def motor_stop():
    in3.low()
    in4.low()
    enb.duty_u16(0)
    
# Main loop to test motor
try:
    while True:
        print("Moving forward")
        motor_forward(32768)
        sleep(2)
        
        print("Stopping")
        motor_stop()
        sleep(2)
        
        print("Moving backward")
        motor_backward(32768)
        sleep(2)

except KeyboardInterrupt:
    motor_stop()
    print("Program stopped")