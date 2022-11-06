from socket import AF_INET, SOCK_DGRAM
import socket
import sys
import struct
import time
import threading
import json

# <username> i kendi kullanıcı adınız ile değiştirin
CONFIG_PATH = '/home/<username>/NTP_SERVER_TEST/config.json'

class Client(threading.Thread):             # İsteği atan client nesnesi (threading.Thread nesnesinden miras)

    # Herhangi bir Client dan istek geldiğinde bir Client nesnesi yaratılır ve zaman bilgisi verilir.
    def __init__(self, ip, port, connection, timeData, intervalSec = 1):
        threading.Thread.__init__(self)
        self.connection = connection        # isteğe cevap veren connection
        self.adress = (ip, port)            # istek atan client ip, port bilgisi
        self.timeData = timeData            # gönderilecek zaman bilgisi
        self.intervalSec = intervalSec      # paket gönderme zaman aralığı

    # Client nesnesi bu zaman bilgisini istek atan clienta düzenli zaman aralıkları ile yayınlar       
    def run(self):                          # thread execute
        while True:
            self.connection.sendto(str(self.timeData).encode('utf-8'), self.adress)    
            time.sleep(self.intervalSec)

class ListenServer(threading.Thread):       # Gelen istekleri dinleyen nesne (threading.Thread nesnesinden miras)

    # Gelen istekleri dinler yayın yapan Client nesnelerinin zamanlarını günceller
    def __init__(self, connection, timeData, intervalSec = 1):
        threading.Thread.__init__(self)
        self.connection = connection       # istekleri bekleyen conneciton !! not:Client nesnesindeki connection ile aynı instance
        self.timeData = timeData           # zaman bilgisi 
        self.intervalSec = intervalSec     # Client nesnelerine verilmek üzere alınan zaman aralığı bilgisi 
        self.clients = []                  # istek atan clientların listesi 

    def UpdateTime(self, lastTimeData):    # bağlı olan clientlara atılan zaman bilgisini güncelleten metod 
        self.timeData = lastTimeData
        for client in self.clients:
            client.timeData = lastTimeData

    def run(self):                         # thread execute
        buf = 1024                         # buffer size  
        while(True):
            recvMsg, (ip, port) = self.connection.recvfrom(buf)     # gelen istek mesajı ve adresi
            if recvMsg:                                             # istek var ise    
                c = Client(ip, port, self.connection, self.timeData, self.intervalSec)      # Client nesnesi yaratılır
                c.start()                                                                   # Client nesnesi üzerinden istek atan clientlara zaman bilgisi verilir ve yayına başlanır
                self.clients.append(c)                                                      # client listesine eklenir            
                
class Server:                              # Çok rollü NTP service nesnesi

    # düzenli aralıklarla gerçek bir ntp serverdan alınan zaman bilgisini istek atan clientlar ile paylaşan ve onlara yayın yapan service nesnesi
    def __init__(self, ip, port, ntpHost = "1.tr.pool.ntp.org", ntpPort = 123, intervalSec = 1):
        self.server = None        # Dinleme yapan ve isteklere cevap atan server socket
        self.client = None        # gerçek ntp servera istek atan client
        self.srvListen = None     # dinleme server nesnesi  

        self.address = (ip, port)             # dinleme yapan ve cevap atan server adress bilgisi
        self.ntpAdress = (ntpHost, ntpPort)   # gerçek ntp server adress bilgisi  
        self.intervalSec = intervalSec        # zaman bilgisi alma ve paylaşma zaman aralığı  

        self.lastTimeData = 2208988800        # '1970-01-01 00:00:00' ilk değerini alan son zaman bilgisi tutan değişken
        self.open_socket()                      

    # Dinleme yapan ve istek atan server ve zaman bilgisi alan client socketlerinin açılması
    def open_socket(self):
        try:
            self.server = socket.socket(AF_INET, SOCK_DGRAM)
            self.server.bind(self.address)
            self.client = socket.socket(AF_INET, SOCK_DGRAM)
        except socket.error:
            print('Cannot Open Socket...\nChange Listen Port From Config File.')
            if self.server:
                self.server.close()
            sys.exit(1)
    
    # Gerçek bir NTP serverdan zaman bilgisi alan metot
    def get_NTP_time(self):
        buf = 1024                          # Buffer size
        reqTimeMsg = '\x23' + 47 * '\0'     # ilk 8 Byte spesifik leap indicator olan 48 bytelık NTP UDP mesaj paketi
        TIME1970 = 2208988800               # 1970-01-01 00:00:00
        
        self.client.sendto(reqTimeMsg.encode('utf-8'), self.ntpAdress)   # istek gönderilir
        recvMsg, address = self.client.recvfrom(buf)                     # cevap    

        if recvMsg:                 # cevap var ise                                     
            t = struct.unpack("!12I", recvMsg)[10]          # dönen binary data unpack edilip zaman verisi çekilir
            t -= TIME1970                                   # dönen zaman datasından ilk zaman değeri çıkarılıp şuanki zaman elde
            return t                                        # şimdiki zaman geri döndürülür
        else:
            return TIME1970         # Unit Test !!! 'için  bu değer dönerse metot yanlış çalışmıştır

    def run(self):                          # Server nesnesi ana metodu
        self.lastTimeData = self.get_NTP_time()             # son zaman datası alınır 

        #print(time.ctime(self.lastTimeData).replace("  ", " "))        

        srvListen = ListenServer(self.server, self.lastTimeData, self.intervalSec)  # dinleme server i yaratılır
        srvListen.start()                                                           # dinleme server i başlatılır

        while(True):                                # düzenli olarak zaman bilgisi alınıp güncellenir
            time.sleep(self.intervalSec)
            self.lastTimeData = self.get_NTP_time()
            srvListen.UpdateTime(self.lastTimeData)
            print(time.ctime(self.lastTimeData).replace("  ", " "))        

def ReadOptionsFromJSON():              # config dosyası okuyan metot
    with open(CONFIG_PATH) as f:
       data = json.load(f)
    return (data["ntpHostURL"], data["ntpServerListenPort"], data["timeIntervalSec"])   # ntphost, dinleme portu ve zaman aralığı bilgisi döndürülür

if __name__ == "__main__":
    # servisimiz gerekli değerleri config dosyasından okuduktan sonra çok rollü Server nesnemizi yaratılıp başlatılır
    (ntpHost, listenPort, interValSec) = ReadOptionsFromJSON()
    ntpPort = 123
    srv = Server("127.0.0.1", listenPort, ntpHost, ntpPort, interValSec)
    srv.run()

