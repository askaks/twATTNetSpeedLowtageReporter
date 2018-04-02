import os
import sys
import time
from datetime import datetime
#import daemon
import signal
import threading
import twitter
import json 
import random
from logger import Logger
from compiler import MsgCompiler
from datetime import timedelta
#from logger import MsgCompiler 
#import logger.MsgCompiler as comp
#dataCompiler = MsgCompiler(' A ' + datetime.now().strftime('%Y-%m-%d '))
shutdownFlag = False
TweetResultsNow = False
SpeedSummary = ' '
SpeedCheckFrequency = 0
TweetFrequency = 0
DateStringFormat = '%Y-%m-%d '
TimeStringFormat = '%H:%M:%S'
TweetDailyBatchReportTime = datetime.now() # just to initialize?
#DATACOMPILER = ''
def main(filename, argv):
    print ("======================================")
    print (" Starting Speed Complainer!           ")
    print " Lets get noisy!                      "
    print "======================================"
    #print 'test a(%s: b %s).' % (a, b)
    #global message
    global LiveTweetFlag
    global shutdownFlag
    global SpeedSummary
    global TweetResultsNow
    global SpeedCheckFrequency
    global TweetFrequency
    global TweetDailyBatchReportFlag
    global TweetDailyBatchReportTime
    global DateStringFormat
    global TimeStringFormat
    global LoggingOn
    signal.signal(signal.SIGINT, shutdownHandler)
    config = json.load(open('./config.json'))
    LoggingOn = bool(config['LoggingOn'])
    SpeedSummary = datetime.now().strftime(DateStringFormat + TimeStringFormat)

    SpeedCheckFrequency = int(config['SpeedCheckFrequency'])
    TweetFrequency = int(config['TweetFrequency'])
    LiveTweetFlag = bool(config['LiveTweet'])
    TweetDailyBatchReportFlag = bool(config['TweetDailyBatchReport'])
    configtimestring = config['TweetDailyBatchReportNextTime']
    #configtime = datetime.time.str(configtimestring)
    dateNowStr = datetime.now().strftime(DateStringFormat)
    #dateNowStr = dateNow.strftime(date)
    configtime = datetime.strptime(dateNowStr + configtimestring, DateStringFormat + TimeStringFormat)
    #'%Y-%m-%d %H:%M:%S'
    TweetDailyBatchReportTime = configtime
 

    monitor = Monitor()
    while not shutdownFlag:
        try:

            monitor.run()

            #and not 'no results' in msg
            #if not msg is None and not msg == 'no results':
                #print ('MSG' + msg)
            #if TweetResultsNow == True:
                #print ('Speed Results: ' + speedResult)
            for i in range(0, 5):
                if shutdownFlag:
                    break
                time.sleep(1)

        except Exception as e:
            print 'Error: %s' % e
            sys.exit(1)

    sys.exit()

def shutdownHandler(signo, stack_frame):
    global shutdownFlag
    print 'Got shutdown signal (%s: %s).' % (signo, stack_frame)
    shutdownFlag = True

class ResultsCompiler():
    def __init__(self, msg):
        self.msg = msg


    def append(self, msg):
        #print 'COMPILER MSG self.msg(%s: just msg %s).' % (self.msg, str(msg))
        #print ('Messaging Coming IN: ' + str(msg[0]) + ' down ' +str(msg[1]))
        self.msg = self.msg + str(msg[0]) + 'Download:' + str(msg[1]) + ' Mbit/s '
        #print (self.msg)     
        return self.msg

class Monitor():
    def __init__(self):
        self.lastPingCheck = None
        self.lastSpeedTest = None
        #self.resultsCompiler = ResultsCompiler(datetime.now().strftime('%Y-%m-%d '))
        #self.dataCompiler = MsgCompiler(' A ' + datetime.now().strftime('%Y-%m-%d '))

    def run(self):
        runResult = 'no results'
        global SpeedCheckFrequency
        if not self.lastPingCheck or (datetime.now() - self.lastPingCheck).total_seconds() >= 60:
            self.runPingTest()
            self.lastPingCheck = datetime.now()

        if not self.lastSpeedTest or (datetime.now() - self.lastSpeedTest).total_seconds() >= SpeedCheckFrequency:
            runResult = self.runSpeedTest()
            self.lastSpeedTest = datetime.now()
        return runResult

    def runPingTest(self):
        pingThread = PingTest()
        pingThread.start()

    def runSpeedTest(self):
        speedThread = SpeedTest()
        #global speedResult
        speedThread.start()
        #return speedResult


