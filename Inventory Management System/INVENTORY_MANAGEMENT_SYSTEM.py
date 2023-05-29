# CS_PROJECT - INVENTORY MANAGEMENT SYSTEM(GUI) 
# TODO: implement using sqlite
''' 
    This was my grade 12 cs project :)
    This project combines MySQL and python's Tkinter GUI framework to create a simple,robust interface to manage an inventory system
    This program contains various features including Insertion,Updation,Deletion,Sorting along with some extra features which enables 
    the user to Import table to a CSV file, Export to a CSV file, Prepare a project report, etc..
    This project requires mysql.connector,tabulate and ttk module to be installed 
'''

'''
    Various style settings of tkinter framework varies heavily depending on the OS, therfore the window might show up with the wrong padding,
    alignment and sizes.===THIS PROGRAM WAS WRITTEN IN A WINDOWS10 SYSTEM AND LOOKS BEST ON A WINDOWS itself===. Padding and alignment are
    slightly different in unix systems.
'''

from tkinter import *
from tkinter.font import BOLD,ITALIC
import mysql.connector
import tkinter.ttk as ttk
import tkinter.messagebox as messagebox
import csv
import datetime
import tabulate
import pickle
import os
import re
import getpass

''' troubleshoot : sha2_password method is not supported.It is the recommended settings in mysql server 8.x .
    Please use legacy authentication method.
    the files will be created in the program directory
    The window theme and padding might vary with OSs as with their WMs.
    The password and username for mysql are stored in `.auth_info.dat` file
'''

#Checking credentials and trying to login
print('\n================================================\nMySQL login\n---------------')
try:
    with open('.auth_info.dat', 'rb') as file:
        auth = pickle.load(file)
        mysql_user = auth[0]
        mysql_password = auth[1]
        print('Trying with any previously entered credentials ...')
except:
    messagebox.showwarning('No credentials', 'Please enter your MySQL credentials at the working console')
    mysql_user = input('Enter mysql username : ')
    mysql_password = getpass.getpass('Enter the password to the user : ')
    with open('.auth_info.dat', 'wb+') as file:
        pickle.dump([mysql_user, mysql_password], file)

#Trying to Establish a connection between mysql and python 
#A single 'connection' handle and 'cursor' object is used throughout the program. and is terminated upon exit
#Possible errors are caught

try:
    connection = mysql.connector.connect(host='localhost', user=mysql_user, password=mysql_password)
    connection.autocommit = True
except (mysql.connector.errors.ProgrammingError, mysql.connector.errors.DatabaseError) as e:
    os.remove('.auth_info.dat')
    print('\n[ERROR]Could not establish a connection between python and mysql.Exiting ...\n\n'
            'Possible Causes:\n'
            '\t> Seems like there is an error with the username and password,please recheck.\n'
            '\t> The given username might not have the permissions required.\n'
            '\t> sha2_password is not supported, please use legacy authentication method.\n'
            '\t> check whether mysql service is started and running')
    exit()

except mysql.connector.errors.InterfaceError:
    print('\t> Seems like mysql service is not started on your system.please start the mysql service to establish a connection.Exiting ...')
    exit()
cursor = connection.cursor()
cursor.execute("CREATE DATABASE IF NOT EXISTS inv_db;")
cursor.execute("USE inv_db")


print('Login Successful')
cursor.execute("CREATE TABLE IF NOT EXISTS `product` (product_id varchar(15) PRIMARY KEY NOT NULL, product_name varchar(20), product_qty int(10), product_price double(10,2), date_added varchar(10))")
print('creating database and table incase they do not exist ...')

sql_fields = ['product_id', 'product_name', 'product_qty', 'product_price', 'date_added']


#function defenitions

def get_inventory_worth():
    #returns the overall worth of inventory
    cursor.execute('SELECT SUM(product_qty*product_price) from product')
    inventory_worth = cursor.fetchone()[0]
    return inventory_worth


