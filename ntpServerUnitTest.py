import unittest

from ntpServer import Server

class Test_NTP_Time(unittest.TestCase):
    def test_Get_NTP_Time(self):
        TIME1970 = 2208988800
        result = Server('127.0.0.1', 5555).get_NTP_time()
        self.assertNotEqual(result, TIME1970)

if __name__ == '__main__':
    unittest.main()

