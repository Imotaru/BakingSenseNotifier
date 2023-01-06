import datetime
import tkinter
from webbot import Browser
from playsound import playsound
from functools import partial


root = tkinter.Tk()
root.title("Baking a lot of sense")
root.iconbitmap("Icn_Broccoli.ico")
SETTINGS_FILE = "settings.txt"
FOOD_URL = "https://bakingsense.net/food"
INVALID_STRING = "error"


def clean_string(dirty_text: str):
    return dirty_text.strip('\x00').strip("\n")


def load_settings():
    file = open(SETTINGS_FILE, "r")
    data = file.readlines()
    file.close()
    return data


def save_settings(data):
    file = open(SETTINGS_FILE, "r+")
    file.truncate(0)
    for i in range(0, len(data)):
        file.write((clean_string(data[i])) + "\n")
    file.close()


def get_setting(row_name: str) -> str:
    data = load_settings()
    for row in data:
        clean_row = clean_string(row)
        if clean_row.startswith(row_name):
            return clean_row[(len(row_name) + 2):]
        
    return INVALID_STRING


def try_get_setting(row_name: str, alternative_value: str) -> str:
    value = get_setting(row_name)
    if value == INVALID_STRING:
        return alternative_value
    return value


def get_settings_index(row_name: str):
    data = load_settings()
    return get_setting_index_by_data(row_name, data)


def get_setting_index_by_data(rowName, data):
    for i in range(0, len(data)):
        if clean_string(data[i]).startswith(rowName):
            return i

    return -1


def change_setting(rowName, newValue):
    data = load_settings()
    index = get_setting_index_by_data(rowName, data)
    new_row = rowName + ": " + newValue
    if index == -1:
        data.append(new_row)
    else:
        data[index] = new_row
    
    save_settings(data)


WIDTH = 800
HEIGHT = 600

background_color = try_get_setting("backgroundColor", "#202020")
output_log_frame_color = try_get_setting("outputlogFrameColor", "#505050")
primary_text_color = try_get_setting("primaryTextColor", "#00FF00")
secondary_text_color = try_get_setting("secondaryTextColor", "#A59263")
button_bg_color = try_get_setting("btnBgColor", "#505050")
btn_text_color = try_get_setting("btnTextColor", primary_text_color)

canvas = tkinter.Canvas(root, width=WIDTH, height=HEIGHT)
main_frame = tkinter.Frame(canvas, bg=background_color, bd=10)
console_frame = tkinter.Frame(canvas, bg=output_log_frame_color, bd=10)

output_log = tkinter.Label(console_frame, bg=background_color, fg=secondary_text_color, anchor="nw", justify="left", bd=10)
username_entry = tkinter.Entry(main_frame)
password_entry = tkinter.Entry(main_frame, show="*")
meal_link_entry = tkinter.Entry(main_frame)
mean_name_entry = tkinter.Entry(main_frame)
meal_number_entry = tkinter.Entry(main_frame)

username = None
loggedIn = False
web = None

order_buttons = []
cancel_order_buttons = []
btnTimerLabels = []

awaiting_buttons = []

PHI = 1.618

ORDER_BTN_REL_X = 0.08
ORDER_BTN_REL_Y = 0.4
ORDER_BTN_STEP_X = 0.2
ORDER_BTN_STEP_Y = 0.15
ORDER_BTN_WIDTH = 0.117
ORDER_BTN_HEIGHT = 0.1


def output(message):
    output_log['text'] = message + "\n" + output_log['text']


def login():
    global loggedIn
    global username
    global web

    if not loggedIn:
        output("starting browser")
        web = Browser(showWindow=False)
        web.go_to(FOOD_URL)

        if web.get_page_source().count("password") > 1:
            if get_settings_index("username") == -1 or get_settings_index("password") == -1:
                output("Username or password not set, can't log in")
            else:
                username = get_setting("username")
                web.type(username, into="username")
                web.type(get_setting("password"), into="password")
                web.press(web.Key().ENTER)
                loggedIn = True
                # TODO: check if login was actually successful
                output("logged in")


def notify():
    output("Enjoy your meal :)")
    playsound("chime.wav")
    # window = tkinter.Toplevel(root)
    # tkinter.Label(window, text="ayy").pack()
    # root.focus_force()


