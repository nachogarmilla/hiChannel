# hiChannel
Python tool for sending messages to several Slack groups and change Icon and/or status message.

I use it to say hi! or Bye in several work channels, instead of search and write on each one.

It doesn't send scheduled messages but sends messages (indicated or selected depending of the system time) triggered by the user.

## Setup

### Environment & Dependences

Developed, tested and used on Win 10, Python 3.9.0 and Request 2.25.1

**hiChannel.py** requires `Requests` library to call Slack web api. You'll find `Requests` in: https://pypi.org/project/requests/

Slack's token can be provided as parameter (see below) and as environment variable, named `slack_hichannel_token` (recomended)

### Files

There are some important files to setup and place in the **hiChannel.py** folder.

* `channels.txt` : Contens Slack Channel IDs where the message will be posted. Channels file can be indicated as parameter too. See Execution Parameters section below. Bonus: [How find slack channel ID](https://stackoverflow.com/questions/40940327/what-is-the-simplest-way-to-find-a-slack-team-id-and-a-channel-id)
* `<<your messages file.txt>>` : Contens messages to post. By default **hiChannel.py** will select randomnly wich line to post, but it's possible to force to use the first one (execution param `-first`). You may need several messages files, one for saying Hi!, one for Bye!, another for I'll have a rest, and so on.
* `timetables.txt` : Contens hours, messages files to use after this hour, status message and status icon. It allows to let **hiChannel.py** to determine the messages file to use, acording to the system time. File format is:

`hour before it will use the indicated message file, message file, status message, status icon`
      
Example:
      
```afer_this_hour,use_this_messages_file,status_message,staus_icon
   6,saludos.txt,,:smile:
   10.25,descanso.txt,Break,:coffee:
   13,deVuelta.txt,,:smile:
   13.25,acomer.txt,Lunch Time,:pizza:
   16.5,deVuelta.txt,,:smile:
   17.5,despedida.txt,Hasta Mañana,:zzz:
```

Notes:

* First line will be ommited
* Hours to be indicated in decimal format
* Status icon to be indicated using english name Bonus: [Slack icons names](https://www.webfx.com/tools/emoji-cheat-sheet/)
* You'll find example files in the `Examples` folder.
* Hours must be indicated from earlyer to later (i.e. 10.25 before 13). If not, **hiChannel.py** will raise an error message and stop it's execution.

## Execution parameters

```
C:\Code\Python\HiChannel>hichannel.py --help
usage: hiChannel.py [-h] [-first] [-ChannelsFile CHANNELSFILE] [-verbose] [-test] [-Token TOKEN]
                    [-statusMes STATUSMES] [-StatusIcon STATUSICON] [-confirm] (-auth | -file FILE | -timetable)

Send Hi and Bye messages to several Slack channels

optional arguments:
  -h, --help            show this help message and exit
  -first                Use first messaje of the message files
  -ChannelsFile CHANNELSFILE
                        Set the channels file to use. Default: channels.txt
  -verbose              Verbose mode
  -test                 Test mode. Doesn't send any message
  -Token TOKEN          Slack authentication Token. Default: 'slack_hichannel_Token' (environment variable)
  -statusMes STATUSMES  Message for the status. Overrides 'timetable.txt' status message.
  -StatusIcon STATUSICON
                        Icon for the status-. Overrides 'timetable.txt' status icon.
  -confirm              Ask for confirmations to send messages and change status.
  -auth                 Test authentication. Don't sends message.
  -file FILE            Use this particular file for messages source.
  -timetable            Use 'timetable.txt' to decide the messages file to use according to the system hour.
```

**SUGGESTION:** I love to launch **hiChannel.py** using a `.bat` file. You'll find one example in the `Examples` folder:

```
"C:\Program Files\Python39\python.exe" "c:\Code\Python\HiChannel\hiChannel.py" "-timetable" "-confirm"
exit
```


# Pending improvements

## Functional Improvements

Any suggestion?

## Code Improvements

* Add more code comments and translate some of them already in spanish
* Document function parameters
* Allow use slack python library instead requests one

Any other suggestion?


