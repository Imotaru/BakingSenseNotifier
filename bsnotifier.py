# import time
import datetime
import tkinter as tk
from webbot import Browser
from playsound import playsound
# import winsound
# import asyncio
from functools import partial


root = tk.Tk()
root.title("Baking a lot of sense")
root.iconbitmap("Icn_Broccoli.ico")

invalidString = "error"


def Cleanstr(dirtytext: str):
    return dirtytext.strip('\x00').strip("\n")


def GetDataFromFile():
    file = open("settings.txt", "r")
    data = file.readlines()
    file.close()
    return data


def SaveFile(data):
    file = open("settings.txt", "r+")
    file.truncate(0)
    for x in range (0, len(data)):
        file.write((Cleanstr(data[x])) + "\n")
    file.close()


def GetSetting(rowName):
    data = GetDataFromFile()
    for row in data:
        cleanrow = Cleanstr(row)
        if(cleanrow.startswith(rowName)):
            return cleanrow[(len(rowName) + 2):]
        
    return invalidString


def TryGetSetting(rowName, alternativeValue):
    value = GetSetting(rowName)
    if(value == invalidString):
        return alternativeValue
    return value


def GetSettingIndex(rowName):
    data = GetDataFromFile()
    return GetSettingIndexByData(rowName, data)


def GetSettingIndexByData(rowName, data):
    for x in range(0, len(data)):
        if(Cleanstr(data[x]).startswith(rowName)):
            return x

    return -1


def ChangeSetting(rowName, newValue):
    data = GetDataFromFile()
    index = GetSettingIndexByData(rowName, data)
    newRow = rowName + ": " + newValue
    if(index == -1):
        data.append(newRow)
    else:
        data[index] = newRow
    
    SaveFile(data)


WIDTH = 800
HEIGHT = 600

backgroundColor = TryGetSetting("backgroundColor", "#202020")
outputlogFrameColor = TryGetSetting("outputlogFrameColor", "#505050")
primaryTextColor = TryGetSetting("primaryTextColor", "#00FF00")
secondaryTextColor = TryGetSetting("secondaryTextColor", "#A59263")
btnBgColor = TryGetSetting("btnBgColor", "#505050")
btnTextColor = TryGetSetting("btnTextColor", primaryTextColor)

canvas = tk.Canvas(root, width = WIDTH, height = HEIGHT)
mainFrame = tk.Frame(canvas, bg = backgroundColor, bd = 10)
consoleFrame = tk.Frame(canvas, bg = outputlogFrameColor, bd = 10)

outputlog = tk.Label(consoleFrame, bg = backgroundColor, fg = secondaryTextColor, anchor = "nw", justify = "left", bd = 10)
usernameEntry = tk.Entry(mainFrame)
passwordEntry = tk.Entry(mainFrame, show="*")
mealLinkEntry = tk.Entry(mainFrame)
mealNameEntry = tk.Entry(mainFrame)
mealNumberEntry = tk.Entry(mainFrame)

username = None
loggedIn = False

foodurl = "https://bakingsense.net/food"

web = None

orderBtns = []
cancelOrderBtns = []
btnTimerLabels = []

awaitingButtons = []

phi = 1.618

orderBtnRelX = 0.08
orderBtnRelY = 0.4
orderBtnStepX = 0.2
orderBtnStepY = 0.15
orderBtnWidth = 0.117
orderBtnHeight = 0.1


def Output(message):
    outputlog['text'] = message + "\n" + outputlog['text']

def Login():
    global loggedIn
    global username
    global web

    if(not loggedIn):
        Output("starting browser")
        web = Browser(showWindow=False)
        web.go_to(foodurl)

        if(web.get_page_source().count("password") > 1):
            if(GetSettingIndex("username") == -1 or GetSettingIndex("password") == -1):
                Output("Username or password not set, can't log in")
            else: 
                username = GetSetting("username")
                web.type(username, into="username")
                web.type(GetSetting("password"), into="password")
                web.press(web.Key().ENTER)
                loggedIn = True
                # TODO: check if login was actually successful
                Output("logged in")



def Notify():
    Output("Enjoy your meal :)")
    playsound("chime.wav")
    # window = tk.Toplevel(root)
    # tk.Label(window, text="ayy").pack()
    # root.focus_force()

