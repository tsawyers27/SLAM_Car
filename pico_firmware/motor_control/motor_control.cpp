#include "Motor.h"
#include "hardware/pwm.h"
#include <stdio.h>
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
int direction1 {0}; // 1 = forward, -1 = backward, 0 = stopped
int direction2 {0}; // 1 = forward, -1 = backward, 0 = stopped

void sendEncoderData() {
    // Send encoder data via I2C

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

    // Tell GPIO pins they are allocated to the PWM
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

    // Instantiate motors
    Motor MOTOR1(IN1, IN2, ENA1);
    Motor MOTOR2(IN3, IN4, ENA2);

    while (true) {
        // Check for user input over serial
        int input = getchar_timeout_us(0);

        // If input equals anything other than a timeout error, control motors
        if (input != PICO_ERROR_TIMEOUT) {
            // Forward
            if (input == 'w') {
                direction1 = direction2 = 1;
                printf("Forward at %d\n", speed);
            }
            else if (input == 's') {
                direction1 = direction2 = -1;
                printf("Backward at %d\n", speed);
            }
            else if (input == 'd') {
                direction1 = 1;
                direction2 = -1;
                printf("Turning right");
            }
            else if (input == 'a') {
                direction1 = -1;
                direction2 = 1;
                printf("Turning left");
            }
            else if (input == 'x') {
                direction1 = direction2 = 0;
                std::cout << "Stopped motors\n";
            }
            else if (input == '+') {
                speed = speed + 10;
                if (speed > 100) speed = 100;
                std::cout << "Increased speed by 10%\n";
            }
            else if (input == '-') {
                speed = speed - 10;
                if (speed < 0) speed = 0;
                std::cout << "Decreased speed by 10%\n";
            }

            MOTOR1.setMotorSpeed(direction1 * speed);
            MOTOR2.setMotorSpeed(direction2 * speed);
        }
        
        sleep_ms(10);

    }
}
