class OutputRow:
    def __init__(self, msg_body):
        self.user_id = msg_body["user_id"]
        self.device_type = msg_body["device_type"]
        
        # TODO mask these 2 fields
        self.device_id = msg_body["device_id"]
        self.ip = msg_body["ip"]

        self.locale = msg_body["locale"]
        self.app_version = version_to_int(msg_body["app_version"])
    
    def __str__(self):
        return f"user_id={self.user_id}, device_type={self.device_type}, device_id={self.device_id}, ip={self.ip}, locale={self.locale}, app_version={self.app_version})"
    
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

