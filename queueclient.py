from tkinter import *
from tkinter import scrolledtext as st
from configparser import ConfigParser
import os
import json
import datetime
import webbrowser
import pip

def pinstall(package):
    pip.main(['install', package])

try:
    import requests
except:
    pinstall('requests')
    import requests

### CONSTANTS ###

HEADER = "https://www.speedrun.com/api/v1/"
OFFSET_LIMIT = 20
TRUE_VALUES = ['true', 'yes', '1']

#################

options = ConfigParser()
options.read(os.path.join(os.path.dirname(os.path.realpath(__file__)), 'options.txt'))

game_str = options['options']['game']
API_KEY = options['options']['api_key']
stay_on_top = options['options']['stay_on_top'].lower() in TRUE_VALUES
sort_by_date = options['options']['sort_by_date'].lower() in TRUE_VALUES
examine_also_opens = options['options']['examine_also_opens'].lower() in TRUE_VALUES

if float(options['options']['gamma']) > 5:
    raise ValueError("Turn your gamma down idiot")

def log(message):
    console.configure(state = NORMAL)
    console.insert(INSERT, '\n' + message)
    console.see(END)
    console.configure(state = DISABLED)

def json_from_url(url):
    return requests.get(url).json()

def json_from_src(short_url):
    return json_from_url(HEADER + short_url)

def continual_data(short_url):
    hold = []
    temp = json_from_src(short_url + ("&max=200" if '?' in short_url else "?max=200"))
    while True:
        hold.extend(temp['data'])
        if 'pagination' not in temp or temp['pagination']['size'] < 200:
            break
        temp = json_from_url({item['rel']: item['uri']
                              for item in temp['pagination']['links']}['next'])
    return hold

def get_queue(game_id):
    return continual_data(f"runs?game={game_id}&status=new&embed=players")

def reject_run(run_id, reason):
    log(f"Attempting to reject run {run_id}")
    rej_json = {'status': {'status': 'rejected', 'reason': reason}}
    r = requests.put(f"{HEADER}runs/{run_id}/status",
                     data = json.dumps(rej_json),
                     headers = {'X-API-Key': API_KEY,
                                'Accept': 'application/json'})
    log(f"Status: {r.status_code}")
    if r.status_code != 200:
        try:
            log(f"Something went wrong: {r.json()['message']}")
        except:
            log(f"Something went wrong: {r.text}")
    return r.status_code

def verify_run(run_id):
    log(f"Attempting to verify run {run_id}")
    rej_json = {'status': {'status': 'verified'}}
    r = requests.put(f"{HEADER}runs/{run_id}/status",
                     data = json.dumps(rej_json),
                     headers = {'X-API-Key': API_KEY,
                                'Accept': 'application/json'})
    log(f"Status: {r.status_code}")
    if r.status_code != 200:
        try:
            log(f"Something went wrong: {r.json()['message']}")
        except:
            log(f"Something went wrong: {r.text}")
    return r.status_code

def str_time(seconds, milliseconds = 0):
    minutes, seconds = divmod(seconds, 60)
    hours, minutes = divmod(minutes, 60)
    if hours != 0:
        if milliseconds:
            return "{0}:{1:0>2}:{2:0>2}.{3:0>3}".format(hours, minutes, seconds, milliseconds)
        else:
            return "{0}:{1:0>2}:{2:0>2}".format(hours, minutes, seconds)
    elif minutes != 0:
        if milliseconds:
            return "{0}:{1:0>2}.{2:0>3}".format(minutes, seconds, milliseconds)
        else:
            return "{0}:{1:0>2}".format(minutes, seconds)
    elif seconds != 0:
        if milliseconds:
            return "{0}.{1:0>3}".format(seconds, milliseconds)
        else:
            return "0:{0:0>2}".format(seconds)
    else:
        return "0.{0:0>3}".format(milliseconds)

