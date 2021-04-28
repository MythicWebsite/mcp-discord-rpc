from pypresence import Presence
import time, os, json, socket
import urllib.request
import configparser
from threading import Thread
import asyncio
import PySimpleGUIQt as sg
configParser = configparser.ConfigParser()
socket.setdefaulttimeout(5.0)

# Global Variables
running = True
connected = False
RPC = None
prevGameName = "No game currently running"

# Systemtray setup
menu_def = ['MemcardPro', ['Click icon to refesh current game info on system tray.', 'Game info on Discord refeshes automatically.', '---', 'Exit']]
logo = b'''iVBORw0KGgoAAAANSUhEUgAAACAAAAAgCAYAAABzenr0AAAACXBIWXMAAAsTAAALEwEAmpwYAAAF8WlUWHRYTUw6Y29tLmFkb2JlLnhtcAAAAAAAPD94cGFja2V0IGJlZ2luPSLvu78iIGlkPSJXNU0wTXBDZWhpSHpyZVN6TlRjemtjOWQiPz4gPHg6eG1wbWV0YSB4bWxuczp4PSJhZG9iZTpuczptZXRhLyIgeDp4bXB0az0iQWRvYmUgWE1QIENvcmUgNS42LWMxNDggNzkuMTY0MDM2LCAyMDE5LzA4LzEzLTAxOjA2OjU3ICAgICAgICAiPiA8cmRmOlJERiB4bWxuczpyZGY9Imh0dHA6Ly93d3cudzMub3JnLzE5OTkvMDIvMjItcmRmLXN5bnRheC1ucyMiPiA8cmRmOkRlc2NyaXB0aW9uIHJkZjphYm91dD0iIiB4bWxuczp4bXA9Imh0dHA6Ly9ucy5hZG9iZS5jb20veGFwLzEuMC8iIHhtbG5zOmRjPSJodHRwOi8vcHVybC5vcmcvZGMvZWxlbWVudHMvMS4xLyIgeG1sbnM6cGhvdG9zaG9wPSJodHRwOi8vbnMuYWRvYmUuY29tL3Bob3Rvc2hvcC8xLjAvIiB4bWxuczp4bXBNTT0iaHR0cDovL25zLmFkb2JlLmNvbS94YXAvMS4wL21tLyIgeG1sbnM6c3RFdnQ9Imh0dHA6Ly9ucy5hZG9iZS5jb20veGFwLzEuMC9zVHlwZS9SZXNvdXJjZUV2ZW50IyIgeG1wOkNyZWF0b3JUb29sPSJBZG9iZSBQaG90b3Nob3AgMjEuMCAoV2luZG93cykiIHhtcDpDcmVhdGVEYXRlPSIyMDIxLTA0LTI3VDE5OjMyOjQ1LTA0OjAwIiB4bXA6TW9kaWZ5RGF0ZT0iMjAyMS0wNC0yOFQxMzo0NzoxNy0wNDowMCIgeG1wOk1ldGFkYXRhRGF0ZT0iMjAyMS0wNC0yOFQxMzo0NzoxNy0wNDowMCIgZGM6Zm9ybWF0PSJpbWFnZS9wbmciIHBob3Rvc2hvcDpDb2xvck1vZGU9IjMiIHBob3Rvc2hvcDpJQ0NQcm9maWxlPSJzUkdCIElFQzYxOTY2LTIuMSIgeG1wTU06SW5zdGFuY2VJRD0ieG1wLmlpZDowZmI0YWJhYi0zYjk3LWU1NDEtOTdiMC04MDdhMzI0MjllOTUiIHhtcE1NOkRvY3VtZW50SUQ9ImFkb2JlOmRvY2lkOnBob3Rvc2hvcDo0ZDBiMmExNC0yZGQzLWJmNDktYjlmYi0xYTc5YjE3MDljNmUiIHhtcE1NOk9yaWdpbmFsRG9jdW1lbnRJRD0ieG1wLmRpZDpjZjkyYWRmMS1jMjgyLTU3NDYtYTI5OS00ZDcwZGUyMzMyM2QiPiA8eG1wTU06SGlzdG9yeT4gPHJkZjpTZXE+IDxyZGY6bGkgc3RFdnQ6YWN0aW9uPSJjcmVhdGVkIiBzdEV2dDppbnN0YW5jZUlEPSJ4bXAuaWlkOmNmOTJhZGYxLWMyODItNTc0Ni1hMjk5LTRkNzBkZTIzMzIzZCIgc3RFdnQ6d2hlbj0iMjAyMS0wNC0yN1QxOTozMjo0NS0wNDowMCIgc3RFdnQ6c29mdHdhcmVBZ2VudD0iQWRvYmUgUGhvdG9zaG9wIDIxLjAgKFdpbmRvd3MpIi8+IDxyZGY6bGkgc3RFdnQ6YWN0aW9uPSJzYXZlZCIgc3RFdnQ6aW5zdGFuY2VJRD0ieG1wLmlpZDowZmI0YWJhYi0zYjk3LWU1NDEtOTdiMC04MDdhMzI0MjllOTUiIHN0RXZ0OndoZW49IjIwMjEtMDQtMjhUMTM6NDc6MTctMDQ6MDAiIHN0RXZ0OnNvZnR3YXJlQWdlbnQ9IkFkb2JlIFBob3Rvc2hvcCAyMS4wIChXaW5kb3dzKSIgc3RFdnQ6Y2hhbmdlZD0iLyIvPiA8L3JkZjpTZXE+IDwveG1wTU06SGlzdG9yeT4gPC9yZGY6RGVzY3JpcHRpb24+IDwvcmRmOlJERj4gPC94OnhtcG1ldGE+IDw/eHBhY2tldCBlbmQ9InIiPz4CIxkhAAAGxklEQVRYheWXW3BdZRXHf9+3L+d+TpKTe9MQmkSTtoSkpdjOVKFjq1ZERmSwWmeoI+Pomw+KjOOQFxGRcYYXFGf0QRxBR8RLoZbAlDLlUrEEKW1S0jRpLiXNSXJOzn2ffft86E00qb3A9ME1s1/2Xnut/6z1X/9vfUIpxbU0eU2zA/rwjx+/JEdNakjbCbycnm49kQiMWcm456EIFC2Clo3mgxJXAOAFe+GSHO1QgEQuG1n/x1d/3VkbHJvqbH1pqqtld6YmlsomIhiFEuFCBU1d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'''
tray = sg.SystemTray(menu=menu_def, data_base64=logo, tooltip="MCP Discord RPC")

