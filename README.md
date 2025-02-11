# raspi_lcdClock
ラズパイで動くLCDに時間/温度/湿度表示＋Ambientとkintoneに温湿度情報の送信
## ハード構成
・Rassbery PI Zero2W

・DHT-11(4pinに接続)

・1602 LCDディスプレイ(I2Cアドレス = 0x27)

![image](https://github.com/user-attachments/assets/114eb52d-6706-48ad-9b95-f541a36531f1)

## ソフトウェア構成
### Ambient
d1 : 温度

d2 : 湿度

![image](https://github.com/user-attachments/assets/d893bf70-7d20-4081-aec2-80a659e546f0)

### kintone
ID : ロケーションID（本コードでは、"001"で固定）。別のロケーションにも設置する場合は、このコードで管理

温度：温度

湿度：湿度

![image](https://github.com/user-attachments/assets/509cc6a9-b640-42e1-b67e-9889e6544936)

## 使い方
必要な箇所に値を設定すると、LCDにはリアルタイムで年月日、曜日、時間、温度、湿度が表示されます。

また、1時間に1回、その際の温度と湿度をAmbientとkintoneに送ります。
