from twisted.internet import reactor, protocol
import json, ecdsa, os
version = "IPFSC 0.1"
endl = "\r\n" # This does not change the expected endl for recieving, only sending
config = json.load(open("/etc/ipfsc/server.conf", "r")) # todo command line option to specify config file, but with sane default
db = BTEdb("/etc/ipfsc/database.json")
def mb(bool, power=0):
    return bool*(2^power)
class ipfsc(twisted.protocols.basic.LineReceiver):
    self.state = 0
    def lineRecieved(self, line):
        if self.state == 0:
            self.remote_username = line
            self.state = 1
            return
        if self.state == 1:
            self.remote_request_type = line.split()[0]
            if self.remote_request_type == "REGISTER":
                if config["allow_user_registration"] == False:
                    self.loseConnection()
                    return
                if config["allow_user_registration_without_approval"] == False: 
                    pass # todo add request to moderation queue
                else:
                    pass # todo Add user
            elif self.remote_request_type == "AUTHENTICATE":
                results = db.Select(username = self.remote_username)
                if len(results) == 0:
                    self.loseConnection()
                    return
                self.vk = ecdsa.VerifyingKey.from_pem(results[0]["verifying_key"])
                self.auth_challenge = base64.b64encode(os.urandom(128))
                self.transport.write("CHALLENGE" + " " + self.auth_challenge)
                state = 3
                return
            else:
                self.loseConnection()
                return
        if self.state == 3:
            if vk.verify(line, self.auth_challenge):
                pass # Authentication success
            else:
                self.loseConnection()
    def connectionMade(self):
        self.transport.write(version)
        self.transport.write(endl)
        # Following line subject to change
        self.transport.write(str(mb(config["allow_public_read"])+mb(config["allow_user_registration"]["requests"], 1), + mb(config["allow_user_registration_without_approval"], 2)))
        self.transport.write(endl)


factory = protocol.ServerFactory()
factory.protocol = ipfsc
reactor.listenTCP(config["port"], factory)
reactor.run()