def generate_report(event=None):
    #generate an inventory report. user can choose to either append/overwrite to an existing report
    #pro
    result = messagebox.askquestion('Generate report', "Would you like to generate a report based on this inventory?\nThe report will be made in the program directory")
    if result == 'yes':
        cursor.execute('SELECT * FROM product')
        product_data = cursor.fetchall()
        table = []
        inventory_worth = get_inventory_worth()
        #A new field 'Product_price' is provided in the report for easiness
        for i in product_data:  
            table.append(list(i))
        for i in table: 
            i.insert(4, i[2]*i[3])
        
        write_mode = 'w+'
        append = messagebox.askyesno('Choose write mode', 'Do you want to append new report to any previously existing report?\nOtherwise, will be overwritten')
        if append == 1:
            write_mode = 'a+'
        with open('inventory_report.txt', write_mode) as report:
            reset()
            report.write('==========================    INVENTORY REPORT    ===========================\n')
            report.write('-----------------    [report created on ' + (datetime.datetime.now()).strftime("%d/%m/%Y %H:%M:%S") + ']    ----------------\n\n')
            report.write('INVENTORY                                                     TOTAL ENTRIES = ' + str(get_total_entries()) + '\n')
            report.write(tabulate.tabulate(table, ('PRODUCT_ID', 'PRODUCT_NAME', 'QUANTITY', 'UNIT PRICE', 'TOTAL PRICE', 'DATE_ADDED'), tablefmt="pretty"))
            report.write('\nINVENTORY WORTH = ' + str(inventory_worth))
            report.write('\n\n\n')
        info_label.config(text='Inventory report generated!', foreground=green)


def destroy_root_window(event=None):  # this function prompts the user to exit the program
    #Destroys rootwindow, closes connection and exits the program after a prompt
    result = messagebox.askquestion('', 'Are you sure you want to exit?')
    if result == 'yes':
        inventory_window.destroy()
        print('Exiting ...')
        cursor.close()
        connection.close()
        exit()


#TODO: sorting could be easier with identify_column
def sort(column_heading):
    #sort the inventory as needed 
    #the user can click on corresponding column heading to sort accordingly
    #sorting is performed as an sql query and the fetched data is displayed in the tree
    #reset the treeview before sorting
    reset()
    if ORDER.get() == 'ASC':
        ORDER.set('DESC')
        order_ind = '▼'
    else:
        ORDER.set('ASC')
        order_ind = '▲'
    #we need these lists to match between headings,text on headings, and actual sql fields
    heading_text_list = ['PRODUCT ID', 'PRODUCT', 'QUANTITY', 'UNIT PRICE', 'DATE ADDED']
    heading_list = ['P_ID', 'Product', 'Quantity', 'Price', 'Date']  

    h_text=heading_text_list[heading_list.index(column_heading)]
    #update the clicked heading with an indicator
    tree_view_widget.heading(column_heading, text=(h_text+' '+order_ind))
    #sql field names for corresponding treeview headings
    #the corresponding field name for the DATE element is replaced with a command
    # STR_TO_DATE(date_added, '%d-%m-%Y')
    #this is to get date in 'DD-MM-YYYY' format. 
    value = sql_fields[heading_list.index(column_heading)]

    cursor.execute('SELECT * FROM product ORDER BY ' + value + ' ' + ORDER.get())
    #clearing the treeview to replace it with sorted data
    tree_view_widget.delete(*tree_view_widget.get_children())
    treeview_insert(cursor.fetchall())


#insert fetched values into treeview
#the fetched data is numbered
def treeview_insert(cursor_fetch):
    for row_index in range(len(cursor_fetch)):
        numbered = list(cursor_fetch[row_index])
        numbered.insert(0,row_index+1)
        tree_view_widget.insert('', 'end', values=numbered)


