#!/usr/bin/env python
import os
import pyperclip
from subprocess import Popen
from collections import Counter
from tkinter import *
from tkinter import ttk

'''
    NOTE: this program only works in arch linux based systems(using pacman package manager).
    This program makes use of python tkinter to display package and its information in a 
    treeview seperately for officail and aur repos.also highlights explicitly installed/orphaned packages

    The search query is directly fed to pacman command and the result is piped back, instead of
    actually fetching from the servers. simply it runs pacman command and shows the output in a treeview

    This program is inefficient and poorly implemented as it was made in a hurry :)
    i'll fix it sometime later
'''

packages = {
            'official'           : {},
            'aur'                : {},
            'installed'          : (),
            'installed_aur'      : (),
            'installed_official' : (),
            'orphaned'           : {},
            }

def show_installed_packages_all():
    terminal_command = ('pacman -Qqe')
    result_set = os.popen(terminal_command).read().split('\n')
    packages['installed'] = tuple(result_set)

def show_installed_packages_official():
    #we only need explicitly installed ones ,so not using -Qn
    show_installed_packages_aur()
    show_installed_packages_all()
    result_set = list((Counter(packages['installed']) - Counter(packages['installed_aur'])).elements())
    packages['installed_official'] = tuple(result_set)

def show_installed_packages_aur():
    terminal_command = ('pacman -Qqm')
    result_set = os.popen(terminal_command).read().split('\n')
    packages['installed_aur'] = tuple(result_set)

def search_for_package_both(package_name):
    search_for_package(package_name,'official')
    search_for_package(package_name,'aur')

def search_for_package(package_name,package_repo):
    show_installed_packages_all() # checking if package is already installed
    if package_repo == 'both':
        search_for_package_both(package_name)
        return
    if package_repo == 'official':
        package_manager = 'pacman'
    if package_repo == 'aur':
        package_manager = 'yay'
    terminal_out = os.popen(package_manager + ' -Ss ' + package_name).readlines()
    for i in range(0,len(terminal_out),2):
        formatted_string = terminal_out[i].strip('\n')[terminal_out[i].find('/')+1: terminal_out[i].find(' ')]
        desc = (terminal_out[i+1].strip('\n')).lstrip()
        packages[package_repo][formatted_string] = desc
        if '(Orphaned)' in terminal_out[i]:
            packages['orphaned'][formatted_string] = desc

def filter_from_aur():
    if len(packages['official']) == 0:
        print('returning')
        return
    if len(packages['aur']) == 0:
        print('returning')
        return
    official_set = set(packages['official'])
    aur_set = set(packages['aur'])
    for name in official_set.intersection(aur_set):
        del packages['aur'][name]

def call_search_for_package():
    s = SEARCH.get()
    if s == '' or  s == len(s) * s[0]:
        return
    if REPO.get() == '1':
        repo = 'official'
    elif REPO.get() == '2':
        repo = 'aur'
    elif REPO.get() == '3':
        repo = 'both'
    reset_treeview()
    search_for_package(SEARCH.get(),repo)
    filter_from_aur()
    insert_to_treeview(repo)

def get_package_info(package_name):
    terminal_command = ('pacman -Si '+package_name)
    terminal_out = os.popen(terminal_command).readlines()
    if terminal_out == []:
        #print('This will take a second')
        terminal_command = ('yay -Si '+package_name)
        terminal_out = os.popen(terminal_command).readlines()
        #fixme somehow
        if len(terminal_out) < 2:
            print('[ERROR]-----------[PACKAGE NOT FOUND]')
            return 0 # might need to return something incase of error JIC
    result_set = []
    for i in terminal_out:
        for data in ['Repository','Version','Description','URL','Download','Installed']:
            if i.startswith(data):
                result_set.append(i.replace('\n',''))
    update_labels(result_set)

def on_repo_selected():
    search_button.config(state='active')
    find_in_search_button.configure(state='active')

def insert_to_treeview(repo):
    if repo == 'both':
        insert_to_treeview_both()
        return
    for i in packages[repo]:
        if i in packages['installed']:
            tree_dict[repo].insert('', 'end', values=(i,packages[repo][i]), tags = ('installed_style',))
            continue
        if i in packages['orphaned']:
            tree_dict[repo].insert('', 'end', values=(i,packages[repo][i]), tags = ('orphaned_style',))
            continue
        tree_dict[repo].insert('', 'end', values=(i,packages[repo][i]))

def insert_to_treeview_both():
    for i in packages['official']:
        if i in packages['installed']:
            tree_dict['official'].insert('', 'end', values=(i,packages['official'][i]), tags = ('installed_style',))
            continue
        if i in packages['orphaned']:
            tree_dict['official'].insert('', 'end', values=(i,packages['official'][i]), tags = ('orphaned_style',))
            continue
        tree_dict['official'].insert('', 'end', values=(i,packages['official'][i]))

    for i in packages['aur']:
        if i in packages['installed']:
            tree_dict['aur'].insert('', 'end', values=(i,packages['aur'][i]), tags = ('installed_style',))
            continue
        if i in packages['orphaned']:
            tree_dict['aur'].insert('', 'end', values=(i,packages['aur'][i]), tags = ('orphaned_style',))
            continue
        tree_dict['aur'].insert('', 'end', values=(i,packages['aur'][i]))

