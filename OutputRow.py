
from ff3 import FF3Cipher

class OutputRow:
    def __init__(self, msg_body):
        if ("user_id" in msg_body and 
           "device_type" in msg_body and 
           "device_id" in msg_body and 
           "ip" in msg_body and 
           "locale" in msg_body and 
           "app_version" in msg_body):

            self.validRow = True
            self.user_id = msg_body["user_id"]
            self.device_type = msg_body["device_type"]
            self.locale = msg_body["locale"]
            
            # mask these 2 fields using ff3 encryption
            self.device_id = encryptMask(msg_body["device_id"])
            self.ip = encryptMask(msg_body["ip"])
            
            #need to convert the app_version to an integer - strip out the . and pad with 0's
            self.app_version = version_to_int(msg_body["app_version"])
        else:
            self.validRow = False

    def __str__(self):
        return f"user_id={self.user_id}, device_type={self.device_type}, device_id={self.device_id}, ip={self.ip}, locale={self.locale}, app_version={self.app_version})"


# this method of masking encrypts the value.  can be decrypted with the key later
# this is using FF3 which does "format presering encryption" to keep the length of the value the same
def encryptMask(value):
    """Returns a masked version of a string using format preserving encryption
    """
    # NOTE:ideally, this key should be stored in a secure location not in the code
    key = "b83302516f1278a1e95200e542189656"
    tweak = "5ff40e6d0ce864"

    c = FF3Cipher.withCustomAlphabet(key, tweak, "0123456789-.") # use this alphabet to allow for . and - in the value
    ciphertext = c.encrypt(value)
    print(f"ciphertext: {ciphertext}")
    return ciphertext


def pad_to_two_digits(val):
    return f"{val:02d}"

def version_to_int(version):
    l = [int(x) for x in version.split('.')]
    major = pad_to_two_digits(l[0] if len(l) > 0 else 0)
    minor = pad_to_two_digits(l[1] if len(l) > 1 else 0)
    tiny = pad_to_two_digits(l[2] if len(l) > 2 else 0)
    build = pad_to_two_digits(l[3] if len(l) > 3 else 0)
    version = int(major + minor + tiny + build)
    return version

#print(version_to_int("2.12.0")) would be 20120000 (leading zero is lost when converting to integer)                        
#print(version_to_int("2.2.13.2")) would be 20213002                        
#print(version_to_int("2.12.3.2")) would be 20120302                         
#print(version_to_int("22.12.0.2")) would be 22120002

