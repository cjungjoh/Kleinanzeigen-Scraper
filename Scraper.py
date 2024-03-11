''' Script for collecting new entries of appartment-articles and sending a Windows notification if so.
Text with Link will be displayed in cmd.'''

from requests_html import HTML, HTMLSession
from win10toast_click import ToastNotifier
import time
from datetime import datetime
import webbrowser
#import time
import random
import os
from logging import error

# set toast texts
toast_head = ''
toast_msg = ''
# set output message
output_msg = ''
# other variables
open_url_links = ['']
bool_new_article = False
base_countdown = 15
t = 0
go = True
start = True
tim = datetime.now().time()
day = (datetime.today()).strftime('%d.%m.%Y')
# there is a function in os module to get this path automatically, I was just too lazy to implement :^)
# just copy path from the file in here
fullpath = "Path to this file/LastLinks.txt"   
# html stuff
# just enter link here. F.e if you want to check on appartments for rent up to 1000 €, 
# enter this information on kleinanzeigen.de and copy the link here
mainsession = 'Link to your kleinanzeigen-site you want to check'   
session = HTMLSession()
r = session.get(mainsession)




####################
# read write stuff #
####################


def write_txt(text):
    # please format text in seperate lines!
    try:
        f = open(fullpath, 'w')
        f.write("{}".format(text))
        f.close()
        print("updated file.")
    except error as e:
        f.close()
        print("An error ocurred during writing file. {}".format(e))

def read_txt():

    if os.path.exists("LastLinks.txt"):
        f = open(fullpath, 'r')
        output = f.read()
        f.close()
    else:
        print("File doesnt exist!")
    return output


########
# html #
########
def get_article(data_adid):
    # finds specific article thanks to data_adid
    string = '[data-adid="' + str(data_adid) + '"]'
    art = r.html.find(string)
    return art


#########
# sonst #
#########

def get_data_adid(list):
    # needs list with converted string entries
    adid_list = []
    for entry in list:
        article_split = entry.split()   # generates list -> ['<Element', "'article'", "class=('aditem',)", "data-adid='2288201203'", "data-href='/s-anzeige/wohnung-zur-miete/2288201203-203-8970'>"]
        data_adid = article_split[3].split("'")
        adid_list.append(data_adid[1])
    # print(adid_list)
    return adid_list
    
def get_article_link(article):
    for entry in article:
        split = entry.split()
        linkpart = split[4]   # generates list -> ['<Element', "'article'", "class=('aditem',)", "data-adid='2288201203'", "data-href='/s-anzeige/wohnung-zur-miete/2288201203-203-8970'>"]
        linksplit = linkpart.split("'")
        link = 'https://www.ebay-kleinanzeigen.de' + linksplit[1]
        # print(data_adid[1])
        return link

def convert_objlist_to_strlist(list):
    # convert list with Objects to list with String
    str_list = []
    for obj in list:
        str_list.append(str(obj))
    # print(str_list)
    return str_list

def make_link_list(adid_l):
    link_list = []
    for entry in adid_l: 
        a = get_article(entry)
        str_a = convert_objlist_to_strlist(a)
        a_link = get_article_link(str_a)
        link_list.append(a_link)
    return link_list

def get_newest_links(link_l):
    global toast_head
    global toast_msg
    global bool_new_article
    new_link_l = []
    print(new_link_l, len(new_link_l))
    x = 0
    last_link = ''
    print("File_Links Size: {}".format(len(last_link)))
    last_link = read_txt()
    print(last_link)

    if last_link == '':
        # if file is empty (at first start/deletion etc.), get first 3 links
        y = 0
        for link in link_l:
            if y < 3:
                new_link_l.append(link)
                y += 1
        make_toast_text(1)
        make_output_text(1)
        bool_new_article = True
    else:
        for link in link_l:
            if link != last_link:
                # if link is diff than last link and no 3 links are already picked
                if x < 3:
                    new_link_l.append(link)
                    x += 1
                else:
                    # if more than 3 entries are new
                    make_toast_text(1)
                    make_output_text(1)
                    bool_new_article = True
            elif link == last_link:
                # if no new links found
                if x == 0:
                    make_toast_text(2)
                    make_output_text(2)
                else:
                # if there are just 1, 2 new links
                    make_toast_text(0)
                    make_output_text(0)
                    bool_new_article = True
                break
            else:
                print("Sth went wrong by comparing links.")
                make_output_text(3)

    return new_link_l


def make_toast_text(x):
    global toast_head
    global toast_msg
    if x == 0:
        toast_head = "Some new entries."
        toast_msg = "Klick to open."
    elif x == 1:
        toast_head = "Many new entries!"
        toast_msg = "Please see log for all links."   

def make_output_text(x):
    global output_msg
    if x == 0:
        output_msg = "*** New entries ***"
    elif x == 1:
        output_msg = "*** Many new entries! ***"
    elif x == 2:
        output_msg = "*** NO new ones, sad ***"
    elif x == 3:
        output_msg = "*** ERROR ***"

def open_url_click():
    if bool_new_article:
        open_url()

def open_url():
    for link in open_url_links:
        try:
            webbrowser.open_new(link)
        except:
            print('Failed to open URL.')

def toast():
    try:
        toaster = ToastNotifier()
        toaster.show_toast(toast_head, toast_msg, duration=None, callback_on_click=open_url_click)
    except:
        print('insert ugly toast errors here.')

def randomnumber():
    global t
    global base_countdown
    x = random.randint(1,4)
    tim = (base_countdown + x)*60
    print("Sleep: {}".format(tim))
    return tim

def countdown(t):
    time.sleep(t)

def output(new_links):
    global output_msg
    global toast_msg
    global toast_head
    global bool_new_article

    print("\n*** Global Link: {} *** Time: {}".format(mainsession, tim))
    print("{}".format(output_msg))
    for l in new_links:
        print("{}".format(l))
    if bool_new_article:
        write_txt(new_links[0])
        toast()
    else:
        print("Bool new articles: {}".format(bool_new_article))
    # clear up
    toast_msg = ''
    toast_head = ''
    output_msg = ''
    bool_new_article = False


while go:
    art_list = r.html.find('.aditem')
    str_art_list = convert_objlist_to_strlist(art_list)
    adid_list = get_data_adid(str_art_list)
    link_list = make_link_list(adid_list)
    open_url_links = get_newest_links(link_list)
    output(open_url_links)
    countdown(randomnumber())
    start = False
    r = session.get(mainsession)


