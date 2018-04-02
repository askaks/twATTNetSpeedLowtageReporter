class MsgCompiler(object):
    def __init__(self, msg):
        self.msg = msg


    def compile(self, msg):
        #print 'COMPILER MSG self.msg(%s: just msg %s).' % (self.msg, str(msg))
        #print ('Messaging Coming IN: ' + str(msg[0]) + ' down ' +str(msg[1]))
        self.msg = self.msg + str(msg[0]) + 'Download:' + str(msg[1]) + ' Mbit/s '
        #print (self.msg)     
        return self.msg

        #print (msg)
        #print 'AFTER COMPILER MSG self.msg(%s: just msg %s).' % (self.msg, str(msg))
            