# Set Discord connection info
configParser.read(os.getcwd() + "//config.txt")
addr = "http://" + configParser.get('config', 'mcp_local_ip') + "/api/currentState"
client_id = configParser.get('config', 'client_id')
refresh_delay = int(configParser.get('config', 'refresh_delay'))
wait_on_fail = int(configParser.get('config', 'wait_on_fail'))
default_image = configParser.get('config', 'default_image')
RPC = Presence(client_id, pipe=0)


# Discord Presence
def memwhile():
    asyncio.set_event_loop(event_loop)
    global running
    global connected
    global RPC
    global prevGameName
    while running is True:
        # First connection or connection after connection failure
        try:
            print("Connecting...")
            prevGameData = json.loads(urllib.request.urlopen(addr, timeout=5.0).read().decode())
            if connected is False:
                RPC.connect()
                connected = True
            prevGameName = prevGameData['gameName']
            prevGameID = prevGameData['gameID'].lower()
            starttime = time.time()
            status = RPC.update(details=prevGameName, start=starttime, large_image=prevGameID)
            if not status['data']['assets']:
                status = RPC.update(details=prevGameName, start=starttime, large_image=default_image)
            print(status)

            # Loop to update game info
            while running is True:
                for i in range(refresh_delay):
                    if running is False:
                        break
                    time.sleep(1)
                curGameData = json.loads(urllib.request.urlopen(addr).read().decode())
                curGameName = curGameData['gameName']
                if prevGameName != curGameName:
                    prevGameName = curGameName
                    prevGameID = curGameData['gameID'].lower()
                    starttime = time.time()
                    status = RPC.update(details=prevGameName, start=starttime, large_image=prevGameID)

                    if not status['data']['assets']:
                        status = RPC.update(details=prevGameName, start=starttime, large_image=default_image)
                    print(status)

        # If connection to MemcardPro or Discord fails
        except Exception:
            if connected is True:
                RPC.close()
            connected = False
            prevGameName = "No game currently running"
            print('Connection failed, trying again in ' + str(wait_on_fail) + ' seconds...')
            for i in range(wait_on_fail):
                if running is False:
                    break
                time.sleep(1)


# Run the systemtray
def systray():
    global running
    global prevGameName
    while running is True:
        menu_item = tray.Read()
        menu_def = ['MemcardPro', [prevGameName, '---', 'Exit']]
        tray.Update(menu=menu_def)
        if menu_item == 'Exit':
            tray.Update(tooltip="Closing...")
            print("Closing...")
            running = False


event_loop = asyncio.new_event_loop()
t2 = Thread(target=memwhile)
t2.start()
systray()
