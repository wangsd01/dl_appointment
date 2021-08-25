import random
from datetime import datetime
from pydub import AudioSegment
from pydub.playback import play
import os
import re
import requests
from bs4 import BeautifulSoup
from slimit import ast
from slimit.parser import Parser
from slimit.visitors import nodevisitor
import time
import urllib
from io import BytesIO



def get_soup_from_url(url):
    """
    Returns the JSON from the given financialmodelingprep.com URL.
    """
    request = requests.get(url)
    data_html = request.text
    return BeautifulSoup(data_html, 'html.parser')

def get_array_items(node):
    array_items = []
    for item in node.initializer.items:
        parsed_dict = {}
        for n in nodevisitor.visit(item):
            if isinstance(n, ast.Assign):
                key = getattr(n.left, 'value', '')[1:-1]
                value = getattr(n.right, 'value', '')
                if len(value) > 2 and value[0] == '"':
                    value = value[1:-1]
                parsed_dict[key] = value
        array_items.append(parsed_dict)
    return array_items

def play_music():
    # music_url = ""
    # req = urllib.request.Request(music_url, headers={'User-Agent': ''}) 
    # mp3 = urllib.request.urlopen(req).read()
    # music = AudioSegment.from_mp3(ByteIO(mp3))

    # music preview downloaded from https://soundbible.com/1937-Tornado-Siren-II.html
    music = AudioSegment.from_mp3("Tornado_Siren_II-Delilah-747233690.mp3")
    print("Playing mp3 file...")
    # play the file
    play(music * 5)


url = 'https://telegov.njportal.com/njmvc/AppointmentWizard/17'


final_data_time = datetime(year=2021, month=9, day=30, hour=12)

while True:
    soup = get_soup_from_url(url)
    # script = soup.find('script')
    script = soup.find('script', text=lambda text: text and "var locationData = " in text)
    if script is None:
        time.sleep(random.randrange(start=0, stop=30))
        continue
    # parse js
    parser = Parser()
    tree = parser.parse(script.string)
    for node in nodevisitor.visit(tree):
        if isinstance(node, ast.VarDecl) and hasattr(node.initializer, 'items'):
            if node.identifier.value == 'locationData':
                locationData = get_array_items(node)
            elif node.identifier.value == 'timeData':
                timeData = get_array_items(node)
            elif node.identifier.value == 'locationModel':
                locationModel = get_array_items(node)
    # print(timeData)

    location_dict = dict()

    for location in locationData:
        id = location['LocationId']
        location_dict[id] = location
    for time_dict in timeData:
        id = time_dict['LocationId']
        if time_dict['FirstOpenSlot'] == 'No Appointments Available':
            continue
        n_appointment, next_time = time_dict['FirstOpenSlot'].split(' Appointments Available <br/> Next Available: ')
        date_time_obj = datetime.strptime(next_time, '%m/%d/%Y %I:%M %p')
        if date_time_obj < final_data_time:
            print("{} has {} appointments at {}".format(location_dict[id]['Name'], n_appointment, date_time_obj))
            play_music()
    print("not found! continue..")
    time.sleep(random.randrange(start=0, stop=300))
