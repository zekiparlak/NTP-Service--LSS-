# NTP-Service--LSS-
# Gerçek bir ntp server url inden aldığı zaman bilgisini kendine istek atan clientler ile düzenli olarak paylaşan linux sistem servisi olarak çalışan python scripti.

1. Servisimizin çalışması için config dosyasının bulunduğu path ntpServer.py ve ntpServerTest.service dosyası üstündeki scriptimizin path yollarını vermeniz   düzenlemeniz gerekli.

2. Gerekli ayarlamaları yaptıktan sonra service dosyasını /etc/systemd/system/ dizini altına atarak systemctl komutları ile enable ve start ederek servisi     kaldırabilrisiniz.

3. Gelen zaman datasını test eden unittest scripti ntpServerUnitTest.py örnek olarak verilmiştir

4. testClient.py ile servisimize bağlanıp istek atıp zaman bilgisi alabilirsiniz.
