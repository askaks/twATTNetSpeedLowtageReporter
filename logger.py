
class Logger(object):
    def __init__(self, type, config):
        if type == 'csv':
            self.logger = CsvLogger(config['filename'])
        if type == 'txt':
            self.logger = CsvLogger(config['filename'])
        #if type == 'msg':
         #   self.logger = MsgCompiler('Empty')

    def log(self, logItems):
        self.logger.log(logItems)

   # def compile(self, logItems):
     #   self.logger.compile(logItems)

class CsvLogger(object):
    def __init__(self, filename):
        self.filename = filename

    def log(self, logItems):
        with open(self.filename, "a") as logfile:
            logfile.write("%s\n" % ','.join(logItems))