def AwaitMeal(id):
    Login()
    web.go_to(foodurl)
    if(id != 0):
        awaitingButtons.append(id)
        btnTimerLabels[id-1]["text"] = "Counting Lentils..."

    def waitloop():
        try:
            if web.get_page_source().count(username) > 1:
                root.after(60000, waitloop)
            else:
                Notify()
                if(id != 0):
                    btnTimerLabels[id - 1]["text"] = datetime.datetime.strftime(datetime.datetime.today() , '%H:%M')
                    awaitingButtons.remove(id)
                    cancelOrderBtns[id - 1].place_forget()
        except:
            Output("An exception occured but was caught")
            root.after(60000, waitloop)

    waitloop()

def SetUsername():
    newName = usernameEntry.get()
    ChangeSetting("username", newName)
    Output("username set to: " + newName)

def SetPassword():
    ChangeSetting("password", passwordEntry.get())
    Output("password updated")

def SetMeal(id, name, link):
    editing = GetSettingIndex("meal" + str(id)) != -1

    # input handling
    if(id > 16 or id < 1):
        Output("invalid ID, make sure the ID is between 1 and 16")
        return

    link = link.strip(' ')
    if(not link.startswith(foodurl + "/") and not editing):
        Output("invalid link, go to your profile, click on a meal and copy that link")
        return

    if(name == "[name]" or name.strip(' ') == ""):
        if(editing):
            name = GetSetting("meal" + str(id) + "name")
        else:
            name = "Meal " + str(id)



    if(editing):
        orderBtns[id - 1]["text"] = name

    if(link.startswith(foodurl + "/")):
        ChangeSetting("meal" + str(id), link)

    ChangeSetting("meal" + str(id) + "name", name)
    Output("Meal " + str(id) + " set to " + link)

    if(not editing):
        x = (id-1) % 4
        y = int((id-1) / 4)

        orderBtns[id - 1] = (tk.Button(mainFrame, text = mealname, fg = btnTextColor, bg = btnBgColor, font = ("Arial", 10), command = orderCommand))
        orderBtns[id - 1].place(relx = orderBtnRelX + (orderBtnStepX * x), rely = orderBtnRelY + (orderBtnStepY * y), relwidth = orderBtnWidth, relheight = orderBtnHeight)
        cancelOrderBtns[id - 1] = (tk.Button(mainFrame, text = "Cancel", fg = secondaryTextColor, bg = "#AA0000", font = ("Arial", 10), command = CancelOrder))

        btnTimerLabels[id - 1] = (tk.Label(mainFrame, text = "", fg = secondaryTextColor, bg = backgroundColor, font = ("Arial", 8)))
        btnTimerLabels[id - 1].place(relx = orderBtnRelX + (orderBtnStepX * x), rely = orderBtnRelY + 0.11 + (orderBtnStepY * y), relwidth = orderBtnWidth, relheight = 0.03)




def OrderMeal(id):
    if(id in awaitingButtons):
        Output("Meal being made")
        return
    Login()
    web.go_to(GetSetting("meal" + str(id)))
    web.click("Good Morning")
    web.go_to(foodurl)

    x = (id-1) % 4
    y = int((id-1) / 4)
    cancelOrderBtns[id - 1].place(relx = orderBtnRelX + orderBtnWidth + (orderBtnStepX * x), rely = orderBtnRelY + (orderBtnStepY * y), relwidth = (orderBtnWidth / phi), relheight = orderBtnHeight)

    # TODO: show the time when the meal is expected to come
    Output("Order placed for " + GetSetting("meal" + str(id) + "name"))
    AwaitMeal(id)

def FindInformation(source, startingLocation, endLocation):
    i = source.find(startingLocation)
    information = source[i + len(startingLocation):]
    i = information.find(endLocation)
    information = information[:i]
    return information

# TODO: not working yet
def CancelOrder(id):
    Output("the order would probably be canceled now if this feature was implemented")
    Login()
    web.go_to(GetSetting("meal" + str(id)))
    source = str(web.get_page_source())
    print(source)

    name = FindInformation(source, "<h1 class=\"text-center\">", "</h1>")
    image = FindInformation(source, "<img class=\"img-responsive\" src=\"", "\" />")

    # this information is flawed, it doesn't represent the actual settings
    # breakfastSet = FindInformation(source, "<p>Breakfast: ", "</p>")
    # lunchSet = FindInformation(source, "<p>Lunch: ", "</p>")
    # dinnerSet = FindInformation(source, "<p>Dinner: ", "</p>")
    # extraSet = FindInformation(source, "<p>Extra: ", "</p>")

    awaymode = FindInformation(source, "<p>AwayMode: ", "</p>")

    allergy = FindInformation(source, "<p id=\"allergy\">Allergy:", "</p>")

    location = FindInformation(source, "<p>Location: ", "</p>")
    mealsize = FindInformation(source, "<p>Meal Size: ", "</p>")

    # breakfastDesc = FindInformation(source, "<p>Extra: ", "</p>")

    print(awaymode)
    print(allergy)
    print(location)
    print(mealsize)
    # get description for every meal
    # get times
    # get dynamic setting


    # get meal information
    # delete meal
    # create new meal
    # input information and save
    # update link

