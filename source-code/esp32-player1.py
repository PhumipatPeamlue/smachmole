import time
import ssd1306
import framebuf

import threading

import utime
from machine import Pin, I2C

i2c = I2C(scl=Pin(22),sda=Pin(21),freq=100000)

oled = ssd1306.SSD1306_I2C(128,64,i2c)
fbuf = framebuf.FrameBuffer(bytearray(20 * 100 * 2), 128, 64, framebuf.MONO_VLSB)

res_final = 0
res_p1 = 0
res_p2 = 0

print("Scanning I2C bus... found",i2c.scan())

# แสดงผลที่จอ oled ว่า "Press Ready"
fbuf.fill(0)
fbuf.text('Press Ready', 23, 25, 0xffff)
oled.framebuf.blit(fbuf, 0, 0)
oled.show()
time.sleep(2)

# esp32-player1 จะรับข้อความจาก start-board เพื่อรอให้มีการกดปุ่มเริ่มเกมส์
while True:
    start = i2c.readfrom(0x51,5)
    start = start.decode()
    if(start == "START"):
        print(start)
        break

# แสดงผลที่จอ oled ว่า "Game Begin!"
fbuf.fill(0)
fbuf.text('Game Begin!', 23, 25, 0xffff)
oled.framebuf.blit(fbuf, 0, 0)
oled.show()
time.sleep(1.5)

# แสดงผลที่จอ oled ว่า "3"
fbuf.fill(0)
fbuf.line(45,10,85,10,0xffff)
fbuf.line(45,11,85,11,0xffff)
fbuf.line(45,63,85,63,0xffff)
fbuf.line(45,62,85,62,0xffff)
fbuf.line(85,10,85,63,0xffff)
fbuf.line(84,10,84,63,0xffff)
fbuf.line(45,36,85,36,0xffff)
fbuf.line(45,37,85,37,0xffff)
oled.framebuf.blit(fbuf, 0, 0)
oled.show()
time.sleep(1)

# แสดงผลที่จอ oled ว่า "2"
fbuf.fill(0)
fbuf.line(45,10,85,10,0xffff)
fbuf.line(45,11,85,11,0xffff)
fbuf.line(45,63,85,63,0xffff)
fbuf.line(45,62,85,62,0xffff)
fbuf.line(85,10,85,36,0xffff)
fbuf.line(84,10,84,36,0xffff)
fbuf.line(45,36,85,36,0xffff)
fbuf.line(45,37,85,37,0xffff)
fbuf.line(45,36,45,63,0xffff)
fbuf.line(46,36,46,63,0xffff)
oled.framebuf.blit(fbuf, 0, 0)
oled.show()
time.sleep(1)

# แสดงผลที่จอ oled ว่า "1"
fbuf.fill(0)
fbuf.line(53,20,65,10,0xffff)
fbuf.line(53,21,65,11,0xffff)
fbuf.line(53,22,65,12,0xffff)
fbuf.line(65,10,65,63,0xffff)
fbuf.line(64,10,64,63,0xffff)
fbuf.line(55,63,75,63,0xffff)
fbuf.line(55,62,75,62,0xffff)
oled.framebuf.blit(fbuf, 0, 0)
oled.show()
time.sleep(1)

# แสดงผลที่จอ oled ว่า "Start!"
fbuf.fill(0)
fbuf.text('Start!', 42, 27, 0xffff)
oled.framebuf.blit(fbuf, 0, 0)
oled.show()
time.sleep(1.5)

# ------------------------------------------------------------ #

# score
int_score = 0
temp = ''

# function ที่ return ว่าใครเป่ายิ้งฉุบชนะ (0 = draw, 1 = player1, 2 = player2)
def who_win(res1,res2):
    if (res1 == res2):
        return 0
    p = [[1,2],[1,3],[2,1],[2,3],[3,1],[3,2]]
    pp = [2,1,1,2,2,1]
    for i in range(len(p)):
        if (res1 == p[i][0] and res2 == p[i][1]):
            return pp[i]

# function ที่ return ผลลัพธ์เป่ายิ้งฉุบของ player1/player2
def input_from_switch():
    res1 = ''
    res2 = ''
    button_1 = Pin(2,mode=Pin.IN,pull=Pin.PULL_UP)
    button_2 = Pin(0,mode=Pin.IN,pull=Pin.PULL_UP)
    button_3 = Pin(4,mode=Pin.IN,pull=Pin.PULL_UP)
    button_4 = Pin(14,mode=Pin.IN,pull=Pin.PULL_UP)
    button_5 = Pin(12,mode=Pin.IN,pull=Pin.PULL_UP)
    button_6 = Pin(13,mode=Pin.IN,pull=Pin.PULL_UP)
    while True:
        if (button_1.value() == 0): res1 = 1
        if (button_2.value() == 0): res1 = 2
        if (button_3.value() == 0): res1 = 3
        if (button_4.value() == 0): res2 = 1
        if (button_5.value() == 0): res2 = 2
        if (button_6.value() == 0): res2 = 3
        if (res1 != '' and res2 != ''): break
    return [res1,res2]

# เก็บผลลัพธ์ลงใน res_final (global variable)
def main():
    global res_final
    while(1):
        res = input_from_switch()
        res_final = who_win(res[0],res[1])

# create and run main() function in thread
thread = threading.Thread(target=main)
thread.start()

# บันทึกเวลาที่เริ่มเกมส์ตีตุ่น
t_start = utime.ticks_ms()

while (1):
    score = i2c.readfrom(0x50,4)
    score = score.decode()
    
    # ถ้า mole-board ส่ง"hit "มาให้ (ตีตุ่นโดน) +1 คะแนน
    if(score == "hit "):
        print(score)
        int_score += 1
        
    # ถ้า player2 เป่ายิ้งฉุบชนะ -1 คะแนน
    if(res_final == 2):
        int_score -= 1
        res_final = 0
    
    # แสดงผลที่จอ oled ว่า "score : __"
    str_score = 'score : ' + str(int_score)
    fbuf.fill(0)
    fbuf.text(str_score, 28, 27, 0xffff)
    oled.framebuf.blit(fbuf, 0, 0)
    oled.show()
    time.sleep(0.5)
    
    t_now = utime.ticks_ms() # บันทึกเวลาปัจจุจัน
    # ถ้าเวลาถึง 30 วินาที ให้จบเกมส์
    if(utime.ticks_diff(t_now,t_start) > 30000):
        break

# ------------------------------------------------------------ #

# แสดงผลที่จอ oled ว่า "END score : __"
fbuf.fill(0)
fbuf.text('END', 50, 27, 0xffff)
fbuf.text(str_score, 28, 37, 0xffff)
oled.framebuf.blit(fbuf, 0, 0)
oled.show()
time.sleep(0.5)
