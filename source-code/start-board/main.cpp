#include "mbed.h"
#include "DebounceIn.h"

DebounceIn sw(D3, PullUp);
I2CSlave slave(D0, D1);

bool start = false;

// ISR
void swPressed() {
    
    start = true;
}

// write text ("START"/"WAIT ") to esp32-player1 and esp32-player2
void task() {
    char buf[20];
    slave.address(0xA2);

    while (true) {
        int i = slave.receive();

        for(int i = 0; i < sizeof(buf); i++) buf[i] = 0; // Clear buffer

        switch (i) {
            case I2CSlave::ReadAddressed:
                if (start) {
                    start = false;
                    slave.write("START", 5);
                } else {
                    slave.write("WAIT ", 5);
                }
                break;
            case I2CSlave::WriteAddressed:
                slave.read(buf, sizeof(buf)-1);
                break;
        }
    }
}

// main() runs in its own thread in the OS
int main() {
    sw.rise(callback(swPressed));
    task();
}
