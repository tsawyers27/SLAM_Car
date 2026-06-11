#include <stdio.h>
#include "pico/stdlib.h"
#include "hardware/pwm.h"
#include "hardware/pio.h"
#include <iostream>
#include <string>

// Define motor 1 control pins
const uint IN1 = 2;
const uint IN2 = 3;
const uint ENA1 = 4;

// Define motor 2 control pins
const uint IN3 = 5;
const uint IN4 = 6;
const uint ENA2 = 7;

// Define encoder pins
// const uint ENC1_SDA = 9;
// const uint ENC1_SCL = 7;
// const uint ENC2_SDA = 14;
// const uint ENC2_SCL = 12;

// Define baseline speed value (percentage out of 100)
int speed {50};

void setMotorSpeed(int speed) {
    // Clamp speed to -100..100
    if (speed > 100) speed = 100;
    if (speed < -100) speed = -100;
    
    // Positive speed = move forward, Negative speed = move backward
    if (speed > 0) {
        gpio_put(IN1, 1);
        gpio_put(IN2, 0);
        gpio_put(IN3, 1);
        gpio_put(IN4, 0);
    } else if (speed < 0) {
        gpio_put(IN1, 0);
        gpio_put(IN2, 1);
        gpio_put(IN3, 0);
        gpio_put(IN4, 1);
        speed = -speed; // Make speed positive for PWM
    } else {
        gpio_put(IN1, 0);
        gpio_put(IN2, 0);
        gpio_put(IN3, 0);
        gpio_put(IN4, 0);
    }

    pwm_set_gpio_level(ENA1, speed * 255 / 100); // Scale speed to PWM range
    pwm_set_gpio_level(ENA2, speed * 255 / 100); // Scale speed to PWM range
} 

void sendEncoderData() {
    // Send encoder data via I2C

}

void readKeyboardInput() {
    //
}

int main()
{
    stdio_init_all();
    
    // Initialize pins
    gpio_init(IN1);
    gpio_init(IN2);
    gpio_init(ENA1);
    gpio_init(IN3);
    gpio_init(IN4);
    gpio_init(ENA2);

    // Set pin directions
    gpio_set_dir(IN1, GPIO_OUT);
    gpio_set_dir(IN2, GPIO_OUT);
    gpio_set_dir(ENA1, GPIO_OUT);
    gpio_set_dir(IN3, GPIO_OUT);
    gpio_set_dir(IN4, GPIO_OUT);
    gpio_set_dir(ENA2, GPIO_OUT);

    // Tell GPIO 0 and 1 they are allocated to the PWM
    gpio_set_function(ENA1, GPIO_FUNC_PWM);
    gpio_set_function(ENA2, GPIO_FUNC_PWM);

    // Set PWM duty cycle based on speed
    uint slice_num1 = pwm_gpio_to_slice_num(ENA1);
    uint slice_num2 = pwm_gpio_to_slice_num(ENA2);

    // Set PWM range to 0..255
    pwm_set_wrap(slice_num1, 255);
    pwm_set_wrap(slice_num2, 255);

    // Start PWM
    pwm_set_enabled(slice_num1, true);
    pwm_set_enabled(slice_num2, true);

    while (true) {
        setMotorSpeed(70);
        sleep_ms(2000);

        setMotorSpeed(0);
        sleep_ms(2000);

        setMotorSpeed(-70);
        sleep_ms(2000);

        setMotorSpeed(0);
        sleep_ms(2000);
    }
}
