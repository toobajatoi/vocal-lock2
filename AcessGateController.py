class AccessGateController:
    def __init__(self, enroller, authenticator):
        self.enroller = enroller
        self.authenticator = authenticator

    def grant_or_deny(self, user_id, passphrase, audio_path):
        ok, msg = self.authenticator.authenticate(user_id, passphrase, audio_path)
        if ok:
            print("✅ Access Granted")
            return True
        else:
            print("❌ Access Denied:", msg)
            return False
