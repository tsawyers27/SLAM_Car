#ifndef MOTOR_H
#define MOTOR_H

#include "pico/stdlib.h"

class Motor {
    private:
        uint input_1;
        uint input_2;
        uint ENA;
    
    public:
        Motor(uint in1, uint in2, uint en);
        void setMotorSpeed(int speed);
};

#endif