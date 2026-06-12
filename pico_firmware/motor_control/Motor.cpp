#include "Motor.h"
#include "hardware/pwm.h"

Motor::Motor(uint in1, uint in2, uint en) {
    input_1 = in1;
    input_2 = in2;
    ENA = en;
}
    
void Motor::setMotorSpeed(int speed) {
    // Clamp speed to -100..100
    if (speed > 100) speed = 100;
    if (speed < -100) speed = -100;
    
    // Positive speed = move forward, Negative speed = move backward
    if (speed > 0) {
        gpio_put(input_1, 1);
        gpio_put(input_2, 0);
    } else if (speed < 0) {
        gpio_put(input_1, 0);
        gpio_put(input_2, 1);
        speed = -speed; // Make speed positive for PWM
    } else {
        gpio_put(input_1, 0);
        gpio_put(input_2, 0);
    }

    pwm_set_gpio_level(ENA, speed * 255 / 100); // Scale speed to PWM range
} 