class Run:
    def __init__(self, run):
        self.run_object = run
        self.status = 'pending'

    @property
    def players(self):
        return [(player['names']['international']
                 if player['rel'] == 'user'
                 else player['name'])
                for player in self.run_object['players']['data']]

    @property
    def players_newline(self):
        return '\n'.join(self.players)

    @property
    def players_comma(self):
        return ', '.join(self.players)

    @property
    def category(self):
        return cat_map[self.run_object['category']]

    @property
    def level(self):
        return level_map[self.run_object['level']]

    @property
    def full_category(self):
        subcatvals = [subcat_map[val]
                      for val in self.run_object['values'].values()
                      if val in subcat_map]
        
        if self.run_object['level'] is None:
            main = self.category
        else:
            main = self.level
            subcatvals = [self.category] + subcatvals
            
        if len(subcatvals) > 0:
            return main + ' - ' + ', '.join(subcatvals)
        else:
            return main

    @property
    def primary_time(self):
        return (None if self.run_object['times']['primary'] is None
                else str_time(*divmod(round(self.run_object['times']['primary_t'] * 1000), 1000)))

    @property
    def real_time(self):
        return (None if self.run_object['times']['realtime'] is None
                else str_time(*divmod(round(self.run_object['times']['realtime_t'] * 1000), 1000)))

    @property
    def noloads_time(self):
        return (None if self.run_object['times']['realtime_noloads'] is None
                else str_time(*divmod(round(self.run_object['times']['realtime_noloads_t'] * 1000), 1000)))

    @property
    def ingame_time(self):
        return (None if self.run_object['times']['ingame'] is None
                else str_time(*divmod(round(self.run_object['times']['ingame_t'] * 1000), 1000)))

    @property
    def description(self):
        return (None if self.run_object['comment'] is None
                else self.run_object['comment'].replace('\r\n', '\n'))

    @property
    def var_string(self):
        return '\n'.join([f"{var_map[var]}: {var_map[val]}"
                          for var, val in self.run_object['values'].items()
                          if val not in subcat_map])

    @property
    def status_color(self):
        if self.status == 'verified':
            return 'SpringGreen3'
        elif self.status == 'rejected':
            return 'IndianRed1'
        else:
            return None

    def open_run(self):
        webbrowser.open(self.run_object['weblink'])

    def update_color(self):
        self.examine_button.configure(bg = self.status_color)

    def display(self):
        next_row = queue_display.grid_size()[1]
        self.cat_label = Label(queue_display, text = self.full_category)
        self.cat_label.grid(row = next_row, column = 1)
        self.players_label = Label(queue_display, text = self.players_newline)
        self.players_label.grid(row = next_row, column = 2)
        self.time_label = Label(queue_display, text = self.primary_time)
        self.time_label.grid(row = next_row, column = 3)
        self.date_label = Label(queue_display, text = self.run_object['date'])
        self.date_label.grid(row = next_row, column = 4)
        self.examine_button = Button(queue_display, text = "Examine", command = self.examine,
                                     bg = self.status_color, relief = FLAT)
        self.examine_button.grid(row = next_row, column = 5)
        self.open_button = Button(queue_display, text = "Open", command = self.open_run, relief = FLAT)
        self.open_button.grid(row = next_row, column = 6)

    def mark_verified(self):
        self.status = 'verified'
        self.update_color()

    def mark_rejected(self):
        self.status = 'rejected'
        self.update_color()

    def mark_pending(self):
        self.status = 'pending'
        self.update_color()
    
    def verify(self):
        reason = self.reason_entry.get('1.0', 'end-1c')
        if reason == '':
            log(f"Cannot verify run {self.run_object['id']} for no reason")
        else:
            verify_request = verify_run(self.run_object['id'])
            if verify_request == 200:
                self.mark_verified()

    def reject(self):
        reason = self.reason_entry.get('1.0', 'end-1c')
        if reason == '':
            log(f"Cannot reject run {self.run_object['id']} for no reason")
        else:
            reject_request = reject_run(self.run_object['id'], reason)
            if reject_request == 200:
                self.mark_rejected()

    def examine(self):
        if examine_also_opens:
            self.open_run()
        self.popup = Tk()
        self.popup.title("Run Examination")
        self.popup.wm_attributes("-topmost", 1)
        self.examine_header = Label(self.popup, text = "Examining Run")
        self.examine_header.grid(row = 0, column = 0)
        self.examine_info = Label(self.popup, wraplength = 1000, justify = LEFT,
                                  text = (f"Category: {self.full_category}\n" +
                                          f"Players: {self.players_comma}\n" +
                                          (f"RTA: {self.real_time}\n" if 'realtime'
                                           in game_obj['ruleset']['run-times'] else '') +
                                          (f"RTA without loads: {self.noloads_time}\n" if 'realtime_noloads'
                                           in game_obj['ruleset']['run-times'] else '') +
                                          (f"IGT: {self.ingame_time}\n" if 'ingame'
                                           in game_obj['ruleset']['run-times'] else '') +
                                          f"{self.var_string}\n" +
                                          f"Description:\n{self.description}"))
        self.examine_info.grid(row = 1, column = 0)
        self.examine_buttons = Frame(self.popup)
        self.verify_button = Button(self.examine_buttons, text = "Verify run",
                                    bg = 'SpringGreen3', command = self.verify)
        self.verify_button.grid(row = 0, column = 0)
        self.reject_button = Button(self.examine_buttons, text = "Reject run",
                                    bg = 'IndianRed1', command = self.reject)
        self.reject_button.grid(row = 0, column = 1)
        self.reason_entry = Text(self.examine_buttons, width = 50, height = 3)
        self.reason_entry.grid(row = 1, columnspan = 2)
        self.examine_buttons.grid(row = 2, column = 0)