def fetch_table():
    #this is the default view of the inventory(same as in the table)
    cursor.execute("SELECT * FROM product")
    treeview_insert(cursor.fetchall())


def get_cur_date():
    #returns the current date in 'DD-MM-YYYY'
    return(datetime.date.strftime(datetime.date.today(), "%d-%m-%Y"))


def insert_new():
    #insert a new row to the table   
    #check if entered values in entry fields are permitted
    if validate() == 1:
        try:
            cursor.execute("INSERT INTO `product` (product_id, product_name, product_qty, product_price, date_added) VALUES(%s, %s, %s, %s, %s)",
                           (PRODUCT_ID.get(), PRODUCT_NAME.get(), int(PRODUCT_QUANTITY.get()), float(PRODUCT_PRICE.get()), DATE.get()))
        #primary key must be unique
        except mysql.connector.errors.IntegrityError:
            messagebox.showwarning('Error', 'PRODUCT_ID must be unique.')

        #clear table and fetch data
        tree_view_widget.delete(*tree_view_widget.get_children())
        fetch_table()
        info_label.config(text='TOTAL NO: OF ITEMS : ' + str(get_total_entries()) + "\t\tINVENTORY WORTH : " + str(get_inventory_worth()), foreground=light3)


def export_to_csv():
    #export the table into a CSV file(inventory_data.csv) in the working directory
    cursor.execute('SELECT * FROM product')
    product_data = cursor.fetchall()
    result = messagebox.askquestion('Proceed?', 'This action will overwrite if inventory_data.csv exists from a previous backup.\n'
                                                'make a copy of previous backup if needed.\n'
                                                'Confirm to export ??')
    if result == 'no':
        return
    with open('inventory_data.csv', 'w+', newline='') as file:
        writer = csv.writer(file, delimiter=',')
        writer.writerow(['PRODUCT_ID', 'PRODUCT_NAME', 'PRODUCT_QTY', 'UNIT_PRICE', 'DATE'])
        writer.writerows(product_data)
        info_label.config(text='Exported to csv', foreground=green)


def import_from_csv():
    #import data from a CSV file(inventory_data.csv) in the working directory
    cursor.execute("SELECT count(*) FROM product")
    count = cursor.fetchone()
    if count == (0,):
        try:
        #for each row in the file, set corresponding values to the entries, then call insert_new()        
            with open('inventory_data.csv', 'r', newline='') as file:
                reader = csv.reader(file)
                for row in reader:
                    if row[0] == 'PRODUCT_ID':
                        continue
                    PRODUCT_ID.set(row[0])
                    PRODUCT_NAME.set(row[1])
                    PRODUCT_QUANTITY.set(row[2])
                    PRODUCT_PRICE.set(row[3])
                    DATE.set(row[4])
                    insert_new()
                    
            messagebox.showwarning('','Import Complete!\nOnly properly delemited rows are imported')
        except FileNotFoundError:
            result = messagebox.showinfo('File not found', "No previously exported csv backup found.\n"
            "Additionally,You can make use of any spreadsheet program to make 'inventory_data.csv'\n"
            "and place it in the program's directory inorder to import it if needed.")
            #NOTE: only properly delemited rows are imported. no spaces allowed between comma
        #reset the view    
        reset()
    else:
        info_label.config(text='csv can only be imported to empty table', foreground=red)
    

def delete_all():
    #delete all rows from the table
    result = messagebox.askquestion('Are you sure?', 'This action will delete all data in the table. \nproceed?')
    if result == 'yes':
        cursor.execute('DELETE FROM product')
        reset()


def get_cell(event):
    try:
        column = int(tree_view_widget.identify_column(event.x)[1])
        row = tree_view_widget.identify_row(event.y)
        region = tree_view_widget.identify_region(event.x, event.y)
    except:
        return
    if region == 'heading':
        if column < 2:
            sub_label.config(text='inv_db : product', foreground=blue)
            return
        field_name = sql_fields[column-2]
        sub_label.config(text='SQL field name : '+field_name, foreground=blue)
    else:
        sub_label.config(text='')