def reset_treeview():
    global packages
    packages = {
            'official'           : {},
            'aur'                : {},
            'installed'          : (),
            'installed_aur'      : (),
            'installed_official' : (),
            'orphaned'           : {},
            }
    for item in left_treeview.get_children():
        left_treeview.delete(item)
    for item in right_treeview.get_children():
        right_treeview.delete(item)

    REPO_NAME.set('')
    VERSION.set('')
    DESCRIPTION.set('')
    URL.set('')
    DOWNLOAD.set('')

def on_selection_left(event=None):
    try:
        current_item = left_treeview.focus()
        contents = (left_treeview.item(current_item))
        get_package_info(contents['values'][0])
    except:
        pass

def on_selection_right(event=None):
    try:
        current_item = right_treeview.focus()
        contents = (right_treeview.item(current_item))
        get_package_info(contents['values'][0])
    except:
        pass

def update_labels(values):
    info = []
    DOWNLOAD.set('')
    INSTALLED_SIZE.set('')

    for i in values:
        info.append(i[i.find(': ')+2:])
    REPO_NAME.set(info[0].upper())
    VERSION.set(info[1])
    DESCRIPTION.set(info[2])
    URL.set(info[3])

    DOWNLOAD.set(info[4])
    INSTALLED_SIZE.set(info[5])

def find():
    query = FIND.get()
    if query in ['',' ']:
        return
    left_selections = []
    right_selections = []
    for child in left_treeview.get_children():
        if query.lower() in str(left_treeview.item(child)['values']).lower():
            left_selections.append(child)
    left_treeview.selection_set(left_selections)

    for child in right_treeview.get_children():
        if query.lower() in str(right_treeview.item(child)['values']).lower():
            right_selections.append(child)
    right_treeview.selection_set(right_selections)

def copy_from_left():
    if left_treeview.selection() == ():
        return
    copy_list = []
    for i in left_treeview.selection():
        copy_list.append(left_treeview.item(i)['values'][0])
    pyperclip.copy('sudo pacman -S '+' '.join(copy_list))

def copy_from_right():
    if right_treeview.selection() == ():
        return
    copy_list = []
    for i in right_treeview.selection():
        copy_list.append(right_treeview.item(i)['values'][0])
    pyperclip.copy('yay -S '+' '.join(copy_list))

def remove_selections_on_hover(event=None):
    for tree in tree_dict.values():
        for item in tree.selection():
            tree.selection_remove(item)

root = Tk()
root.geometry('1217x632')
root.config(background="#3F3F3F")
root.resizable(1, 1)
#root.overrideredirect(1)
root.config(padx=1, pady=1)
root.columnconfigure(0, weight=1)

SEARCH = StringVar()
REPO = StringVar()
REPO_NAME = StringVar()
URL = StringVar()
VERSION = StringVar()
DOWNLOAD = StringVar()
INSTALLED_SIZE = StringVar()
DESCRIPTION = StringVar()
FIND = StringVar()

style = ttk.Style(root)
style.theme_use('clam')
ttk.Style().configure("Treeview", background="#383838", foreground="white", fieldbackground="#3f3f3f")


left_frame = Frame(root , relief='solid', borderwidth=1)
left_frame.grid(row=0, column=0, sticky='nsew', padx=1, pady=1)

middle_frame = Frame(root , relief='solid', borderwidth=1)
middle_frame.grid(row=0, column=1, sticky='nsew', padx=1, pady=1)

right_frame = Frame(root , relief='solid', borderwidth=1)
right_frame.grid(row=0, column=2, sticky='nsew', padx=1, pady=1)

# LEFT TREE VIEW
left_scroll_y = Scrollbar(left_frame, orient=VERTICAL)
left_scroll_y.grid(row=0, column=1, sticky='nsew')
left_scroll_x = Scrollbar(left_frame, orient=HORIZONTAL)
left_scroll_x.grid(row=1, column=0, sticky='nsew')
left_treeview = ttk.Treeview(left_frame, columns=('package', 'description'), selectmode="extended",yscrollcommand=left_scroll_y.set, xscrollcommand=left_scroll_x.set,height=22)
left_scroll_y.config(command=left_treeview.yview)
left_scroll_x.config(command=left_treeview.xview)
left_treeview.grid(row=0, column=0, sticky='nsew')
left_treeview.heading('package', text='PACKAGE', anchor=W)
left_treeview.heading('description', text='DESCRIPTION', anchor=W)
left_treeview.column('#0', stretch=NO, minwidth=0, width=0)
left_treeview.column('#1', stretch=NO, minwidth=100, width=150)
left_treeview.column('#2', stretch=NO, minwidth=300, width = 350)
left_treeview.bind("<<TreeviewSelect>>",on_selection_left)
left_treeview.bind('<Enter>', remove_selections_on_hover)


