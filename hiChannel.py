# Sends a message to several channels in slack and changes Icon and/or Status Message.
# This version doesn't use slack's library. Only webapi calls
# https://github.com/nachogarmilla/hiChannel
# March 2021

# Coding Resources
    # https://www.w3schools.com/python/ref_requests_post.asp
    # https://keestalkstech.com/2019/10/simple-python-code-to-send-message-to-slack-channel-without-packages/
    # https://api.slack.com/methods/auth.test
    # https://api.slack.com/web#posting_json
    # https://api.slack.com/docs/presence-and-status
    # https://levelup.gitconnected.com/the-easy-guide-to-python-command-line-arguments-96b4607baea1

# Pending Improvements:
    # Function Arguments documentation
    # Translate code comments (spanish to english)
    # Add more comments?

# Non native Python library: https://pypi.org/project/requests/
import requests

import os
import argparse
import random
import sys
import csv
import time

UrlMesSlack = "https://slack.com/api/chat.postMessage"
UrlAuthSlack = "https://slack.com/api/auth.test"
UrlStatusSlack = "https://slack.com/api/users.profile.set"
SlackCtype = "application/json; charset=utf-8"
AuthType = "Bearer"
DefaultChannelsFile = "channels.txt"
DefaultTimeTableFile = "timetable.txt"

# Execution params reading
parser = argparse.ArgumentParser(description = 'Send Hi and Bye messages to several Slack channels')
parser.add_argument("-first", action = "store_true", help = "Use first messaje of the message files")
parser.add_argument("-ChannelsFile", type = str, default = DefaultChannelsFile, help = "Set the channels file to use. Default: " + DefaultChannelsFile)
parser.add_argument("-verbose", action = "store_true", help = "Verbose mode")
parser.add_argument("-test", action = "store_true", help = "Test mode. Doesn't send any message")
parser.add_argument("-Token", type = str, default = str(os.environ.get("slack_hichannel_Token")), help = "Slack authentication Token. Default: 'slack_hichannel_Token' (environment variable)")
parser.add_argument("-statusMes", type = str, default = None, help = "Message for the status. Overrides '" + DefaultTimeTableFile + "' status message.")
parser.add_argument("-StatusIcon", type = str, help = "Icon for the status-. Overrides '" + DefaultTimeTableFile + "' status icon.")
parser.add_argument("-confirm", action = "store_true", help = "Ask for confirmations to send messages and change status.")
group = parser.add_mutually_exclusive_group(required = True)
group.add_argument("-auth", action = "store_true", help = "Test authentication. Don't sends message.")
group.add_argument("-file", type = str, help = "Use this particular file for messages source.")
group.add_argument("-timetable", action = "store_true", help = "Use '" + DefaultTimeTableFile + "' to decide the messages file to use according to the system hour.")

cliArgs = parser.parse_args()

# Params to vars for an easyest code reading
ChannelsFileToUse = cliArgs.ChannelsFile
MessagesFileToUse = cliArgs.file
VerboseMode = cliArgs.verbose
UseFirstLine = cliArgs.first
TestMode = cliArgs.test
TokenSlack = cliArgs.Token
AutCheck = cliArgs.auth
UseTimetableFile = cliArgs.timetable
StatusMessage = cliArgs.statusMes
StatusIcon = cliArgs.StatusIcon
AskForConfirm = cliArgs.confirm

def smart_Message_File_Selector(StsMes, StsIco):
    '''Determines the message file, status message and status icon depending of system timetable and timetables file'''

    global VerboseMode

    TimeDec = (time.localtime().tm_hour + time.localtime().tm_min / 60)
    if VerboseMode:
        print(f"System time in decimal format: {TimeDec}")

    TimeFramesHours = []
    TimeFramesMessages = []
    TimeFramesStatusMessages = []
    TimeFramesStatusIcons = []
    Line_Count = 0
    Prev_Hour = 0

    try:
        with open(DefaultTimeTableFile, "r", encoding = 'utf-8') as TimetableFile:
            Csv_reader = csv.reader(TimetableFile, delimiter=',', )
            for row in Csv_reader:
                if Line_Count == 0:
                    if VerboseMode:
                        print(f'Column names are {", ".join(row)}')
                    Line_Count= Line_Count + 1
                else:
                    # Checking timetable file hours definition integrity
                    if Prev_Hour >= float(row[0]):
                        print("Timetable file is wrong. Hours to be defined from earlierr to later, i.e. 9 before 18.")
                        sys.exit()

                    # Hours, messages files, status and icons list formation
                    TimeFramesHours.append(float(row[0]))            
                    Prev_Hour = float(row[0])
                    TimeFramesMessages.append(row[1])
                    TimeFramesStatusMessages.append(row[2])
                    TimeFramesStatusIcons.append(row[3])
    except:
        sys.exit("Error opening timetables file.")
    

    # Para la lógica de asignación conviene que se recorra de hora mayor hacia hora menor
    TimeFramesHours.reverse()
    TimeFramesMessages.reverse()
    TimeFramesStatusMessages.reverse()
    TimeFramesStatusIcons.reverse()

    # Busqueda de de ventana horaria en la que estamos para asignar fichero de mensajes, status e icono
    Count = 0
    for i in TimeFramesHours:
        Count = Count + 1 
        if TimeDec >= i:
            # Message File
            MessagesFileSelected = TimeFramesMessages[Count - 1]
            # Status Msg & Icon
            if StsMes == None:
                StsMes = TimeFramesStatusMessages[Count - 1]
            if StsIco == None:
                StsIco = TimeFramesStatusIcons[Count - 1]
            if VerboseMode:
                print(f"Messages File: {MessagesFileSelected}")
                print(f"Status Message: {StsMes}")
                print(f"Status Icon: {StsIco}")
            break
    return MessagesFileSelected, StsMes, StsIco