def get_data(event):
    selected_item = tree_view_widget.focus()
    contents = (tree_view_widget.item(selected_item))
    #set entry widgets with corresponding values when a row is clicked
    try:
        PRODUCT_ID.set(contents['values'][1])
        PRODUCT_NAME.set(contents['values'][2])
        PRODUCT_QUANTITY.set(contents['values'][3])
        PRODUCT_PRICE.set(contents['values'][4])
        DATE.set(contents['values'][5])
        product_total_label.config(text='TOTAL PRICE = ' + str(float(PRODUCT_QUANTITY.get()) * float(PRODUCT_PRICE.get())), foreground=dark0)
    except IndexError:
        return


def update_data():
    #update any row of the table
    if tree_view_widget.selection() == ():
        return
    #entries are validated before querying
    if validate() == 1:
        cursor.execute("UPDATE product SET product_id = '" + PRODUCT_ID.get() + "',product_name = '" + PRODUCT_NAME.get() + "', product_qty = '" +
                       PRODUCT_QUANTITY.get() + "', product_price = '" + PRODUCT_PRICE.get() + "', date_added = '" + DATE.get() + "' WHERE product_id = '" + PRODUCT_ID.get() + "'")
        reset()


def validate():
    #this function checks whether the entered values are permissible
    #if it passes all tests, returns 1 
    if '' in (PRODUCT_ID.get(),PRODUCT_NAME.get(),PRODUCT_PRICE.get(),PRODUCT_QUANTITY.get()):
        info_label.config(text='please enter the details', foreground=red)
        return
    if PRODUCT_ID.get().isalnum() == 0:
        info_label.config(text='Enter an alphanumeric, unique product ID', foreground=red)
        return
    if re.match(r'^\w+$', PRODUCT_NAME.get()) == None:
        info_label.config(text='Proceed with a valid Product name', foreground=red)
        return
    if (PRODUCT_QUANTITY.get().isdigit() == 0) or (int(PRODUCT_QUANTITY.get()) < 1):
        info_label.config(text='Enter a valid quantity', foreground=red)
        return
    if PRODUCT_PRICE.get().replace('.','').isdigit() == 0:
        info_label.config(text='Price must be a number', foreground=red)
        return
    if DATE.get() == '':
        info_label.config(text="Today's date will be entered", foreground=green)
        #if date is not provided, current date is automatically used
        DATE.set(get_cur_date())
        return
    elif len(DATE.get()) != 10:
        info_label.config(text='Enter date in DD-MM-YYYY format', foreground=red)
        return
    try:
        a = DATE.get().split('-')
        datetime.date(day=int(a[0]), month=int(a[1]), year=int(a[2]))
    except ValueError:
        info_label.config(text='Please enter a valid Date (DD-MM-YYYY)', foreground=red)
        return 

    return 1


def reset():
    #resets the treeview, clears labels,entries and other widgets
    tree_view_widget.delete(*tree_view_widget.get_children())
    fetch_table()
    SEARCH.set('')
    PRODUCT_ID.set('')
    PRODUCT_NAME.set('')
    PRODUCT_QUANTITY.set('')
    PRODUCT_PRICE.set('')
    DATE.set('')
    
    get_inventory_worth()

    info_label.config(text='TOTAL NO: OF ITEMS : ' + str(get_total_entries()) + "\t\tINVENTORY WORTH : " + str(get_inventory_worth()), foreground=light3)
    sub_label.config(text='')
    product_total_label.config(text='')
    #restore default heading
    tree_view_widget.heading('#0', text="S.No")
    tree_view_widget.heading('P_ID', text="PRODUCT ID")
    tree_view_widget.heading('Product', text="PRODUCT")
    tree_view_widget.heading('Quantity', text="QUANTITY")
    tree_view_widget.heading('Price', text="UNIT PRICE")
    tree_view_widget.heading('Date', text="DATE ADDED")
    #restore default column widths
    tree_view_widget.column('#1',width=60)
    tree_view_widget.column('#2',width=60)
    tree_view_widget.column('#3',width=60)
    tree_view_widget.column('#4',width=60) 
    tree_view_widget.column('#5',width=60)
    tree_view_widget.column('#6',width=60)