def refresh_queue():
    for widget in queue_display.winfo_children():
        widget.destroy()
    for run in queue_pages[queue_offset]:
        run.display()
    queue_display.grid(row = 1, column = 0)
    back_button.configure(state = (DISABLED if queue_offset == 0 else ACTIVE))
    next_button.configure(state = (DISABLED if queue_offset == len(queue_pages) - 1 else ACTIVE))
    pagination.configure(text = f"Page {queue_offset + 1} of {len(queue_pages)}")

def back_switch():
    global queue_offset
    queue_offset -= 1
    refresh_queue()

def next_switch():
    global queue_offset
    queue_offset += 1
    refresh_queue()

def edit_working_queue():
    global queue_offset, queue_pages, working_queue
    if cat_select.get() == "All Categories":
        working_queue = queue
    else:
        working_queue = [run for run in queue if run.full_category == cat_select.get()]
    queue_pages = []
    hold = []
    counter = 0
    for run in working_queue:
        if counter + len(run.players) > OFFSET_LIMIT:
            queue_pages.append(hold)
            hold = [run]
            counter = len(run.players)
        else:
            hold.append(run)
            counter += len(run.players)
    queue_pages.append(hold)
    queue_offset = 0
    refresh_queue()

def open_verifclient():
    import verifclient
    client = verifclient.VerifClient(log)

game_obj = json_from_src(f"games/{game_str}")['data']
GAME = game_obj['id']

beta_queue = sorted(get_queue(GAME),
                    key = lambda run: ((run['date'] if sort_by_date else 1),
                                       run['submitted']))
queue = [Run(run) for run in beta_queue]
working_queue = queue
cat_map = {cat['id']: cat['name'] for cat in json_from_src(f"games/{GAME}/categories")['data']}
level_map = {level['id']: level['name'] for level in json_from_src(f"games/{GAME}/levels")['data']}
variables = json_from_src(f"games/{GAME}/variables")['data']
subcat_map = {}
for subcat in [var for var in variables if var['is-subcategory']]:
    subcat_map.update({val: subcat['values']['values'][val]['label'] for val in subcat['values']['values']})
var_map = {}
for var in variables:
    var_map.update({var['id']: var['name']})
    var_map.update({val: var['values']['values'][val]['label'] for val in var['values']['values']})

window = Tk()
window.title("QueueClient v1.1.1")

if stay_on_top:
    window.wm_attributes("-topmost", 1)

Label(window, text = "Queue").grid(row = 0, column = 0)
queue_display = Frame(window, height = 525, width = 750)
queue_display.grid_propagate(0)
queue_display.grid_columnconfigure(0, weight = 1)
queue_display.grid_columnconfigure(7, weight = 1)

Label(window, text = "Utilities").grid(row = 0, column = 1)
utilities = Frame(window)
console = st.ScrolledText(utilities, width = 50, height = 10)
console.insert(INSERT, f"Initiated at {datetime.datetime.now().isoformat()}")
console.configure(state = DISABLED)
console.grid(row = 0, column = 0)

Label(utilities).grid(row = 1, column = 0)

queue_buttons = Frame(utilities)
back_button = Button(queue_buttons, text = "Back", command = back_switch)
back_button.grid(row = 0, column = 0)
next_button = Button(queue_buttons, text = "Next", command = next_switch)
next_button.grid(row = 0, column = 1)
queue_buttons.grid(row = 2, column = 0)
pagination = Label(utilities, height = 2)
pagination.grid(row = 3, column = 0)

cat_filter = Frame(utilities)
all_cats = ["All Categories"] + sorted(list({run.full_category for run in queue}))
cat_select = StringVar()
cat_select.set("All Categories")
cat_menu = OptionMenu(cat_filter, cat_select, *all_cats)
cat_menu.grid(row = 0, column = 0)
filter_button = Button(cat_filter, text = "Apply", command = edit_working_queue)
filter_button.grid(row = 0, column = 1)
cat_filter.grid(row = 4, column = 0)

Label(utilities).grid(row = 5, column = 0)

verifclient_button = Button(utilities, text = "Open VerifClient", command = open_verifclient)
verifclient_button.grid(row = 6, column = 0)

utilities.grid(row = 1, column = 1, sticky = N)

edit_working_queue()

window.mainloop()