# RIGHT TREE VIEW
right_scroll_y = Scrollbar(right_frame, orient=VERTICAL)
right_scroll_y.grid(row=0, column=1, sticky='nsew')
right_scroll_x = Scrollbar(right_frame, orient=HORIZONTAL)
right_scroll_x.grid(row=1, column=0, sticky='nsew')
right_treeview = ttk.Treeview(right_frame, columns=('package', 'description'), selectmode="extended",yscrollcommand=right_scroll_y.set, xscrollcommand=right_scroll_x.set,height=22)
right_scroll_y.config(command=right_treeview.yview)
right_scroll_x.config(command=right_treeview.xview)
right_treeview.grid(row=0, column=0, sticky='nsew')
right_treeview.heading('package', text='PACKAGE', anchor=W)
right_treeview.heading('description', text='DESCRIPTION', anchor=W)
right_treeview.column('#0', stretch=NO, minwidth=0, width=0)
right_treeview.column('#1', stretch=NO, minwidth=100, width=150)
right_treeview.column('#2', stretch=NO, minwidth=300, width = 350)
right_treeview.bind("<<TreeviewSelect>>",on_selection_right)
right_treeview.bind('<Enter>', remove_selections_on_hover)


tree_dict = {'official' : left_treeview,
             'aur': right_treeview}

right_treeview.tag_configure('installed_style', background='#a3b86c')
left_treeview.tag_configure('installed_style', background='#a3b86c')
left_treeview.tag_configure('orphaned_style', background='#cd594a')
right_treeview.tag_configure('orphaned_style', background='#cd594a')

# MIDDLE FRAME BUTTONS
search_field = Entry(middle_frame, textvariable=SEARCH, relief='solid', width=20)
search_field.grid(row=0, column=0, sticky='nsew')

Radiobutton(middle_frame, text="OFFICIAL", variable=REPO, value=1, command=on_repo_selected).grid(row=1, column=0, sticky='nsew')
Radiobutton(middle_frame, text="AUR       ", variable=REPO, value=2, command=on_repo_selected).grid(row=2, column=0, sticky='nsew')
Radiobutton(middle_frame, text="BOTH      ", variable=REPO, value=3, command=on_repo_selected).grid(row=3, column=0, sticky='nsew')

search_button = Button(middle_frame, text='SEARCH', relief='solid', state='disabled', command=call_search_for_package)
search_button.grid(row=4, column=0, sticky='nsew')

clear_button = Button(middle_frame, text='CLEAR' , relief='solid', command=reset_treeview)
clear_button.grid(row=5, column=0, sticky='nsew')

repo_label = Label(root, relief='solid', textvariable=REPO_NAME, bg='#383838', fg='#ff0000')
repo_label.grid(row=1, column=0, sticky='nsew', pady=(6,2), padx=2, columnspan=3)

version_label = Label(root, relief='solid', textvariable=VERSION, bg='#383838', fg='#28E70D')
version_label.grid(row=2, column=0, sticky='nsew', pady=2, padx=2, columnspan=3)

desc_label = Label(root, relief='solid', textvariable=DESCRIPTION, bg='#383838', fg='#ffff00')
desc_label.grid(row=3, column=0, sticky='nsew', pady=2, padx=2, columnspan=3)

url_label = Label(root, relief='solid', textvariable=URL, bg='#383838', fg='#0affff')
url_label.grid(row=4, column=0, sticky='nsew', pady=2, padx=2, columnspan=3)

download_label = Label(root, relief='solid', textvariable=DOWNLOAD, bg='#383838', fg='#F6DD13')
download_label.grid(row=5, column=0, sticky='nsew', pady=2, padx=2, columnspan=3)

installed_size_label = Label(root, relief='solid', textvariable=INSTALLED_SIZE, bg='#383838', fg='#F6DD13')
installed_size_label.grid(row=6, column=0, sticky='nsew', pady=2, padx=2, columnspan=3)

exit_button = Button(middle_frame, text='EXIT', relief='solid', command=exit)
exit_button.grid(row=7, column=0, sticky='nsew', pady=2, padx=2)

find_in_search_entry = Entry(middle_frame, textvariable=FIND, relief='solid', width=20)
find_in_search_entry.grid(row=8, column=0, sticky='nsew', pady=(8,2), padx=2)

find_in_search_button = Button(middle_frame, text='FIND', state='disabled', relief='solid', command=find)
find_in_search_button.grid(row=9, column=0, sticky='nsew', padx=2)

copy_left_button = Button(middle_frame, text='-->> COPY', relief='solid', command=copy_from_left)
copy_left_button.grid(row=11, column=0, sticky='nsew', padx=2)

copy_right_button = Button(middle_frame, text='COPY <<--', relief='solid', command=copy_from_right)
copy_right_button.grid(row=12, column=0, sticky='nsew', padx=2)

root.mainloop()