def delete_record():
    #delete a record from the table
    if PRODUCT_ID.get() == '':
        pass
    else:
        get_data(event=None)
        cursor.execute("DELETE FROM product WHERE product_id = '" + PRODUCT_ID.get() + "'")
        reset()


def search_record():
    #search for a string in the whole table
    #matches with all columns 
    if SEARCH.get() == '':
        return
    else:
        s = "'%" + SEARCH.get() + "%'"
        cursor.execute("SELECT * FROM product WHERE product_name LIKE" + s + "OR product_id LIKE " + s + "OR product_qty LIKE " + s +
                       "OR product_price LIKE " + s + "OR date_added LIKE " + s)
        tree_view_widget.delete(*tree_view_widget.get_children())
        treeview_insert(cursor.fetchall())


def get_total_entries():
    #return the total number of records
    cursor.execute('SELECT COUNT(*) FROM product')
    total_entries = ((cursor.fetchone())[0]) 
    return total_entries


def run_custom_query(event=None):
    query = CUSTOM_QUERY.get()
    if query == '':
        return
    print('\n================OUTPUT================')
    print(query.upper())
    try:
        cursor.execute(query)
    except mysql.connector.errors.DatabaseError:
        print(':( An error\nCheck the syntax and try again')
        custom_query_entry.config(foreground=red, highlightcolor=red)
        # CUSTOM_QUERY.set('')
        return
    custom_query_entry.config(foreground=green, highlightcolor=green)
    #we need to quickly assign the column names before any other query is executed
    headings = cursor.column_names
    output = cursor.fetchall()
    # reset()
    print(tabulate.tabulate(output,headings, tablefmt="pretty"))
    

def escape_click(event):
    if tree_view_widget.identify_region(event.x, event.y) == "separator":
        return "break"


#create the root window
inventory_window = Tk()
inventory_window.title("INVENTORY MANAGEMENT SYSTEM")

#color palette
dark0= '#002b36'
dark1= '#073642'
light3= '#cdedf8'
light2= '#aac9d4'
light1=  '#abb9bb'
light0=  '#93a1a1'
red=    '#E64141'
blue =   '#268bd2'
green=  '#8AFF96'

inventory_window.config(background=dark0)
inventory_window.geometry('645x400')
#comment this line to resize the window
inventory_window.resizable(0, 0)
inventory_window.attributes('-topmost',True)



#NOTE: for some reason style config is not working for some widgets
style = ttk.Style()
style.theme_use('alt') #use alt theme for better compatibility
style.configure('TButton',background=light0,relief=NONE, shiftrelief=SOLID, foreground=dark1, font=('consolas',9, BOLD))
style.configure("Treeview.Heading", background=light0, foreground=dark0, font=('consolas',10,BOLD), relief=NONE, padding=5) 
style.configure("Treeview", background=light3, fieldbackground=light2)
style.configure('TLabel',background=light0, anchor=CENTER, relief=NONE ,foreground=dark1, font=('consolas',10, BOLD,ITALIC))
style.configure('TScrollbar', troughcolor=dark1, background=light0, arrowcolor=dark0, bordercolor=dark1)
style.map("TScrollbar", background=[('active',light0)])
style.map("TButton", background=[('active',light1)], relief=[('active',FLAT)])
style.map("Treeview.Heading", background =[('active',light3)])
style.map("Treeview",foreground=[('selected', dark0)],background=[('focus','#88bef5')],font=[('focus',('consolas',10,BOLD))])
#these variables are binded to various entries and can be globally accessed
#TODO: Use IntVar() for qty and price
PRODUCT_ID = StringVar()
PRODUCT_NAME = StringVar()
PRODUCT_QUANTITY = StringVar()
PRODUCT_PRICE = StringVar()
DATE = StringVar()