def await_meal(meal_id: int):
    login()
    web.go_to(FOOD_URL)
    if meal_id != 0:
        awaiting_buttons.append(meal_id)
        btnTimerLabels[meal_id - 1]["text"] = "Counting Lentils..."

    def wait_loop():
        try:
            if web.get_page_source().count(username) > 1:
                root.after(60000, wait_loop)
            else:
                notify()
                if meal_id != 0:
                    btnTimerLabels[meal_id - 1]["text"] = datetime.datetime.strftime(datetime.datetime.today(), '%H:%M')
                    awaiting_buttons.remove(meal_id)
                    cancel_order_buttons[meal_id - 1].place_forget()
        except:
            output("An exception occured but was caught")
            root.after(60000, wait_loop)

    wait_loop()


def set_username():
    new_name = username_entry.get()
    change_setting("username", new_name)
    output("username set to: " + new_name)


def set_password():
    change_setting("password", password_entry.get())
    output("password updated")


def set_meal(id, name, link):
    editing = get_settings_index("meal" + str(id)) != -1

    # input handling
    if id > 16 or id < 1:
        output("invalid ID, make sure the ID is between 1 and 16")
        return

    link = link.strip(' ')
    if not link.startswith(FOOD_URL + "/") and not editing:
        output("invalid link, go to your profile, click on a meal and copy that link")
        return

    if name == "[name]" or name.strip(' ') == "":
        if editing:
            name = get_setting("meal" + str(id) + "name")
        else:
            name = "Meal " + str(id)

    if editing:
        order_buttons[id - 1]["text"] = name

    if link.startswith(FOOD_URL + "/"):
        change_setting("meal" + str(id), link)

    change_setting("meal" + str(id) + "name", name)
    output("Meal " + str(id) + " set to " + link)

    if not editing:
        x = (id-1) % 4
        y = int((id-1) / 4)

        order_buttons[id - 1] = (tkinter.Button(main_frame, text = meal_name, fg = btn_text_color, bg = button_bg_color, font = ("Arial", 10), command = orderCommand))
        order_buttons[id - 1].place(relx =ORDER_BTN_REL_X + (ORDER_BTN_STEP_X * x), rely =ORDER_BTN_REL_Y + (ORDER_BTN_STEP_Y * y), relwidth = ORDER_BTN_WIDTH, relheight = ORDER_BTN_HEIGHT)
        cancel_order_buttons[id - 1] = (tkinter.Button(main_frame, text ="Cancel", fg = secondary_text_color, bg ="#AA0000", font = ("Arial", 10), command = cancel_order))

        btnTimerLabels[id - 1] = (tkinter.Label(main_frame, text ="", fg = secondary_text_color, bg = background_color, font = ("Arial", 8)))
        btnTimerLabels[id - 1].place(relx =ORDER_BTN_REL_X + (ORDER_BTN_STEP_X * x), rely =ORDER_BTN_REL_Y + 0.11 + (ORDER_BTN_STEP_Y * y), relwidth = ORDER_BTN_WIDTH, relheight = 0.03)




def order_meal(meal_id):
    if meal_id in awaiting_buttons:
        output("Meal being made")
        return
    login()
    web.go_to(get_setting("meal" + str(meal_id)))
    web.click("Good Morning")
    web.go_to(FOOD_URL)

    x = (meal_id - 1) % 4
    y = int((meal_id - 1) / 4)
    cancel_order_buttons[meal_id - 1].place(relx =ORDER_BTN_REL_X + ORDER_BTN_WIDTH + (ORDER_BTN_STEP_X * x), rely =ORDER_BTN_REL_Y + (ORDER_BTN_STEP_Y * y), relwidth = (ORDER_BTN_WIDTH / PHI), relheight = ORDER_BTN_HEIGHT)

    # TODO: show the time when the meal is expected to come
    output("Order placed for " + get_setting("meal" + str(meal_id) + "name"))
    await_meal(meal_id)


def find_information(source, starting_location, end_location):
    i = source.find(starting_location)
    information = source[i + len(starting_location):]
    i = information.find(end_location)
    information = information[:i]
    return information


# TODO: not working yet
def cancel_order(order_id):
    output("the order would probably be canceled now if this feature was implemented")
    login()
    web.go_to(get_setting("meal" + str(order_id)))
    source = str(web.get_page_source())
    print(source)

    name = find_information(source, "<h1 class=\"text-center\">", "</h1>")
    image = find_information(source, "<img class=\"img-responsive\" src=\"", "\" />")

    # this information is flawed, it doesn't represent the actual settings
    # breakfastSet = FindInformation(source, "<p>Breakfast: ", "</p>")
    # lunchSet = FindInformation(source, "<p>Lunch: ", "</p>")
    # dinnerSet = FindInformation(source, "<p>Dinner: ", "</p>")
    # extraSet = FindInformation(source, "<p>Extra: ", "</p>")

    away_mode = find_information(source, "<p>AwayMode: ", "</p>")

    allergy = find_information(source, "<p id=\"allergy\">Allergy:", "</p>")

    location = find_information(source, "<p>Location: ", "</p>")
    meal_size = find_information(source, "<p>Meal Size: ", "</p>")

    # breakfastDesc = FindInformation(source, "<p>Extra: ", "</p>")

    print(away_mode)
    print(allergy)
    print(location)
    print(meal_size)
    # get description for every meal
    # get times
    # get dynamic setting

    # get meal information
    # delete meal
    # create new meal
    # input information and save
    # update link

