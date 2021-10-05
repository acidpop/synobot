#PyOtp

import single
import pyotp


class OtpHandler(single.SingletonInstane):
    TimeOtp = None
    SecretKey = ''

    def __init__(self, *args, **kwargs):
        self.TimeOtp = pyotp.TOTP(self.SecretKey)

    def InitOtp(self, secretKey):
        self.SecretKey = secretKey
        self.TimeOtp = pyotp.TOTP(self.SecretKey)

    def GetOtp(self):
        if self.SecretKey == '':
            return ''

        return self.TimeOtp.now()