SEARCH = StringVar()
CUSTOM_QUERY = StringVar()
ORDER = StringVar()

#clear sub_label when mouse pointer is out of inventory_window
inventory_window.bind('<Leave>', lambda event=None: sub_label.config(text=''))

#a container for buttons
action_frame = Frame(inventory_window)
action_frame.config(background=dark0)
action_frame.pack(fill=X)

#a container for entries
data_display_frame = Frame(inventory_window)
data_display_frame.pack(padx=(2,2), pady=(3, 0))
data_display_frame.config(background=red)
# data_display_frame.bind('<Enter>', lambda event=None: sub_label.config(text=''))

#display some useful info at the bottom
info_label = ttk.Label(inventory_window, text='TOTAL NO: OF ITEMS : ' + str(get_total_entries()) + "\t\tINVENTORY WORTH : " + str(get_inventory_worth()), foreground=light3, background=dark1)
info_label.pack(side='bottom', fill=X, padx=2, pady=2)

sub_label = ttk.Label(action_frame, text='', borderwidth=1, font=('consolas',11,BOLD), foreground=light3, background=dark1)
sub_label.grid(row=5, column=3, columnspan=3, padx=(2,3), pady=(3, 3), sticky='nsew')

#NOTE: this is a normal tkinter widget (NOT from ttk) 
custom_query_entry = Entry(action_frame, textvariable=CUSTOM_QUERY, width=37, font=('consolas',13), justify=CENTER, bg=dark0, foreground=light3, highlightthickness=1, insertbackground=blue, insertwidth=2)
custom_query_entry.grid(row=5, column=0, sticky='nsew', padx=(3, 2), pady=(3, 3), columnspan=2)
custom_query_entry.bind('<Key-Return>',run_custom_query)
custom_query_entry.bind('<Enter>',lambda event: sub_label.config(text='Execute an SQL query', foreground=light3))
#the reason behind not updating highlight color in the next line is to show user if previous execution was a success or not
custom_query_entry.bind('<Key>', lambda event: custom_query_entry.config(foreground=light3))
custom_query_entry.bind('<FocusOut>', lambda event: CUSTOM_QUERY.set('Enter an SQL query ...') if CUSTOM_QUERY.get() == '' else None)
custom_query_entry.bind('<FocusIn>', lambda event: CUSTOM_QUERY.set('') if CUSTOM_QUERY.get() == 'Enter an SQL query ...' else None)

run_query_button = ttk.Button(action_frame, text='⮐', command=run_custom_query, width=3)
run_query_button.grid(row=5, column=2, padx=(2, 2), pady=(3, 3), sticky='nse')
run_query_button.bind('<Enter>', lambda event=None: sub_label.config(text='Execute an SQL query', foreground=light3))


search_entry = Entry(action_frame, textvariable=SEARCH, justify=CENTER, font=('consolas',11), bg=light3)
search_entry.grid(row=0, column=3, columnspan=3, padx=(1,3), pady=(3,2), sticky='nsew')