canvas.pack()
main_frame.place(relx=0, rely=0, relwidth=1, relheight=0.8)
console_frame.place(relx=0, rely=0.8, relwidth=1, relheight=0.2)

startBtn = tkinter.Button(main_frame, text="Await", fg=btn_text_color, bg=button_bg_color, font=("Arial", 16), command=lambda: await_meal(0))
startBtn.place(relx=0.1, rely=0.1, relwidth=0.25, relheight=0.1)

username_entry.place(relx=0.73, rely=0.05, relwidth=0.1, relheight=0.05)
password_entry.place(relx=0.73, rely=0.11, relwidth=0.1, relheight=0.05)

changeUsernameBtn = tkinter.Button(main_frame, text="Set Username", fg=btn_text_color, bg=button_bg_color, font=("Arial", 10), command=set_username)
changeUsernameBtn.place(relx=0.84, rely=0.05, relwidth=0.15, relheight=0.05)

changePasswordBtn = tkinter.Button(main_frame, text="Set Password", fg=btn_text_color, bg=button_bg_color, font=("Arial", 10), command=set_password)
changePasswordBtn.place(relx=0.84, rely=0.11, relwidth=0.15, relheight=0.05)

meal_link_entry.place(relx=0.73, rely=0.17, relwidth=0.1, relheight=0.05)
meal_link_entry.insert(0, "[link]")
mean_name_entry.place(relx=0.62, rely=0.17, relwidth=0.1, relheight=0.05)
mean_name_entry.insert(0, "[name]")
meal_number_entry.place(relx=0.55, rely=0.17, relwidth=0.06, relheight=0.05)
meal_number_entry.insert(0, "[id 1-16]")

setMealBtn = tkinter.Button(main_frame, text="Set Meal", fg=btn_text_color, bg=button_bg_color, font=("Arial", 10), command=lambda: set_meal(int(meal_number_entry.get().strip(' ')), mean_name_entry.get(), meal_link_entry.get()))
setMealBtn.place(relx=0.84, rely=0.17, relwidth=0.15, relheight=0.05)


for ui_loop_y in range(0, 4):
    for ui_loop_x in range(0, 4):
        ui_loop_index = ui_loop_y * 4 + ui_loop_x
        if get_settings_index("meal" + str(ui_loop_index + 1)) != -1:
            orderCommand = partial(order_meal, (ui_loop_index + 1))
            cancelCommand = partial(cancel_order, (ui_loop_index + 1))
            meal_name = get_setting("meal" + str(ui_loop_index + 1) + "name")
            if meal_name == INVALID_STRING:
                meal_name = "Meal " + str((ui_loop_index + 1))
            order_buttons.append(tkinter.Button(main_frame, text=meal_name, fg=btn_text_color, bg=button_bg_color, font=("Arial", 10), command=orderCommand))
            order_buttons[ui_loop_index].place(relx=ORDER_BTN_REL_X + (ORDER_BTN_STEP_X * ui_loop_x), rely=ORDER_BTN_REL_Y + (ORDER_BTN_STEP_Y * ui_loop_y), relwidth=ORDER_BTN_WIDTH, relheight=ORDER_BTN_HEIGHT)

            cancel_order_buttons.append(tkinter.Button(main_frame, text="Cancel", fg=secondary_text_color, bg="#AA0000", font=("Arial", 10), command=cancelCommand))

            btnTimerLabels.append(tkinter.Label(main_frame, text="", fg=secondary_text_color, bg=background_color, font=("Arial", 8)))
            btnTimerLabels[ui_loop_index].place(relx=ORDER_BTN_REL_X + (ORDER_BTN_STEP_X * ui_loop_x), rely=ORDER_BTN_REL_Y + 0.11 + (0.15 * ui_loop_y), relwidth=ORDER_BTN_WIDTH, relheight=0.03)
        else:
            order_buttons.append(None)
            btnTimerLabels.append(None)
            cancel_order_buttons.append(None)

output_log.place(relx=0, rely=0, relwidth=1, relheight=1)

root.mainloop()
