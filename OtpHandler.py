#PyOtp

import single
import pyotp
from LogManager import log

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

        try:
            retVal = self.TimeOtp.now()
        except Exception as e:
            retVal = ''
            log.info('otp except.')
        return retVal