#action buttons
#row1
search_button = ttk.Button(action_frame, text="SEARCH", command=search_record)
search_button.grid(row=1, column=3, padx=(2,0), pady=(1, 0), sticky='nsew')
search_button.bind('<Enter>', lambda event=None: sub_label.config(text='Search for an item', foreground=light3))
clear_button = ttk.Button(action_frame, text="CLEAR", command=reset)
clear_button.grid(row=1, column=4, padx=(1,0), pady=(1, 0), sticky='nsew')
clear_button.bind('<Enter>', lambda event=None: sub_label.config(text='Clear selections and entries', foreground=light3))
delete_button = ttk.Button(action_frame, text='DELETE', command=delete_record)
delete_button.grid(row=1, column=5, padx=(1,3), pady=(1, 0), sticky='nsew')
delete_button.bind('<Enter>', lambda event=None: sub_label.config(text='Delete the selected entry', foreground=red))
#row2
update_button = ttk.Button(action_frame, text='UPDATE', command=update_data)
update_button.grid(row=2, column=3, padx=(2,0), pady=(1, 0), sticky='nsew')
update_button.bind('<Enter>', lambda event=None: sub_label.config(text='Update the selected entry', foreground=light3))
add_new_button = ttk.Button(action_frame, text='INSERT', command=insert_new)
add_new_button.grid(row=2, column=4, padx=(1,0), pady=(1, 0), sticky='nsew')
add_new_button.bind('<Enter>', lambda event=None: sub_label.config(text='Add a new entry', foreground=green))
empty_button = ttk.Button(action_frame, text='EMPTY', command=delete_all)
empty_button.grid(row=2, column=5, padx=(1,3), pady=(1, 0), sticky='nsew')
empty_button.bind('<Enter>', lambda event=None: sub_label.config(text='Delete all entries', foreground=red))
#row3
export_button = ttk.Button(action_frame, text='EXPORT', command=export_to_csv)
export_button.grid(row=3, column=3, padx=(2,0), pady=(1, 0), sticky='nsew')
export_button.bind('<Enter>', lambda event=None: sub_label.config(text='Export to a CSV file', foreground=green))
import_from_csv_button = ttk.Button(action_frame, text='IMPORT', command=import_from_csv)
import_from_csv_button.grid(row=3, column=4, padx=(1,0), pady=(1, 0), sticky='nsew')
import_from_csv_button.bind('<Enter>', lambda event=None: sub_label.config(text='Import from a CSV file', foreground=light3))
generate_report_button = ttk.Button(action_frame, text='REPORT', command=generate_report)
generate_report_button.grid(row=3, column=5, padx=(1,3), pady=(1, 0), sticky='nsew')
generate_report_button.bind('<Enter>', lambda event=None: sub_label.config(text='Generate Inventory Report', foreground=green))

#row4
product_total_label = ttk.Label(action_frame, text='', borderwidth=1, background=light3, font=('consolas',10,BOLD))
product_total_label.grid(row=4, column=3, columnspan=2, padx=(2,0), pady=(1, 0), sticky='nsew')

exit_inventory_button = ttk.Button(action_frame, text='EXIT', command=destroy_root_window)
exit_inventory_button.grid(row=4, column=5, padx=(1,3), pady=(1, 0), sticky='nsew')
exit_inventory_button.bind('<Enter>', lambda event=None: sub_label.config(text='Exit the Program', foreground=red))

#display labels and entries
pid_label = ttk.Label(action_frame, text='PRODUCT_ID', borderwidth=1, width=22).grid(row=0, column=0, sticky='nsew', padx=(3, 0), pady=(3, 0))
new_pid_entry = Entry(action_frame, textvariable=PRODUCT_ID, width=26, justify=CENTER, foreground=dark0 ,font=('consolas',11, BOLD), bg=light3, fg=blue).grid(row=0, column=1, columnspan=2, sticky='nsew', padx=(1,2), pady=(3, 0))

product_label = ttk.Label(action_frame, text='PRODUCT', borderwidth=1, width=22).grid(row=1, column=0, sticky='nsew', padx=(3, 0), pady=(1, 0))
new_product_entry = Entry(action_frame, textvariable=PRODUCT_NAME, width=26, justify=CENTER, font=('consolas',11), bg=light3).grid(row=1, column=1, columnspan=2, sticky='nsew', padx=(1,2), pady=(1, 0))

