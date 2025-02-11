# -*- coding: utf-8 -*-
#!/usr/bin/python
import RPi.GPIO as GPIO
import smbus
import time
import datetime
import dht11 # 温湿度センサーモジュール
import ambient
import requests

# I2C通信の設定
I2C_ADDR  = 0x27 # I2Cアドレス
LCD_WIDTH = 16   # 表示文字数の上限
LCD_CHR = 1 # 文字列送信モードの識別子
LCD_CMD = 0 # コマンド送信モードの識別子
LCD_LINE_1 = 0x80 # 一行目に表示する文字列の書き込み先
LCD_LINE_2 = 0xC0 # 二行目に表示する文字列の書き込み先
LCD_BACKLIGHT  = 0x08  # バックライトをOFFにするコマンド

bus = smbus.SMBus(1) # 接続されているバスの番号を指定

#DHT11の設定
TEMP_SENSOR_PIN = 4 # 温湿度センサーのピンの番号
INTERVAL = 10 # 監視間隔（秒）
RETRY_TIME = 2 # dht11から値が取得できなかった時のリトライまので秒数
MAX_RETRY = 20 # dht11から温湿度が取得できなかった時の最大リトライ回数


# kintone API設定
API_TOKEN = "Your kintone api token"
SUBDOMAIN = "subdomain"
APP_ID = "x"
URL = f"https://{SUBDOMAIN}.cybozu.com/k/v1/record.json"
HEADERS = {
    "X-Cybozu-API-Token": API_TOKEN,
    "Content-Type": "application/json"
}


def init_display():
  send_byte_to_data_pin(0x33,LCD_CMD)
  send_byte_to_data_pin(0x32,LCD_CMD)
  send_byte_to_data_pin(0x06,LCD_CMD)
  send_byte_to_data_pin(0x0C,LCD_CMD)
  send_byte_to_data_pin(0x28,LCD_CMD)
  send_byte_to_data_pin(0x01,LCD_CMD)
  time.sleep(0.0005)

def send_byte_to_data_pin(bits, mode):
  upper_bits = mode | (bits & 0xF0) | LCD_BACKLIGHT
  lower_bits = mode | ((bits<<4) & 0xF0) | LCD_BACKLIGHT
  bus.write_byte(I2C_ADDR, upper_bits)
  enable_toggle_button(upper_bits)
  bus.write_byte(I2C_ADDR, lower_bits)
  enable_toggle_button(lower_bits)

def enable_toggle_button(bits):
  time.sleep(0.0005)
  bus.write_byte(I2C_ADDR, (bits | 0b00000100))
  time.sleep(0.0005)
  bus.write_byte(I2C_ADDR,(bits & ~0b00000100))
  time.sleep(0.0005)

def send_string_to_display(message,line):
  message = message.ljust(LCD_WIDTH," ")
  send_byte_to_data_pin(line, LCD_CMD)
  for i in range(LCD_WIDTH):
    send_byte_to_data_pin(ord(message[i]),LCD_CHR)



class EnvSensorClass: # 温湿度センサークラス
    def GetTemp(self): # 温湿度を取得
        instance = dht11.DHT11(pin=TEMP_SENSOR_PIN)
        retry_count = 0
        while True: # MAX_RETRY回まで繰り返す
            retry_count += 1
            result = instance.read()
            if result.is_valid(): # 取得できたら温度と湿度を返す
                return result.temperature, result.humidity
            elif retry_count >= MAX_RETRY:
                return 99.9, 99.9 # MAX_RETRYを過ぎても取得できなかった時に温湿度99.9を返す
            time.sleep(RETRY_TIME)



# メイン処理
def main():
    GPIO.setwarnings(False) # GPIO.cleanup()をしなかった時のメッセージを非表示にする
    GPIO.setmode(GPIO.BCM) # ピンをGPIOの番号で指定

    # LCDのメモリ初期化
    init_display()
    
    cnt=9999
    
    # [Ctrl+C]で強制終了するまで無限ループ@
    while True:
        #温度と湿度を取得
        env = EnvSensorClass()
        temp, hum = env.GetTemp() # 温湿度を取得

        # 現在時刻の取得
        # local_time = datetime.datetime.now()
        # LCDに表示する文字列のメモリへの書き込み
        # send_string_to_display(time.strftime("%Y.%m.%d (%a)", time.gmtime()) , LCD_LINE_1) # 一行目
        #send_string_to_display(local_time.strftime("%H:%M", LCD_LINE_2) + " / " + temp & "c" & hum & "%") # 二行目
        # send_string_to_display(local_time.strftime("%H:%M ") + str(temp) + "C/"+str(hum)+"%", LCD_LINE_2)
        
        start_time = time.perf_counter()
        while True:

          # 現在時刻の取得
          local_time = datetime.datetime.now()
          # LCDに表示する文字列のメモリへの書き込み
          send_string_to_display(time.strftime("%Y.%m.%d (%a)", time.gmtime()) , LCD_LINE_1) # 一行目
          #send_string_to_display(local_time.strftime("%H:%M", LCD_LINE_2) + " / " + temp & "c" & hum & "%") # 二行目
          send_string_to_display(local_time.strftime("%H:%M ") + str(temp) + "C/"+str(hum)+"%", LCD_LINE_2)


          end_time = time.perf_counter()
          elapsed_time = end_time - start_time

          if elapsed_time > 3600:
            break
          #endif
        #endwhile

        while True:
          try:
            am = ambient.Ambient("xxxx","xxxxxxxx")
            res = am.send({'d1':str(temp),'d2':str(hum)})
            print(str(datetime.datetime.now())+' updated.')
            break
          except:
            print(str(datetime.datetime.now())+' excepted.')
            time.sleep(3)
            continue
        #endwhile
        
        while True:
          try:
            data = {
                'app': APP_ID,
                'record': {
                    'ID' : {'value': '001'},
                    '温度': {'value': str(temp)},
                    '湿度': {'value': str(hum)}
                }
            }
            response = requests.post(URL, json=data, headers=HEADERS)
            print(response.json());
            print('kintone '+str(datetime.datetime.now())+' updated.')
            break;
          except:
            print('kintone '+str(datetime.datetime.now())+' excepted.')
            time.sleep(3)
            continue
        #endwhile

try:        
  print('Start:' + str(datetime.datetime.now()))
  main()
except KeyboardInterrupt:
  pass
finally:
  LCD_BACKLIGHT = 0x00  # バックライトをOFFにするコマンド
  send_byte_to_data_pin(0x01, LCD_CMD) # LCDの表示内容をクリア