def auth_Formation(Token, AuthType):
    """ Authorization string creation for Calling Slack.

        Takes the enrionment var, or the token provided as execution
        parameter and elaborates the authorithation string to use in
        the calls to slack web api.
        Parameters
        ----------
        Token: str
            token to use
        AuthType: str
            literal to precede the token. Used to specify kind of token authentication.
        Returns
        -------
        str"""
    
    global VerboseMode

    if Token == None:
        print("")
        input("Press Enter to exit.")
        print("")
        sys.exit("No hay variable de entorno 'slack_hichannel_Token' ni se ha proporcionado como parámetro.")
    else:
        AuthString = AuthType + " " + Token
        if VerboseMode:
            print(f"Auth: {AuthString}")
    return AuthString

def authentication_Check(Url, HeadersForRequest):
    '''Calls Slack to check the authentication'''
    Response = requests.post(Url, headers = HeadersForRequest)
    print(f"Authentication Test Response: {Response.text}")

def channels_Load(ChannelsFile):
    '''Opens the channels file where will be posted the message'''

    global VerboseMode

    try:
        with open(ChannelsFile, "r") as ChannelsFileContent:
            ChannelsLoaded = ChannelsFileContent.readlines()

        ChannelsLoaded = [i.strip() for i in ChannelsLoaded] # Retira los \n de la lista de canales

        print(f" Number of Channels: {len(ChannelsLoaded)}")

        if VerboseMode:
            print(f"{len(ChannelsLoaded)} channels loaded.")
            print(f"Channels loaded: {ChannelsLoaded}")

        return ChannelsLoaded

    except:
       sys.exit("Error opening channel files. Exiting.")

def message_To_Send_Selection(MessagesFile, UseFirstMessage):
    '''Picks message to send from the message file'''

    global VerboseMode

    try:
        # Abre fichero de mensajes
        with open(MessagesFile, "r", encoding = "utf8") as MessagesFileContent:
            Messages = MessagesFileContent.readlines()
        Messages = [i.strip() for i in Messages] # Retira los \n de la lista de mensajes
        if VerboseMode:
            print(f"{len(Messages)} messages loaded.")
            print(f"Messages loaded: {Messages}")
    except:
       sys.exit("Error opening messages files. Exiting.")

    # Elije mensaje a enviar
    if UseFirstMessage:
        ChoosenMessage = Messages[0]
    else:
        ChoosenMessage = Messages[random.randint(0,(len(Messages)-1))]
        print(f" Message: {ChoosenMessage} <<<<<<<<<<<")
    
    return ChoosenMessage

def check_Ok_Response(ReceivedResponseJson, ReceivedResponseText):
    '''Checks if Slack Response is ok'''
    if ReceivedResponseJson["ok"] != True:
        print("")
        print("=============== SLACK CALL ERROR ===============")
        print(ReceivedResponseText)
        print("================================================")
        print("")
        input("Press Enter to exit.")
        print("")
        sys.exit("Slack call doesn't response True")

def send_Message_To_Slack(Url, HeadersForRequest, MessageToSend, ChannelsToSend):
    '''Sends Message to Slack and checks that Response is OK'''

    global VerboseMode

    for i in ChannelsToSend:
        Response = requests.post(Url, headers = HeadersForRequest, json = {"channel": i,"text": MessageToSend})
        print(end=".", flush=True)
        check_Ok_Response(Response.json(), Response.text)
        
        if VerboseMode:
            print("\n")
            print("Slack's response after sending a message:")
            print(Response.text)
    
    print("\n")

def change_Slack_Status(Url, HeadersForRequest, Message, Icon):
    '''Sends new status message and status icon to Slack, and checks if response is OK'''

    global VerboseMode

    Response = requests.post(Url, headers = HeadersForRequest, json = {
            "profile": {
                "status_text": str(Message),
                "status_emoji": str(Icon),
                "status_expiration": 0
                }
        })

    check_Ok_Response(Response.json(), Response.text)

    if VerboseMode:
        print("Status change response:")
        print(Response.text)

if __name__ == "__main__":
    print()

    if UseTimetableFile:
        MessagesFileToUse, StatusMessage, StatusIcon = smart_Message_File_Selector(StatusMessage, StatusIcon)

    Auth = auth_Formation(TokenSlack, AuthType)
    slackRequestHeaders = {'Content-type' : SlackCtype, 'Authorization' : Auth}

    if AutCheck:
        authentication_Check(UrlAuthSlack, slackRequestHeaders)
    else:
        Channels = channels_Load(ChannelsFileToUse)
        channelMessage = message_To_Send_Selection(MessagesFileToUse, UseFirstLine)
        print(f" Status Message: {StatusMessage}")
        print(f" Status Icon: {StatusIcon}")
        if not TestMode:
            if AskForConfirm:
                print()
                userConfirm = input(" Press y + Enter to confirm changes... ").lower()
                if userConfirm != "y":
                    print()
                    sys.exit("Aborted by user.")
            send_Message_To_Slack(UrlMesSlack, slackRequestHeaders, channelMessage, Channels)
            change_Slack_Status(UrlStatusSlack, slackRequestHeaders, StatusMessage, StatusIcon)            
        else:
            print("Test Mode. Message/s not send.")