quantity_label = ttk.Label(action_frame, text='QUANTITY', borderwidth=1, width=22).grid(row=2, column=0, sticky='nsew', padx=(3, 0), pady=(1, 0))
new_quantity_entry = Entry(action_frame, textvariable=PRODUCT_QUANTITY, width=26, justify=CENTER, font=('consolas',11), bg=light3).grid(row=2, column=1, columnspan=2, sticky='nsew', padx=(1,2), pady=(1, 0))

price_label = ttk.Label(action_frame, text='UNIT PRICE', borderwidth=1, width=22).grid(row=3, column=0, sticky='nsew', padx=(3, 0), pady=(1, 0))
new_price_entry = Entry(action_frame, textvariable=PRODUCT_PRICE, width=26, justify=CENTER, font=('consolas',11), bg=light3).grid(row=3, column=1, columnspan=2, sticky='nsew', padx=(1,2), pady=(1, 0))

date_label = ttk.Label(action_frame, text='DATE ADDED', borderwidth=1, width=22).grid(row=4, column=0, sticky='nsew', padx=(3, 0), pady=(1, 0))
date_entry = Entry(action_frame, textvariable=DATE, width=26, justify=CENTER, font=('consolas',11), bg=light3).grid(row=4, column=1, columnspan=2, sticky='nsew', padx=(1,2), pady=(1, 0))

scroll_y = ttk.Scrollbar(inventory_window, orient=VERTICAL)

tree_view_widget = ttk.Treeview(inventory_window, columns=("S.No","P_ID", "Product", "Quantity", "Price", "Date"), selectmode="extended", height=100, yscrollcommand=scroll_y.set)


#configure a scrollbar for the treeview
scroll_y.config(command=tree_view_widget.yview)
scroll_y.pack(side=RIGHT, fill=Y)   

ORDER.set('ASC')
CUSTOM_QUERY.set('Enter an SQL query ...')

#treeview headings
tree_view_widget.heading('S.No', text="S.No", anchor=CENTER, command=lambda: sort("P_ID"))
tree_view_widget.heading('P_ID', text="PRODUCT ID", anchor=CENTER, command=lambda: sort("P_ID"))
tree_view_widget.heading('Product', text="PRODUCT", anchor=CENTER, command=lambda: sort("Product"))
tree_view_widget.heading('Quantity', text="QUANTITY", anchor=CENTER, command=lambda: sort("Quantity"))
tree_view_widget.heading('Price', text="UNIT PRICE", anchor=CENTER, command=lambda: sort("Price"))
tree_view_widget.heading('Date', text="DATE ADDED", anchor=CENTER, command=lambda: sort("Date"))
tree_view_widget.column('#0', minwidth=0, width=0, stretch=False)
tree_view_widget.column('#1', minwidth=60, width=60, anchor=CENTER)
tree_view_widget.column('#2', minwidth=60, width=60, anchor=CENTER)
tree_view_widget.column('#3', minwidth=60, width=60, anchor=CENTER)
tree_view_widget.column('#4', minwidth=60, width=60, anchor=CENTER) 
tree_view_widget.column('#5', minwidth=60, width=60, anchor=CENTER)
tree_view_widget.column('#6', minwidth=60, width=60, anchor=CENTER)
tree_view_widget.pack(fill=X)
#bind this event to get_data() 
tree_view_widget.bind('<<TreeviewSelect>>', get_data)
tree_view_widget.bind('<Motion>', get_cell)
#prevent manual resizing of column width
tree_view_widget.bind('<Button-1>', escape_click)
fetch_table()


#draw seperator lines for ease of viewing
for i in range(2,13,2):
    ttk.Separator(tree_view_widget, orient='vertical').place(relx=i/12,rely=0,relheight=1,relwidth=0)
# ttk.Separator(tree_view_widget, orient='horizontal').place(relx=0,rely=0.095,relheight=0,relwidth=1)

inventory_window.mainloop()
#TODO update total items and total price acc to search view