def MakeSettingsBackup():
    data = GetDataFromFile()
    file = open("settingsbackup.txt", "r+")
    file.truncate(0)
    for x in range (0, len(data)):
        file.write((Cleanstr(data[x])) + "\n")
    file.close()

def LoadSettingsBackup():
    file = open("settings.txt", "r")
    data = file.readlines()
    file.close()
    SaveFile(data)


canvas.pack()
mainFrame.place(relx = 0, rely = 0, relwidth = 1, relheight = 0.8)
consoleFrame.place(relx = 0, rely = 0.8, relwidth = 1, relheight = 0.2)

startBtn = tk.Button(mainFrame, text = "Await", fg = btnTextColor, bg = btnBgColor, font = ("Arial", 16), command = lambda: AwaitMeal(0))
startBtn.place(relx = 0.1, rely = 0.1, relwidth = 0.25, relheight = 0.1)

usernameEntry.place(relx = 0.73, rely = 0.05, relwidth = 0.1, relheight = 0.05)
passwordEntry.place(relx = 0.73, rely = 0.11, relwidth = 0.1, relheight = 0.05)

changeUsernameBtn = tk.Button(mainFrame, text = "Set Username", fg = btnTextColor, bg = btnBgColor, font = ("Arial", 10), command = SetUsername)
changeUsernameBtn.place(relx = 0.84, rely = 0.05, relwidth = 0.15, relheight = 0.05)

changePasswordBtn = tk.Button(mainFrame, text = "Set Password", fg = btnTextColor, bg = btnBgColor, font = ("Arial", 10), command = SetPassword)
changePasswordBtn.place(relx = 0.84, rely = 0.11, relwidth = 0.15, relheight = 0.05)

mealLinkEntry.place(relx = 0.73, rely = 0.17, relwidth = 0.1, relheight = 0.05)
mealLinkEntry.insert(0, "[link]")
mealNameEntry.place(relx = 0.62, rely = 0.17, relwidth = 0.1, relheight = 0.05)
mealNameEntry.insert(0, "[name]")
mealNumberEntry.place(relx = 0.55, rely = 0.17, relwidth = 0.06, relheight = 0.05)
mealNumberEntry.insert(0, "[id 1-16]")

setMealBtn = tk.Button(mainFrame, text = "Set Meal", fg = btnTextColor, bg = btnBgColor, font = ("Arial", 10), command = lambda: SetMeal(int(mealNumberEntry.get().strip(' ')), mealNameEntry.get(), mealLinkEntry.get()))
setMealBtn.place(relx = 0.84, rely = 0.17, relwidth = 0.15, relheight = 0.05)


for y in range(0, 4):
    for x in range(0, 4):
        index = y * 4 + x
        if(GetSettingIndex("meal" + str(index + 1)) != -1):
            orderCommand = partial(OrderMeal, (index + 1))
            cancelCommand = partial(CancelOrder, (index + 1))
            mealname = GetSetting("meal" + str(index + 1) + "name")
            if mealname == invalidString:
                mealname = "Meal " + str((index + 1))
            orderBtns.append(tk.Button(mainFrame, text = mealname, fg = btnTextColor, bg = btnBgColor, font = ("Arial", 10), command = orderCommand))
            orderBtns[index].place(relx = orderBtnRelX + (orderBtnStepX * x), rely = orderBtnRelY + (orderBtnStepY * y), relwidth = orderBtnWidth, relheight = orderBtnHeight)

            cancelOrderBtns.append(tk.Button(mainFrame, text = "Cancel", fg = secondaryTextColor, bg = "#AA0000", font = ("Arial", 10), command = cancelCommand))

            btnTimerLabels.append(tk.Label(mainFrame, text = "", fg = secondaryTextColor, bg = backgroundColor, font = ("Arial", 8)))
            btnTimerLabels[index].place(relx = orderBtnRelX + (orderBtnStepX * x), rely = orderBtnRelY + 0.11 + (0.15 * y), relwidth = orderBtnWidth, relheight = 0.03)
        else:
            orderBtns.append(None)
            btnTimerLabels.append(None)
            cancelOrderBtns.append(None)

outputlog.place(relx = 0, rely = 0, relwidth = 1, relheight = 1)

root.mainloop()