class PingTest(threading.Thread):
    def __init__(self, numPings=3, pingTimeout=2, maxWaitTime=6):
        super(PingTest, self).__init__()
        self.numPings = numPings
        self.pingTimeout = pingTimeout
        self.maxWaitTime = maxWaitTime
        self.config = json.load(open('./config.json'))

        #self.config = os.path.realpath(os.path.join(os.getcwd(), os.path.dirname('.\config.json')))
        #f = open(os.path.join(__location__, 'bundled-resource.jpg'))
        self.logger = Logger(self.config['log']['type'], { 'filename': self.config['log']['files']['ping'] })


    def run(self):
        pingResults = self.doPingTest()
        self.logPingResults(pingResults)

    def doPingTest(self):
        response = os.system("ping -c %s -W %s -w %s 8.8.8.8 > /dev/null 2>&1" % (self.numPings, (self.pingTimeout * 1000), self.maxWaitTime))
        success = 0
        if response == 0:
            success = 1
        return { 'date': datetime.now(), 'success': success }

    def logPingResults(self, pingResults):
        self.logger.log([ pingResults['date'].strftime('%Y-%m-%d %H:%M:%S'), str(pingResults['success'])])

class SpeedTest(threading.Thread):
    def __init__(self):
        super(SpeedTest, self).__init__()
        self.config = json.load(open('./config.json'))
        self.logger = Logger(self.config['log']['type'], { 'filename': self.config['log']['files']['speed'] })
        self.msgLogger = Logger(self.config['msgLog']['type'], { 'filename': self.config['msgLog']['file']['msg'] })
        #bb = self.TweetCompiler
        #print ('bbbbbb' + bb)
        #self.TweetCompiler =  MsgCompiler('second ' + datetime.now().strftime('%Y-%m-%d '))
        #DATACOMPILER =  self.TweetCompiler 
        #print ('after bbb' + self.TweetCompiler)
    def run(self):
        speedTestResults = self.doSpeedTest()
        self.logSpeedTestResults(speedTestResults)
        #self.compileSpeedTestResults(speedTestResults)
        self.tweetResults(speedTestResults)
        #global speedResult
        #speedResult = speedResult + speedTestResults[2]
        return speedTestResults

    def doSpeedTest(self):
        global TweetFrequency
        # run a speed test
        result = os.popen("/usr/local/bin/speedtest-cli --simple").read()
        #print(result) Prints All Ping/Download/Upload Speeds
        if 'Cannot' in result:
            return { 'date': datetime.now(), 'uploadResult': 0, 'downloadResult': 0, 'ping': 0 }

        # Result:
        # Ping: 529.084 ms
        # Download: 0.52 Mbit/s
        # Upload: 1.79 Mbit/s

        resultSet = result.split('\n')
        pingResult = resultSet[0]
        downloadResult = resultSet[1]
        uploadResult = resultSet[2]

        pingResult = float(pingResult.replace('Ping: ', '').replace(' ms', ''))
        downloadResult = float(downloadResult.replace('Download: ', '').replace(' Mbit/s', ''))
        uploadResult = float(uploadResult.replace('Upload: ', '').replace(' Mbit/s', ''))
        print(resultSet[1]) #Download Result full sentence
        return { 'date': datetime.now(), 'uploadResult': uploadResult, 'downloadResult': downloadResult, 'ping': pingResult }
    
    
    def TweetDailyBatchReport(self):
        global TweetDailyBatchReportFlag
        global TweetDailyBatchReportTime
        global SpeedSummary
        if TweetDailyBatchReportFlag:
            hour = TweetDailyBatchReportTime.hour
            day = TweetDailyBatchReportTime.day
            if datetime.now().day == day:
                if datetime.now().hour >= hour:
                    #Tweet(self, SpeedSummary)
                    self.logTwitterMessage('Tweeting Live Report ', SpeedSummary )
                    TweetDailyBatchReportTime = TweetDailyBatchReportTime + timedelta(days=-1)

    def TweetIndividualStatus(self, speedTestResults):
        global TweetFrequency
        if TweetFrequency <= 0:
            self.Tweet(speedTestResults)   
            self.resetTweetFrequency()       
        else: #TweetFrequency set to NOT Tweet
            self.logTwitterMessage('Logging \'Dead\' Tweet (Frequency Only: ' + str(TweetFrequency) +  '): ',  speedTestResults)
        #print ('Tweet Looks Like: Daily Lowtage Summary: ' + speedTestResults)
  
   
    def Tweet(self, message):
        global LiveTweetFlag
        if LiveTweetFlag:
            api = twitter.Api(consumer_key=self.config['twitter']['twitterConsumerKey'],
            consumer_secret=self.config['twitter']['twitterConsumerSecret'],
            access_token_key=self.config['twitter']['twitterToken'],
            access_token_secret=self.config['twitter']['twitterTokenSecret'])
            if api:
                api.PostUpdate(message)
                self.logTwitterMessage('Logging Live Tweet: ', message)
            else:
                self.logTwitterMessage('API ERROR', '')  
        else: # else NOT LiveTweetFlag
            self.logTwitterMessage('Logging Dead Tweet (LiveTweetFlag set to false): ', message)

    def logSpeedTestResults(self, speedTestResults):
        self.logger.log([ speedTestResults['date'].strftime('%Y-%m-%d %H:%M:%S'), str(speedTestResults['uploadResult']), str(speedTestResults['downloadResult']), str(speedTestResults['ping']) ])
    
    
    def logTwitterMessage(self, title, message):
        global LoggingOn
        if LoggingOn:
            self.msgLogger.log([datetime.now().strftime('%Y-%m-%d %H:%M:%S') + title + ' ' + message])

    def resetTweetFrequency(self):
        global TweetFrequency
        newconfig = json.load(open('./config.json'))
        TweetFrequency = newconfig['TweetFrequency']
    #def compileSpeedTestResults(self, speedTestResults):
        #print('IN SPEED TEST ' + str(speedTestResults['downloadResult']))
        #print('AAAAAAAA' + str(self.TweetCompiler.msg))
        #mm = self.TweetCompiler.msg
       # self.TweetCompiler.compile([ speedTestResults['date'].strftime(' %H:%M '), str(speedTestResults['downloadResult']) + DATACOMPILER ])
        #DATACOMPILER = self.TweetCompiler.msg
        #print (self.TweetCompiler.msg)
        #aa = self.TweetCompiler
        #dataCompiler = dataCompiler.compile([ speedTestResults['date'].strftime(' %H:%M '), str(speedTestResults['downloadResult']) ])
        #dataCompiler.compile([ speedTestResults['date'].strftime(' %H:%M '), str(speedTestResults['downloadResult']) ])
    def tweetResults(self, speedTestResults):
        thresholdMessages = self.config['tweetThresholds']
        global SpeedSummary
        global TweetResultsNow
        global TweetFrequency
        message = None
        for (threshold, messages) in thresholdMessages.items():
            threshold = float(threshold)

            if speedTestResults['downloadResult'] < threshold:
                message = messages[random.randint(0, len(messages) - 1)].replace('{tweetTo}', self.config['tweetTo']).replace('{contractCost}', self.config['contractCost']).replace('{contractSpeed}', self.config['contractSpeed']).replace('{downloadResult}', str(speedTestResults['downloadResult']))
                SpeedSummary = SpeedSummary +  ' ' + str(speedTestResults['downloadResult']) + 'Mbps @' + datetime.now().strftime('%H:%M')
                TweetFrequency = TweetFrequency - 1
                self.TweetDailyBatchReport()      
        if message:
            self.TweetIndividualStatus(message)
        
            #speedResult = datetime.now().strftime('%Y-%m-%d')

class DaemonApp():
    def __init__(self, pidFilePath, stdout_path='/dev/null', stderr_path='/dev/null'):
        self.stdin_path = '/dev/null'
        self.stdout_path = stdout_path
        self.stderr_path = stderr_path
        self.pidfile_path = pidFilePath
        self.pidfile_timeout = 1

    def run(self):
        main(__file__, sys.argv[1:])

if __name__ == '__main__':
    main(__file__, sys.argv[1:])

    workingDirectory = os.path.basename(os.path.realpath(__file__))
    stdout_path = '/dev/null'
    stderr_path = '/dev/null'
    fileName, fileExt = os.path.split(os.path.realpath(__file__))
    pidFilePath = os.path.join(workingDirectory, os.path.basename(fileName) + '.pid')
    from daemon import runner
    dRunner = runner.DaemonRunner(DaemonApp(pidFilePath, stdout_path, stderr_path))
    dRunner.daemon_context.working_directory = workingDirectory
    dRunner.daemon_context.umask = 0o002
    dRunner.daemon_context.signal_map = { signal.SIGTERM: 'terminate', signal.SIGUP: 'terminate' }
    dRunner.do_action()



