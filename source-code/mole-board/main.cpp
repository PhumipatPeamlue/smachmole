#include "mbed.h"
#include "DebounceIn.h"

#define BLINKING_RATE 500ms

DebounceIn sw1(A2, PullUp);
DebounceIn sw2(D9, PullUp);
DebounceIn sw3(A3, PullUp);
DebounceIn sw4(A5, PullUp);

DigitalOut led1(D6);
DigitalOut led2(D10);
DigitalOut led3(A4);
DigitalOut led4(A6);

I2CSlave slave(D0, D1);

bool hit = false;

// ISR
void sw1Pressed() {
    if (!led1) return;
    led1 = 0;
    hit = true;
}
void sw2Pressed() {
    if (!led2) return;
    led2 = 0;
    hit = true;
}
void sw3Pressed() {
    if (!led3) return;
    led3 = 0;
    hit = true;
}
void sw4Pressed() {
    if (!led4) return;
    led4 = 0;
    hit = true;    
}

void randomMole() {
    int r;
    int old_r;
    while(true) {
        r = (rand() % 4) + 1;

        if (old_r == r) continue;

        old_r = r;

        switch(r) {
            case 1:
                led1 = 1;
                led2 = 0;
                led3 = 0;
                led4 = 0;
                break;
            case 2:
                led1 = 0;
                led2 = 1;
                led3 = 0;
                led4 = 0;
                break;
            case 3:
                led1 = 0;
                led2 = 0;
                led3 = 1;
                led4 = 0;
                break;
            case 4:
                led1 = 0;
                led2 = 0;
                led3 = 0;
                led4 = 1;
                break;
        }
        ThisThread::sleep_for(BLINKING_RATE);
    }
}

void i2c() {
    char buf[20];

    slave.address(0xA0);

    while(true) {
        int i = slave.receive();

        for(int i = 0; i < sizeof(buf); i++) buf[i] = 0;

        switch(i) {
            case I2CSlave::ReadAddressed:
                if (hit) {
                    slave.write("hit ", 4);
                    hit = false;
                } else {
                    slave.write("miss", 4);
                }
                break;
            case I2CSlave::WriteAddressed:
                slave.read(buf, sizeof(buf)-1);
                break;
        }

    }
}

int main()
{
    Thread t1, t2;

    sw1.rise(&sw1Pressed);
    sw2.rise(&sw2Pressed);
    sw3.rise(&sw3Pressed);
    sw4.rise(&sw4Pressed);

    t1.start(randomMole);
    t2.start(i2c);

    ThisThread::sleep_for(osWaitForever);
}
