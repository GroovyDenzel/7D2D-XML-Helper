# Copyright (C) 2024  Simon Hofer
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA.

import shutil
import tkinter
from tkinter import *
from tkinter import ttk
from tkinter import filedialog
from os.path import exists
from os import path
from PIL import Image, ImageTk
import lxml.etree as et
from xml.dom import minidom
from lxml import etree
from bs4 import BeautifulSoup
import random
import os

file_src = ""
lightning_src = ""
biom_src = ""
map_src = ""
map_info = ""
trader_rekt_src = ""
trader_jen_src = ""
trader_bob_src = ""
trader_hugh_src = ""
trader_joel_src = ""
output_list = []  # 1
output_list_details = []  # 1
displayed_hints = set()
directory = ""


def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)


def update_output():
    global text
    global text_detail
    text.config(state=NORMAL)
    text_detail.config(state=NORMAL)
    text_detail.delete('1.0', tkinter.END)
    text.delete('1.0', tkinter.END)
    for item in output_list:
        text.insert(tkinter.END, item + "\n")
        # text.insert(tkinter.END, "\n")
    for item in output_list_details:
        text_detail.insert(tkinter.END, item + "\n")
        # text_detail.insert(tkinter.END, "\n")
    text.config(state=DISABLED)
    text_detail.config(state=DISABLED)


def xmlprocessing():
    # set configuration
    global lightning_src
    global biom_src
    global file_src
    trader_spec = ""
    trader_spec_not = ""
    if var_tradersetup1.get() == "1":
        if var_tradersetup2.get() == "1":
            trader_spec = "all"
        else:
            trader_spec = "oldwest"
            trader_spec_not = "roadside"
    elif var_tradersetup2.get() == "1":
        trader_spec = "roadside"
        trader_spec_not = "oldwest"
    else:
        trader_spec_not = "all"

    # weather XML changes
    add_weather_snow(biom_src, 'wasteland')
    with open(biom_src, 'r') as file:
        data = file.read()
    bs_data_weather = BeautifulSoup(data, "xml")
    weatherprocessing(bs_data_weather, var_temperature.get())
    adjust_game_loot_stage(bs_data_weather, var_loot.get())
    output = bs_data_weather.prettify(formatter="minimal")
    with open(biom_src, 'w') as file:
        file.write(output)

    # lightning XML changes
    with open(lightning_src, 'r') as file:
        data_world = file.read()
    bs_data_world = BeautifulSoup(data_world, "xml")
    adjust_lightning(bs_data_world, var_lightning.get())
    output_world = bs_data_world.prettify(formatter="minimal")
    with open(lightning_src, 'w') as file:
        file.write(output_world)

    # rwgmixer XML changes
    with open(file_src, 'r') as file:
        data_mixer = file.read()
    bs_data_mixer = BeautifulSoup(data_mixer, "xml")
    landscape(bs_data_mixer, var_worldsize.get(), var_landscape_detail.get(),
              var_landscape_detail2.get())
    trader2biomes(bs_data_mixer, var_traderexcl.get())
    tradercount(bs_data_mixer, var_tradercount.get())
    traderspecial(bs_data_mixer, trader_spec, "true")
    traderspecial(bs_data_mixer, trader_spec_not, "false")
    towns2biomes(bs_data_mixer, choice=var_townexcl.get())
    smalltownsize(bs_data_mixer, wsize=var_worldsize.get(), choice=var_townsize1.get())
    bigtownsize(bs_data_mixer, wsize=var_worldsize.get(), choice=var_townsize2.get())
    smalltowncount(bs_data_mixer, wsize=var_worldsize.get(), choice=var_towncount1.get())
    bigtowncount(bs_data_mixer, wsize=var_worldsize.get(), choice=var_towncount2.get())
    districtcolors(bs_data_mixer, var_districtcolor.get())
    output_mixer = bs_data_mixer.prettify(formatter="minimal")
    with open(file_src, 'w') as file:
        file.write(output_mixer)

    # POIs XML changes
    adjust_trader(trader_rekt_src, "rekt", var_traderfree.get())
    adjust_trader(trader_jen_src, "jen", var_traderfree.get())
    adjust_trader(trader_bob_src, "bob", var_traderfree.get())
    adjust_trader(trader_hugh_src, "hugh", var_traderfree.get())
    adjust_trader(trader_joel_src, "joel", var_traderfree.get())
    poi_fix(var_poifix.get())


def show_hint():
    global text_hints
    global displayed_hints
    text_hints.config(state=NORMAL)
    text_hints.delete('1.0', tkinter.END)
    remaining_hints = set(hints) - displayed_hints
    if remaining_hints:
        random_hint = random.choice(list(remaining_hints))
        displayed_hints.add(random_hint)
        text_hints.insert(tkinter.END, random_hint + "\n")
    else:
        text_hints.insert(tkinter.END, "No more hints available!\n")
    text_hints.config(state=DISABLED)


def exitnew():
    root.destroy()


def process_map():
    mapsize = ""
    global output_list
    global output_list_details
    seed_value = ""
    poisname = []

    with open(map_src, 'r') as file:
        data_map = file.read()
    bs_datas_data = BeautifulSoup(data_map, "lxml")
    with open(map_info, 'r') as file:
        data_info = file.read()
    bs_data_info = BeautifulSoup(data_info, "lxml")

    for tag in bs_datas_data.find_all(True):
        names = tag.attrs
        if bool(names):
            name_value = names['name']
            poisname.append(name_value)
    for tag_info in bs_data_info.find_all(True):
        names_info = tag_info.attrs
        if bool(names_info):
            name_info = names_info['name']
            if name_info == "HeightMapSize":
                mapsize = names_info['value']
        seeds_info = tag_info.attrs
        if bool(seeds_info):
            seed_info = seeds_info['name']
            if seed_info == "Generation.Seed":
                seed_value = seeds_info['value']
    if mapsize == "10240,10240":
        mapsize = 10240
    elif mapsize == "9216,9216":
        mapsize = 9216
    elif mapsize == "8192,8192":
        mapsize = 8192
    elif mapsize == "7168,7168":
        mapsize = 7168
    elif mapsize == "6144,6144":
        mapsize = 6144
    elif mapsize == "5120,5120":
        mapsize = 5120
    elif mapsize == "4096,4096":
        mapsize = 4096
    elif mapsize == "3072,3072":
        mapsize = 3072
    elif mapsize == "2048,2048":
        mapsize = 2048
    else:
        mapsize = "modified"
    output_add = "Size of map is: " + str(mapsize)
    output_list.append(output_add)
    output_add_seed = "Map-Seed is: " + str(seed_value)
    output_list.append(output_add_seed)
    output_add = "Number of POIs (with dublicates): " + str(len(poisname))
    output_list.append(output_add)
    poisname_set = list(set(poisname))
    output_add = "Number of POIs (no dublicates): " + str(len(poisname_set))
    output_list.append(output_add)
    output_add = ("Number of traders: " + str(poisname.count("trader_rekt")) + " " + str(poisname.count("trader_jen")) +
                  " " + str(poisname.count("trader_bob")) + " " + str(poisname.count("trader_hugh")) +
                  " " + str(poisname.count("trader_joel")))
    output_list.append(output_add)
    tier1_common = set(tier1).intersection(poisname_set)
    tier2_common = set(tier2).intersection(poisname_set)
    tier3_common = set(tier3).intersection(poisname_set)
    tier4_common = set(tier4).intersection(poisname_set)
    tier5_common = set(tier5).intersection(poisname_set)
    tier1_commoncount = len(tier1_common)
    tier2_commoncount = len(tier2_common)
    tier3_commoncount = len(tier3_common)
    tier4_commoncount = len(tier4_common)
    tier5_commoncount = len(tier5_common)
    # poisname_unavailable = ['park_plaza_02', 'church_sm_01', 'gas_station_02', 'cave_04',
    #                        'commercial_strip_01', 'house_old_ranch_12', 'house_modern_02', 'city_center_01']
    poisname_missingtier1 = set(tier1) - tier1_common
    poisname_missingtier2 = set(tier2) - tier2_common
    poisname_missingtier3 = set(tier3) - tier3_common
    poisname_missingtier4 = set(tier4) - tier4_common
    poisname_missingtier5 = set(tier5) - tier5_common
    """ ONLY WHEN USED WITH UNAVAILABLE POI"""
    # poisname_missingtier1 = poisname_missingtier1 - poisname_missingtier1.intersection(poisname_unavailable)
    # poisname_missingtier2 = poisname_missingtier2 - poisname_missingtier2.intersection(poisname_unavailable)
    # poisname_missingtier3 = poisname_missingtier3 - poisname_missingtier3.intersection(poisname_unavailable)
    # poisname_missingtier4 = poisname_missingtier4 - poisname_missingtier4.intersection(poisname_unavailable)
    # poisname_missingtier5 = poisname_missingtier5 - poisname_missingtier5.intersection(poisname_unavailable)
    points = (tier1_commoncount * 1 + tier2_commoncount * 2 + tier3_commoncount * 4
              + tier4_commoncount * 7 + tier5_commoncount * 20)
    output_add = "Tier 1: " + str(tier1_commoncount) + " of " + str(len(tier1)) + " - " + str(
        "{:5.1f}".format(tier1_commoncount / len(tier1) * 100)) + "%"
    output_list.append(output_add)
    output_add = "Tier 2: " + str(tier2_commoncount) + " of " + str(len(tier2)) + " - " + str(
        "{:5.1f}".format(tier2_commoncount / len(tier2) * 100)) + "%"
    output_list.append(output_add)
    output_add = "Tier 3: " + str(tier3_commoncount) + " of " + str(len(tier3)) + " - " + str(
        "{:7.1f}".format(tier3_commoncount / len(tier3) * 100)) + "%"
    output_list.append(output_add)
    output_add = "Tier 4: " + str(tier4_commoncount) + " of " + str(len(tier4)) + " - " + str(
        "{:7.1f}".format(tier4_commoncount / len(tier4) * 100)) + "%"
    output_list.append(output_add)
    output_add = "Tier 5: " + str(tier5_commoncount) + " of " + str(len(tier5)) + " - " + str(
        "{:7.1f}".format(tier5_commoncount / len(tier5) * 100)) + "%"
    output_list.append(output_add)
    if poisname_missingtier1:
        output_add_details = "Missing POIs in tier1: " + str(poisname_missingtier1)
        output_list_details.append(output_add_details)
    if poisname_missingtier2:
        output_add_details = "Missing POIs in tier2: " + str(poisname_missingtier2)
        output_list_details.append(output_add_details)
    if poisname_missingtier3:
        output_add_details = "Missing POIs in tier3: " + str(poisname_missingtier3)
        output_list_details.append(output_add_details)
    if poisname_missingtier4:
        output_add_details = "Missing POIs in tier4: " + str(poisname_missingtier4)
        output_list_details.append(output_add_details)
    if poisname_missingtier5:
        output_add_details = "Missing POIs in tier5: " + str(poisname_missingtier5)
        output_list_details.append(output_add_details)
    output_add = "Total POI-Map-Points are: " + str(points)
    output_list.append(output_add)
    output_add = "Your map is " + str(qualitycalc(mapsize, points))
    output_list.append(output_add)
    poisname_set.clear()
    poisname[:] = []
    update_output()
    output_list[:] = []
    output_list_details[:] = []
    tier1_common.clear()
    tier2_common.clear()
    tier3_common.clear()
    tier4_common.clear()
    tier5_common.clear()
    poisname_missingtier1.clear()
    poisname_missingtier2.clear()
    poisname_missingtier3.clear()
    poisname_missingtier4.clear()
    poisname_missingtier5.clear()


def qualitycalc(worldsize_c, points_c):
    if worldsize_c == 10240:
        multiplier = 1.00
    elif worldsize_c == 9216:
        multiplier = 1.02
    elif worldsize_c == 8192:
        multiplier = 1.04
    elif worldsize_c == 7168:
        multiplier = 1.06
    elif worldsize_c == 6144:
        multiplier = 1.08
    elif worldsize_c == 5120:
        multiplier = 1.14
    elif worldsize_c == 4096:
        multiplier = 1.2
    elif worldsize_c == 3072:
        multiplier = 1.3
    elif worldsize_c == 2048:
        multiplier = 1.4
    else:
        multiplier = 1
    points_c = points_c*multiplier
    if points_c > 1546:
        quality = "perfect"
    elif points_c > 1525:
        quality = "almost-perfect"
    elif points_c > 1500:
        quality = "awesome"
    elif points_c > 1475:
        quality = "very good"
    elif points_c > 1450:
        quality = "good"
    elif points_c > 1400:
        quality = "ok"
    elif points_c > 1300:
        quality = "meh, you might want to change some settings"
    else:
        quality = "POI-lame, adjust your settings for POI-variety"
    return quality


def choose_directory():
    global file_src
    global lightning_src
    global biom_src
    global trader_rekt_src
    global trader_jen_src
    global trader_bob_src
    global trader_hugh_src
    global trader_joel_src
    global directory
    directory = filedialog.askdirectory()
    if directory:
        path_window.config(text=directory)
        file_src = directory + "/Data/Config/rwgmixer.xml"
        lightning_src = directory + "/Data/Config/worldglobal.xml"
        biom_src = directory + "/Data/Config/biomes.xml"
        trader_rekt_src = directory + "/Data/Prefabs/POIs/trader_rekt.xml"
        trader_jen_src = directory + "/Data/Prefabs/POIs/trader_jen.xml"
        trader_bob_src = directory + "/Data/Prefabs/POIs/trader_bob.xml"
        trader_hugh_src = directory + "/Data/Prefabs/POIs/trader_hugh.xml"
        trader_joel_src = directory + "/Data/Prefabs/POIs/trader_joel.xml"
        save_file(file_src)
        save_file(lightning_src)
        save_file(biom_src)
        save_file(trader_rekt_src)
        save_file(trader_jen_src)
        save_file(trader_bob_src)
        save_file(trader_hugh_src)
        save_file(trader_joel_src)


def choose_map_directory():
    global map_src
    global map_info
    initialdirectory = path.expandvars(r"%appdata%\7DaysToDie\GeneratedWorlds")
    directory_map = filedialog.askdirectory(initialdir=initialdirectory)
    if directory_map:
        path_window_map.config(text=directory_map)
        map_src = directory_map + "/prefabs.xml"
        map_info = directory_map + "/map_info.xml"
        debug_window.config(text=map_src)
        process_map()


def save_file(file):
    backup_file = file + "-BACKUP"
    if not (exists(backup_file)):
        shutil.copyfile(file, backup_file)


def set_tag(bs_data, tag_d="biomes", value="default"):  #
    tag_c = bs_data.find(tag_d, {'name': value})
    return tag_c


def set_property(tag_c, spec, value):
    prop_c = tag_c.find('property', {spec: value})
    return prop_c


def set_detail(group, spec, value):
    detail_c = group.find('property', {spec: value})
    return detail_c


def set_value(detail_c, value):
    detail_c['value'] = value
    return 0


def add_weather_snow(biom_src_c, biome_c="wasteland"):
    xmlfile = et.parse(biom_src_c)
    world_generation = xmlfile.getroot()
    searchstring = ".//biome[@name=\'" + biome_c + "\']"
    newelement = world_generation.find(searchstring)
    if newelement.find(".//weather[@name='snow']") is None:
        snow_weather = et.SubElement(newelement, "weather", name="snow", prob="0")
        et.SubElement(snow_weather, "Temperature", min="-35", max="-28", prob="1")
        et.SubElement(snow_weather, "CloudThickness", min="55", max="75", prob="1")
        et.SubElement(snow_weather, "Precipitation", min="30", max="60", prob="1")
        et.SubElement(snow_weather, "Fog", min="3", max="8", prob="1")
        et.SubElement(snow_weather, "Wind", min="18", max="25", prob="1")
        et.SubElement(snow_weather, "spectrum", name="Snowy")
        newelement.insert(2, snow_weather)
        xml_str = et.tostring(world_generation,
                              encoding="utf-8",
                              xml_declaration=True)
        parsed_str = minidom.parseString(xml_str)
        pretty_xml_str = parsed_str.toprettyxml(indent="  ", newl='\n')
        with open(biom_src_c, "w", encoding="utf-8") as file:
            file.write(pretty_xml_str)
    # Remove empty lines
        parser = etree.XMLParser(remove_blank_text=True)
        cleanup_xml = etree.parse(biom_src_c, parser)
        pretty_xml_str2 = etree.tostring(cleanup_xml,
                                         pretty_print=True,
                                         encoding='utf-8',
                                         xml_declaration=True).decode('utf-8')
        with open(biom_src_c, 'w', encoding='utf-8') as file2:
            file2.write(pretty_xml_str2)


def adjust_temp(bs_data, biom_c='wasteland', weather_c='snow', temp_min='0', temp_max='0'):
    tag = bs_data.find("biomes")
    biom = tag.find('biome', {'name': biom_c})
    weather = biom.find('weather', {'name': weather_c})
    if weather is not None:
        temperature = weather.find('Temperature')
        if temperature is not None:
            temperature['min'] = temp_min
            temperature['max'] = temp_max


def adjust_trader(data_trader, trader_c="rekt", choice_c="default"):
    xmlfile = et.parse(data_trader)
    trader_xml = xmlfile.getroot()
    if choice_c == "default":
        allowedtowns_element = trader_xml.find(".//property[@name='AllowedTownships']")
        if allowedtowns_element is not None:
            allowedtowns_element.set("value", "city,town,rural,wilderness")
        editorgroup_element = trader_xml.find(".//property[@name='EditorGroups']")
        if editorgroup_element is not None:
            editorgroup_element.set("value", "settlements")
        tags_element = trader_xml.find(".//property[@name='Tags']")
        if tags_element is not None:
            tags_element.set("value", "gateway, nocheckpoint")
        poimarkertags_element = trader_xml.find(".//property[@name='POIMarkerTags']")
        if poimarkertags_element is not None:
            if trader_c == "joel":
                poimarkertags_element.set("value", "rural#gateway")
            elif trader_c == "hugh":
                poimarkertags_element.set("value", "countrytown")
            elif trader_c == "bob":
                poimarkertags_element.set("value", "industrial#industrial#gateway#gateway#countrytown#countrytown")
            elif trader_c == "jen":
                poimarkertags_element.set("value", "rural#rural#gateway#gateway")
            elif trader_c == "rekt":
                poimarkertags_element.set("value", "rural")
    elif choice_c == "inside":
        if trader_c == "rekt" or trader_c == "jen":
            allowedtowns_element = trader_xml.find(".//property[@name='AllowedTownships']")
            if allowedtowns_element is not None:
                allowedtowns_element.set("value", "city, town, rural, wilderness, citybig, wasteland_city, "
                                                  "countrytown, "
                                                  "bforest_town, bforest_countrytown, forest_countrytown")
            editorgroup_element = trader_xml.find(".//property[@name='EditorGroups']")
            if editorgroup_element is not None:
                editorgroup_element.set("value", "downtown, commercial, industrial, "
                                                 "forest_rural, countrytown, countryresidential, rural")
            tags_element = trader_xml.find(".//property[@name='Tags']")
            if tags_element is not None:
                tags_element.set("value", "downtown, commercial, industrial, countrytown, "
                                          "forest_rural, countryresidential, rural")
            poimarkertags_element = trader_xml.find(".//property[@name='POIMarkerTags']")
            if poimarkertags_element is not None:
                poimarkertags_element.set("value", "downtown, commercial, industrial, countrytown, "
                                                   "forest_rural, countryresidential, rural")
        else:
            allowedtowns_element = trader_xml.find(".//property[@name='AllowedTownships']")
            if allowedtowns_element is not None:
                allowedtowns_element.set("value", "city, town, rural, wilderness, citybig, wasteland_city, "
                                                  "countrytown, "
                                                  "bforest_town, bforest_countrytown, forest_countrytown")
            editorgroup_element = trader_xml.find(".//property[@name='EditorGroups']")
            if editorgroup_element is not None:
                editorgroup_element.set("value", "downtown, commercial, industrial, countrytown, "
                                                 "forest_rural, countryresidential")
            tags_element = trader_xml.find(".//property[@name='Tags']")
            if tags_element is not None:
                tags_element.set("value", "downtown, commercial, industrial, countrytown, "
                                          "countryresidential, forest_rural")
            poimarkertags_element = trader_xml.find(".//property[@name='POIMarkerTags']")
            if poimarkertags_element is not None:
                poimarkertags_element.set("value", "downtown, commercial, industrial, "
                                                   "countrytown, countryresidential, forest_rural")
    elif choice_c == "random":
        allowedtowns_element = trader_xml.find(".//property[@name='AllowedTownships']")
        if allowedtowns_element is not None:
            allowedtowns_element.set("value", "city, town, rural, wilderness, citybig, wasteland_city, countrytown, "
                                              "bforest_town, bforest_countrytown, forest_countrytown")
        editorgroup_element = trader_xml.find(".//property[@name='EditorGroups']")
        if editorgroup_element is not None:
            editorgroup_element.set("value", "settlements, downtown, commercial, industrial, "
                                             "rural, residential, countryresidential, countrytown, forest_rural")
        tags_element = trader_xml.find(".//property[@name='Tags']")
        if tags_element is not None:
            tags_element.set("value", "gateway, nocheckpoint, downtown, commercial, industrial, rural, "
                                      "residential, countryresidential, countrytown, forest_rural")
        poimarkertags_element = trader_xml.find(".//property[@name='POIMarkerTags']")
        if poimarkertags_element is not None:
            poimarkertags_element.set("value", "downtown, commercial, industrial, rural, gateway, "
                                               "countryresidential, residential, countrytown, forest_rural")

    xml_str = et.tostring(trader_xml,
                          encoding="UTF-8",
                          xml_declaration=True)
    parsed_str = minidom.parseString(xml_str)
    pretty_xml_str = parsed_str.toprettyxml(indent="  ", newl='\n')
    with open(data_trader, "w", encoding="UTF-8") as file_c:
        file_c.write(pretty_xml_str)
    # Remove empty lines
    parser = etree.XMLParser(remove_blank_text=True)
    cleanup_xml = etree.parse(data_trader, parser)
    pretty_xml_str2 = etree.tostring(cleanup_xml,
                                     pretty_print=True,
                                     encoding="UTF-8",
                                     xml_declaration=True).decode('utf-8')
    with open(data_trader, 'w', encoding="UTF-8") as file_d:
        file_d.write(pretty_xml_str2)


def poi_fix(choice_c="default"):
    poi01 = directory + "/Data/Prefabs/POIs/cave_04.xml"
    poi02 = directory + "/Data/Prefabs/POIs/church_sm_01.xml"
    poi03 = directory + "/Data/Prefabs/POIs/city_center_01.xml"
    poi04 = directory + "/Data/Prefabs/POIs/commercial_strip_01.xml"
    poi05 = directory + "/Data/Prefabs/POIs/gas_station_02.xml"
    poi06 = directory + "/Data/Prefabs/POIs/house_modern_02.xml"
    poi07 = directory + "/Data/Prefabs/POIs/house_old_ranch_12.xml"
    poi08 = directory + "/Data/Prefabs/POIs/factory_01.xml"
    poi09 = directory + "/Data/Prefabs/POIs/factory_02.xml"
    poi10 = directory + "/Data/Prefabs/POIs/utility_refinery_02.xml"
    data_poi_list = [poi01, poi02, poi03, poi04, poi05, poi06, poi07, poi08, poi09, poi10]
    for poi_item in data_poi_list:
        data_poi = poi_item
        save_file(data_poi)
        poi_xml_file = et.parse(data_poi)
        poi_xml = poi_xml_file.getroot()
        if data_poi == poi01:
            property_change = poi_xml.find(".//property[@name='Tags']")
            if property_change is None:
                if choice_c == "fix":
                    et.SubElement(poi_xml, "property", name="Tags", value="wilderness")
            else:
                if choice_c == "default":
                    poi_xml.remove(property_change)

        if data_poi == poi02:
            property_change = poi_xml.find(".//property[@name='Tags']")
            if property_change is None:
                if choice_c == "fix":
                    et.SubElement(poi_xml, "property", name="Tags", value="countrytown, nodiagonal")
            else:
                if choice_c == "default":
                    poi_xml.remove(property_change)
            property_change = poi_xml.find(".//property[@name='AllowedTownships']")
            if property_change is not None:
                if choice_c == "fix":
                    poi_xml.remove(property_change)
            else:
                if choice_c == "default":
                    et.SubElement(poi_xml, "property", name="AllowedTownships", value="city,town,rural,wilderness")
            property_change = poi_xml.find(".//property[@name='EditorGroups']")
            if property_change is not None:
                if choice_c == "fix":
                    property_change.set("value", "countrytown")
                elif choice_c == "default":
                    property_change.set("value", "commercial")
            property_change = poi_xml.find(".//property[@name='Zoning']")
            if property_change is not None:
                if choice_c == "fix":
                    property_change.set("value", "none")
                elif choice_c == "default":
                    property_change.set("value", "ResidentialOld")

        if data_poi == poi03:
            property_change = poi_xml.find(".//property[@name='Tags']")
            if property_change is not None:
                if choice_c == "fix":
                    property_change.set("value", "downtown, inter02downtowntile")
                elif choice_c == "default":
                    property_change.set("value", "downtown")
            property_change = poi_xml.find(".//property[@name='AllowedTownships']")
            if property_change is None:
                if choice_c == "fix":
                    et.SubElement(poi_xml, "property", name="AllowedTownships", value="city, town")
            else:
                if choice_c == "default":
                    poi_xml.remove(property_change)
            property_change = poi_xml.find(".//property[@name='Zoning']")
            if property_change is not None:
                if choice_c == "fix":
                    property_change.set("value", "downtown")
                elif choice_c == "default":
                    property_change.set("value", "none")

        if data_poi == poi04:
            property_change = poi_xml.find(".//property[@name='Tags']")
            if property_change is not None:
                if choice_c == "fix":
                    property_change.set("value", "countrytown, commercial")
                elif choice_c == "default":
                    property_change.set("value", "countrytown")
            property_change = poi_xml.find(".//property[@name='POIMarkerTags']")
            if property_change is not None:
                if choice_c == "fix":
                    property_change.set("value", "countrytown#countrytown, countrytown, commercial")
                elif choice_c == "default":
                    property_change.set("value", "countrytown#countrytown")

        if data_poi == poi05:
            property_change = poi_xml.find(".//property[@name='Tags']")
            if property_change is not None:
                if choice_c == "fix":
                    property_change.set("value", "industrial")
                elif choice_c == "default":
                    property_change.set("value", "gateway, nocheckpoint")
            property_change = poi_xml.find(".//property[@name='POIMarkerTags']")
            if property_change is not None:
                if choice_c == "fix":
                    property_change.set("value", "industrial")
                elif choice_c == "default":
                    property_change.set("value", "##gateway#gateway")

        if data_poi == poi06:
            property_change = poi_xml.find(".//property[@name='Tags']")
            if property_change is not None:
                if choice_c == "fix":
                    property_change.set("value", "rural")
                elif choice_c == "default":
                    property_change.set("value", "residential")
            property_change = poi_xml.find(".//property[@name='POIMarkerTags']")
            if property_change is not None:
                if choice_c == "fix":
                    property_change.set("value", "rural")
                elif choice_c == "default":
                    property_change.set("value", "residential")
            property_change = poi_xml.find(".//property[@name='Zoning']")
            if property_change is not None:
                if choice_c == "fix":
                    property_change.set("value", "any")
                elif choice_c == "default":
                    property_change.set("value", "ResidentialNew")
            property_change = poi_xml.find(".//property[@name='EditorGroups']")
            if property_change is not None:
                if choice_c == "fix":
                    property_change.set("value", "rural")
                elif choice_c == "default":
                    property_change.set("value", "house new")

        if data_poi == poi07:
            property_change = poi_xml.find(".//property[@name='Tags']")
            if choice_c == "fix":
                property_change.set("value", "rural")
            elif choice_c == "default":
                property_change.set("value", "countryresidential")

        if data_poi == poi08:
            property_change = poi_xml.find(".//property[@name='Tags']")
            if property_change is not None:
                if choice_c == "fix":
                    property_change.set("value", "industrial, rural")
                elif choice_c == "default":
                    property_change.set("value", "industrial")
            property_change = poi_xml.find(".//property[@name='EditorGroups']")
            if property_change is not None:
                if choice_c == "fix":
                    property_change.set("value", "industrial, rural")
                elif choice_c == "default":
                    property_change.set("value", "industrial")

        if data_poi == poi09:
            property_change = poi_xml.find(".//property[@name='Tags']")
            if property_change is not None:
                if choice_c == "fix":
                    property_change.set("value", "industrial, rural")
                elif choice_c == "default":
                    property_change.set("value", "industrial")
            property_change = poi_xml.find(".//property[@name='EditorGroups']")
            if property_change is not None:
                if choice_c == "fix":
                    property_change.set("value", "industrial, rural")
                elif choice_c == "default":
                    property_change.set("value", "industrial")

        if data_poi == poi10:
            property_change = poi_xml.find(".//property[@name='Tags']")
            if property_change is not None:
                if choice_c == "fix":
                    property_change.set("value", "industrial, rural")
                elif choice_c == "default":
                    property_change.set("value", "industrial")
            property_change = poi_xml.find(".//property[@name='POIMarkerTags']")
            if property_change is not None:
                if choice_c == "fix":
                    property_change.set("value", "industrial, rural")
                elif choice_c == "default":
                    property_change.set("value", "industrial")

        xml_str = et.tostring(poi_xml,
                              encoding="UTF-8",
                              xml_declaration=True)
        parsed_str = minidom.parseString(xml_str)
        pretty_xml_str = parsed_str.toprettyxml(indent="  ", newl='\n')
        with open(data_poi, "w", encoding="UTF-8") as file_c:
            file_c.write(pretty_xml_str)
        # Remove empty lines
        parser = etree.XMLParser(remove_blank_text=True)
        cleanup_xml = etree.parse(data_poi, parser)
        pretty_xml_str2 = etree.tostring(cleanup_xml,
                                         pretty_print=True,
                                         encoding="UTF-8",
                                         xml_declaration=True).decode('utf-8')
        with open(data_poi, 'w', encoding="UTF-8") as file_d:
            file_d.write(pretty_xml_str2)


def adjust_weather_prob(bs_data, biom_c='wasteland', weather_c='snow', prob_c='0'):
    tag = bs_data.find("biomes")
    biom = tag.find('biome', {'name': biom_c})
    weather = biom.find('weather', {'name': weather_c})
    if weather is not None:
        weather['prob'] = prob_c


def adjust_game_loot_stage(bs_data, choice_c="default"):
    tag = bs_data.find("biomes")
    biom = tag.find('biome', {'name': "snow"})
    if choice_c == "default":
        biom['difficulty'] = "4"
        biom['gamestage_bonus'] = "20"
        biom['gamestage_modifier'] = "1"
        biom['lootstage_bonus'] = "20"
        biom['lootstage_modifier'] = "1"
    elif choice_c == "wasteland":
        biom['difficulty'] = "1"
        biom['gamestage_bonus'] = "30"
        biom['gamestage_modifier'] = "1.5"
        biom['lootstage_bonus'] = "30"
        biom['lootstage_modifier'] = "1.5"
    elif choice_c == "forest":
        biom['difficulty'] = "1"
        biom['gamestage_bonus'] = "0"
        biom['gamestage_modifier'] = "0"
        biom['lootstage_bonus'] = "0"
        biom['lootstage_modifier'] = "0"
    biom = tag.find('biome', {'name': "pine_forest"})
    if choice_c == "default":
        biom['difficulty'] = "1"
        biom['gamestage_bonus'] = "0"
        biom['gamestage_modifier'] = "0"
        biom['lootstage_bonus'] = "0"
        biom['lootstage_modifier'] = "0"
    elif choice_c == "wasteland":
        biom['difficulty'] = "1"
        biom['gamestage_bonus'] = "30"
        biom['gamestage_modifier'] = "1.5"
        biom['lootstage_bonus'] = "30"
        biom['lootstage_modifier'] = "1.5"
    elif choice_c == "forest":
        biom['difficulty'] = "1"
        biom['gamestage_bonus'] = "0"
        biom['gamestage_modifier'] = "0"
        biom['lootstage_bonus'] = "0"
        biom['lootstage_modifier'] = "0"
    biom = tag.find('biome', {'name': "desert"})
    if choice_c == "default":
        biom['difficulty'] = "3"
        biom['gamestage_bonus'] = "10"
        biom['gamestage_modifier'] = "0.5"
        biom['lootstage_bonus'] = "10"
        biom['lootstage_modifier'] = "0.5"
    elif choice_c == "wasteland":
        biom['difficulty'] = "1"
        biom['gamestage_bonus'] = "30"
        biom['gamestage_modifier'] = "1.5"
        biom['lootstage_bonus'] = "30"
        biom['lootstage_modifier'] = "1.5"
    elif choice_c == "forest":
        biom['difficulty'] = "1"
        biom['gamestage_bonus'] = "0"
        biom['gamestage_modifier'] = "0"
        biom['lootstage_bonus'] = "0"
        biom['lootstage_modifier'] = "0"
    biom = tag.find('biome', {'name': "wasteland"})
    if choice_c == "default":
        biom['difficulty'] = "5"
        biom['gamestage_bonus'] = "30"
        biom['gamestage_modifier'] = "1.5"
        biom['lootstage_bonus'] = "30"
        biom['lootstage_modifier'] = "1.5"
    elif choice_c == "wasteland":
        biom['difficulty'] = "1"
        biom['gamestage_bonus'] = "30"
        biom['gamestage_modifier'] = "1.5"
        biom['lootstage_bonus'] = "30"
        biom['lootstage_modifier'] = "1.5"
    elif choice_c == "forest":
        biom['difficulty'] = "1"
        biom['gamestage_bonus'] = "0"
        biom['gamestage_modifier'] = "0"
        biom['lootstage_bonus'] = "0"
        biom['lootstage_modifier'] = "0"
    biom = tag.find('biome', {'name': "burnt_forest"})
    if choice_c == "default":
        biom['difficulty'] = "2"
        biom['gamestage_bonus'] = "10"
        biom['gamestage_modifier'] = "0.5"
        biom['lootstage_bonus'] = "10"
        biom['lootstage_modifier'] = "0.5"
    elif choice_c == "wasteland":
        biom['difficulty'] = "1"
        biom['gamestage_bonus'] = "30"
        biom['gamestage_modifier'] = "1.5"
        biom['lootstage_bonus'] = "30"
        biom['lootstage_modifier'] = "1.5"
    elif choice_c == "forest":
        biom['difficulty'] = "1"
        biom['gamestage_bonus'] = "0"
        biom['gamestage_modifier'] = "0"
        biom['lootstage_bonus'] = "0"
        biom['lootstage_modifier'] = "0"


def adjust_lightning(bs_data_world, choice_c="default"):
    tag_world = bs_data_world.find("worldglobal")
    env = tag_world.find('environment')
    if choice_c == "default":
        prop = env.find('property', {'name': "ambientEquatorScale"})
        prop['value'] = ".7, .45"
        prop = env.find('property', {'name': "ambientGroundScale"})
        prop['value'] = ".3, .05"
        prop = env.find('property', {'name': "ambientSkyScale"})
        prop['value'] = "1, .7"
        prop = env.find('property', {'name': "ambientSkyDesat"})
        prop['value'] = ".7, .7"
        prop = env.find('property', {'name': "ambientMoon"})
        prop['value'] = ".9, .3"
        prop = env.find('property', {'name': "ambientInsideSpeed"})
        prop['value'] = ".3"
        prop = env.find('property', {'name': "ambientInsideThreshold"})
        prop['value'] = ".2"
        prop = env.find('property', {'name': "ambientInsideEquatorScale"})
        prop['value'] = ".55, 1.5"
        prop = env.find('property', {'name': "ambientInsideGroundScale"})
        prop['value'] = ".2, .2"
        prop = env.find('property', {'name': "ambientInsideSkyScale"})
        prop['value'] = ".8, .4"
        prop = env.find('property', {'name': "fogPower"})
        prop['value'] = "1, 1"
    elif choice_c == "darker":
        prop = env.find('property', {'name': "ambientEquatorScale"})
        prop['value'] = ".7, .2"
        prop = env.find('property', {'name': "ambientGroundScale"})
        prop['value'] = ".3, .025"
        prop = env.find('property', {'name': "ambientSkyScale"})
        prop['value'] = "1, .3"
        prop = env.find('property', {'name': "ambientSkyDesat"})
        prop['value'] = ".7, .3"
        prop = env.find('property', {'name': "ambientMoon"})
        prop['value'] = ".9, .1"
        prop = env.find('property', {'name': "ambientInsideSpeed"})
        prop['value'] = ".3"
        prop = env.find('property', {'name': "ambientInsideThreshold"})
        prop['value'] = ".2"
        prop = env.find('property', {'name': "ambientInsideEquatorScale"})
        prop['value'] = ".4, 0.75"
        prop = env.find('property', {'name': "ambientInsideGroundScale"})
        prop['value'] = ".2, .2"
        prop = env.find('property', {'name': "ambientInsideSkyScale"})
        prop['value'] = ".8, .3"
        prop = env.find('property', {'name': "fogPower"})
        prop['value'] = "1, 1.5"
    elif choice_c == "realistic":
        prop = env.find('property', {'name': "ambientEquatorScale"})
        prop['value'] = ".7, .025"
        prop = env.find('property', {'name': "ambientGroundScale"})
        prop['value'] = ".3, .01"
        prop = env.find('property', {'name': "ambientSkyScale"})
        prop['value'] = "1, .1"
        prop = env.find('property', {'name': "ambientSkyDesat"})
        prop['value'] = ".7, .1"
        prop = env.find('property', {'name': "ambientMoon"})
        prop['value'] = ".9, .03"
        prop = env.find('property', {'name': "ambientInsideSpeed"})
        prop['value'] = ".3"
        prop = env.find('property', {'name': "ambientInsideThreshold"})
        prop['value'] = ".2"
        prop = env.find('property', {'name': "ambientInsideEquatorScale"})
        prop['value'] = ".3, 0.4"
        prop = env.find('property', {'name': "ambientInsideGroundScale"})
        prop['value'] = ".2, .05"
        prop = env.find('property', {'name': "ambientInsideSkyScale"})
        prop['value'] = ".8, .1"
        prop = env.find('property', {'name': "fogPower"})
        prop['value'] = "1, 2"


def landscape(bs_data, wsize="large", choice_s="default", choice_c="default"):
    # global tag
    # global detail
    tag = set_tag(bs_data, tag_d="world", value=wsize)
    if choice_s == "default":
        detail = set_property(tag, "class", "lakes")
        detail = set_property(detail, "name", "scale")
        if wsize == "large":
            set_value(detail, "1, 2.2")
        elif wsize == "medium":
            set_value(detail, "1, 2")
        elif wsize == "small":
            set_value(detail, ".8, 1.5")
        elif wsize == "tiny":
            set_value(detail, ".5, .75")
        detail = set_property(tag, "class", "rivers")
        detail = set_property(detail, "name", "scale")
        if wsize == "large":
            set_value(detail, "1, 2")
        elif wsize == "medium":
            set_value(detail, "1, 2")
        elif wsize == "small":
            set_value(detail, ".8, 1.5")
        elif wsize == "tiny":
            set_value(detail, ".5, .75")
        detail = set_property(tag, "class", "craters")
        detail = set_property(detail, "name", "scale")
        if wsize == "large":
            set_value(detail, "1, 2.5")
        elif wsize == "medium":
            set_value(detail, "1, 2")
        elif wsize == "small":
            set_value(detail, ".8, 1.5")
        elif wsize == "tiny":
            set_value(detail, ".5, .75")
        detail = set_property(tag, "class", "canyons")
        detail = set_property(detail, "name", "scale")
        if wsize == "large":
            set_value(detail, "1, 2.5")
        elif wsize == "medium":
            set_value(detail, "1, 2")
        elif wsize == "small":
            set_value(detail, ".8, 1.5")
        elif wsize == "tiny":
            set_value(detail, ".5, .75")
    elif choice_s == "min":
        detail = set_property(tag, "class", "lakes")
        detail = set_property(detail, "name", "scale")
        set_value(detail, "0.5, 1")
        detail = set_property(tag, "class", "rivers")
        detail = set_property(detail, "name", "scale")
        set_value(detail, "0.5, 1")
        detail = set_property(tag, "class", "craters")
        detail = set_property(detail, "name", "scale")
        set_value(detail, "0.5, 1")
        detail = set_property(tag, "class", "canyons")
        detail = set_property(detail, "name", "scale")
        set_value(detail, "0.5, 1")
    elif choice_s == "smaller":
        detail = set_property(tag, "class", "lakes")
        detail = set_property(detail, "name", "scale")
        set_value(detail, "0.75, 1.5")
        detail = set_property(tag, "class", "rivers")
        detail = set_property(detail, "name", "scale")
        set_value(detail, "0.75, 1.5")
        detail = set_property(tag, "class", "craters")
        detail = set_property(detail, "name", "scale")
        set_value(detail, "0.75, 1.5")
        detail = set_property(tag, "class", "canyons")
        detail = set_property(detail, "name", "scale")
        set_value(detail, "0.75, 1.5")
    elif choice_s == "larger":
        detail = set_property(tag, "class", "lakes")
        detail = set_property(detail, "name", "scale")
        set_value(detail, "1, 4.5")
        detail = set_property(tag, "class", "rivers")
        detail = set_property(detail, "name", "scale")
        set_value(detail, "1, 4")
        detail = set_property(tag, "class", "craters")
        detail = set_property(detail, "name", "scale")
        set_value(detail, "1, 4.5")
        detail = set_property(tag, "class", "canyons")
        detail = set_property(detail, "name", "scale")
        set_value(detail, "1, 4")
    elif choice_s == "max":
        detail = set_property(tag, "class", "lakes")
        detail = set_property(detail, "name", "scale")
        set_value(detail, "1, 7.5")
        detail = set_property(tag, "class", "rivers")
        detail = set_property(detail, "name", "scale")
        set_value(detail, "1, 7")
        detail = set_property(tag, "class", "craters")
        detail = set_property(detail, "name", "scale")
        set_value(detail, "1, 7.5")
        detail = set_property(tag, "class", "canyons")
        detail = set_property(detail, "name", "scale")
        set_value(detail, "1, 7")
    if choice_c == "default":
        detail = set_property(tag, "class", "lakes")
        detail = set_property(detail, "name", "count")
        if wsize == "large":
            set_value(detail, "3, 6, 10")
        elif wsize == "medium":
            set_value(detail, "2, 4, 8")
        elif wsize == "small":
            set_value(detail, "2, 4, 8")
        elif wsize == "tiny":
            set_value(detail, "2, 4, 8")
        detail = set_property(tag, "class", "rivers")
        detail = set_property(detail, "name", "count")
        if wsize == "large":
            set_value(detail, "3, 6, 10")
        elif wsize == "medium":
            set_value(detail, "2, 4, 8")
        elif wsize == "small":
            set_value(detail, "2, 4, 8")
        elif wsize == "tiny":
            set_value(detail, "2, 4, 8")
        detail = set_property(tag, "class", "craters")
        detail = set_property(detail, "name", "count")
        if wsize == "large":
            set_value(detail, "3, 6, 10")
        elif wsize == "medium":
            set_value(detail, "2, 4, 8")
        elif wsize == "small":
            set_value(detail, "2, 4, 8")
        elif wsize == "tiny":
            set_value(detail, "2, 4, 8")
        detail = set_property(tag, "class", "canyons")
        detail = set_property(detail, "name", "count")
        if wsize == "large":
            set_value(detail, "3, 6, 10")
        elif wsize == "medium":
            set_value(detail, "2, 4, 8")
        elif wsize == "small":
            set_value(detail, "2, 4, 8")
        elif wsize == "tiny":
            set_value(detail, "2, 4, 8")
    elif choice_c == "min":
        detail = set_property(tag, "class", "lakes")
        detail = set_property(detail, "name", "count")
        set_value(detail, "1, 1, 1")
        detail = set_property(tag, "class", "rivers")
        detail = set_property(detail, "name", "count")
        set_value(detail, "1, 1, 1")
        detail = set_property(tag, "class", "craters")
        detail = set_property(detail, "name", "count")
        set_value(detail, "1, 1, 1")
        detail = set_property(tag, "class", "canyons")
        detail = set_property(detail, "name", "count")
        set_value(detail, "1, 1, 1")
    elif choice_c == "fewer":
        detail = set_property(tag, "class", "lakes")
        detail = set_property(detail, "name", "count")
        set_value(detail, "2, 2, 2")
        detail = set_property(tag, "class", "rivers")
        detail = set_property(detail, "name", "count")
        set_value(detail, "2, 2, 2")
        detail = set_property(tag, "class", "craters")
        detail = set_property(detail, "name", "count")
        set_value(detail, "2, 2, 2")
        detail = set_property(tag, "class", "canyons")
        detail = set_property(detail, "name", "count")
        set_value(detail, "2, 2, 2")
    elif choice_c == "more":
        detail = set_property(tag, "class", "lakes")
        detail = set_property(detail, "name", "count")
        set_value(detail, "5, 10, 15")
        detail = set_property(tag, "class", "rivers")
        detail = set_property(detail, "name", "count")
        set_value(detail, "5, 10, 15")
        detail = set_property(tag, "class", "craters")
        detail = set_property(detail, "name", "count")
        set_value(detail, "5, 10, 15")
        detail = set_property(tag, "class", "canyons")
        detail = set_property(detail, "name", "count")
        set_value(detail, "5, 10, 15")
    elif choice_c == "max":
        detail = set_property(tag, "class", "lakes")
        detail = set_property(detail, "name", "count")
        set_value(detail, "8, 15, 20")
        detail = set_property(tag, "class", "rivers")
        detail = set_property(detail, "name", "count")
        set_value(detail, "8, 15, 20")
        detail = set_property(tag, "class", "craters")
        detail = set_property(detail, "name", "count")
        set_value(detail, "8, 15, 20")
        detail = set_property(tag, "class", "canyons")
        detail = set_property(detail, "name", "count")
        set_value(detail, "8, 15, 50")


def trader2biomes(bs_data, choice="default"):
    trader1 = bs_data.find('prefab_spawn_adjust', {'partial_name': 'trader_rekt'})
    trader2 = bs_data.find('prefab_spawn_adjust', {'partial_name': 'trader_jen'})
    trader3 = bs_data.find('prefab_spawn_adjust', {'partial_name': 'trader_bob'})
    trader4 = bs_data.find('prefab_spawn_adjust', {'partial_name': 'trader_hugh'})
    trader5 = bs_data.find('prefab_spawn_adjust', {'partial_name': 'trader_joel'})
    if choice == "default":
        trader1['biomeTags'] = "forest"
        trader2['biomeTags'] = "burntforest"
        trader3['biomeTags'] = "desert"
        trader4['biomeTags'] = "snow"
        trader5['biomeTags'] = "wasteland"
    elif choice == "random":
        trader1['biomeTags'] = "forest,burntforest,desert,snow,wasteland"
        trader2['biomeTags'] = "forest,burntforest,desert,snow,wasteland"
        trader3['biomeTags'] = "forest,burntforest,desert,snow,wasteland"
        trader4['biomeTags'] = "forest,burntforest,desert,snow,wasteland"
        trader5['biomeTags'] = "forest,burntforest,desert,snow,wasteland"


def tradercount(bs_data, val=20):
    trader1 = bs_data.find('prefab_spawn_adjust', {'partial_name': 'trader_rekt'})
    trader2 = bs_data.find('prefab_spawn_adjust', {'partial_name': 'trader_jen'})
    trader3 = bs_data.find('prefab_spawn_adjust', {'partial_name': 'trader_bob'})
    trader4 = bs_data.find('prefab_spawn_adjust', {'partial_name': 'trader_hugh'})
    trader5 = bs_data.find('prefab_spawn_adjust', {'partial_name': 'trader_joel'})
    val_max = str(int(val / 5))
    if val == 5:
        trader1['min_count'] = trader2['min_count'] = trader3['min_count'] = "1"
        trader4['min_count'] = trader5['min_count'] = "1"
    elif val == 10:
        trader1['min_count'] = trader2['min_count'] = trader3['min_count'] = "1"
        trader4['min_count'] = trader5['min_count'] = "1"
    else:
        trader1['min_count'] = trader2['min_count'] = trader3['min_count'] = "2"
        trader4['min_count'] = trader5['min_count'] = "2"
    trader1['max_count'] = trader2['max_count'] = trader3['max_count'] = val_max
    trader4['max_count'] = trader5['max_count'] = val_max


def traderspecial(bs_data, townshipval="oldwest", val="false"):
    # global tag
    # global detail
    if townshipval == "all":
        tag = set_tag(bs_data, "township", "roadside")
        detail = set_property(tag, "name", "spawn_trader")
        set_value(detail, val)
        tag = set_tag(bs_data, "township", "oldwest")
        detail = set_property(tag, "name", "spawn_trader")
        set_value(detail, val)
        detail = set_property(tag, "name", "spawn_gateway")
        set_value(detail, val)
    elif townshipval == "oldwest":
        tag = set_tag(bs_data, "township", "oldwest")
        detail = set_property(tag, "name", "spawn_trader")
        set_value(detail, val)
        detail = set_property(tag, "name", "spawn_gateway")
        set_value(detail, val)
    elif townshipval == "roadside":
        tag = set_tag(bs_data, "township", "roadside")
        detail = set_property(tag, "name", "spawn_trader")
        set_value(detail, val)


def towns2biomes(bs_data, choice="default"):
    # global tag
    # global detail
    if choice == "random":
        tag = set_tag(bs_data, "township", "oldwest")
        detail = set_property(tag, "name", "biomes")
        set_value(detail, "forest,burntforest,desert,snow,wasteland")
        tag = set_tag(bs_data, "township", "forest_countrytown")
        detail = set_property(tag, "name", "biomes")
        set_value(detail, "forest,burntforest,desert,snow,wasteland")
        tag = set_tag(bs_data, "township", "bforest_countrytown")
        detail = set_property(tag, "name", "biomes")
        set_value(detail, "forest,burntforest,desert,snow,wasteland")
        tag = set_tag(bs_data, "township", "bforest_town")
        detail = set_property(tag, "name", "biomes")
        set_value(detail, "forest,burntforest,desert,snow,wasteland")
        tag = set_tag(bs_data, "township", "countrytown")
        detail = set_property(tag, "name", "biomes")
        set_value(detail, "forest,burntforest,desert,snow,wasteland")
        tag = set_tag(bs_data, "township", "town")
        detail = set_property(tag, "name", "biomes")
        set_value(detail, "forest,burntforest,desert,snow,wasteland")
        tag = set_tag(bs_data, "township", "city")
        detail = set_property(tag, "name", "biomes")
        set_value(detail, "forest,burntforest,desert,snow,wasteland")
        tag = set_tag(bs_data, "township", "wasteland_city")
        detail = set_property(tag, "name", "biomes")
        set_value(detail, "forest,burntforest,desert,snow,wasteland")
        tag = set_tag(bs_data, "township", "citybig")
        detail = set_property(tag, "name", "biomes")
        set_value(detail, "forest,burntforest,desert,snow,wasteland")
    elif choice == "optimized":
        tag = set_tag(bs_data, "township", "oldwest")
        detail = set_property(tag, "name", "biomes")
        set_value(detail, "burntforest,desert,wasteland")
        tag = set_tag(bs_data, "township", "forest_countrytown")
        detail = set_property(tag, "name", "biomes")
        set_value(detail, "forest,burntforest,desert,snow")
        tag = set_tag(bs_data, "township", "bforest_countrytown")
        detail = set_property(tag, "name", "biomes")
        set_value(detail, "burntforest,wasteland")
        tag = set_tag(bs_data, "township", "bforest_town")
        detail = set_property(tag, "name", "biomes")
        set_value(detail, "burntforest,wasteland")
        tag = set_tag(bs_data, "township", "countrytown")
        detail = set_property(tag, "name", "biomes")
        set_value(detail, "forest,burntforest,desert,snow,wasteland")
        tag = set_tag(bs_data, "township", "town")
        detail = set_property(tag, "name", "biomes")
        set_value(detail, "forest,burntforest,desert,snow,wasteland")
        tag = set_tag(bs_data, "township", "city")
        detail = set_property(tag, "name", "biomes")
        set_value(detail, "forest,burntforest,desert,snow,wasteland")
        tag = set_tag(bs_data, "township", "wasteland_city")
        detail = set_property(tag, "name", "biomes")
        set_value(detail, "wasteland")
        tag = set_tag(bs_data, "township", "citybig")
        detail = set_property(tag, "name", "biomes")
        set_value(detail, "desert,snow,wasteland")
    elif choice == "default":
        tag = set_tag(bs_data, "township", "oldwest")
        detail = set_property(tag, "name", "biomes")
        set_value(detail, "desert")
        tag = set_tag(bs_data, "township", "forest_countrytown")
        detail = set_property(tag, "name", "biomes")
        set_value(detail, "forest")
        tag = set_tag(bs_data, "township", "bforest_countrytown")
        detail = set_property(tag, "name", "biomes")
        set_value(detail, "burntforest")
        tag = set_tag(bs_data, "township", "bforest_town")
        detail = set_property(tag, "name", "biomes")
        set_value(detail, "burntforest")
        tag = set_tag(bs_data, "township", "countrytown")
        detail = set_property(tag, "name", "biomes")
        set_value(detail, "desert,snow")
        tag = set_tag(bs_data, "township", "town")
        detail = set_property(tag, "name", "biomes")
        set_value(detail, "desert,snow")
        tag = set_tag(bs_data, "township", "city")
        detail = set_property(tag, "name", "biomes")
        set_value(detail, "desert,snow")
        tag = set_tag(bs_data, "township", "wasteland_city")
        detail = set_property(tag, "name", "biomes")
        set_value(detail, "wasteland")
        tag = set_tag(bs_data, "township", "citybig")
        detail = set_property(tag, "name", "biomes")
        set_value(detail, "wasteland")
    elif choice == "no forest":
        tag = set_tag(bs_data, "township", "oldwest")
        detail = set_property(tag, "name", "biomes")
        set_value(detail, "burntforest,desert,wasteland")
        tag = set_tag(bs_data, "township", "forest_countrytown")
        detail = set_property(tag, "name", "biomes")
        set_value(detail, "burntforest,desert,snow,wasteland")
        tag = set_tag(bs_data, "township", "bforest_countrytown")
        detail = set_property(tag, "name", "biomes")
        set_value(detail, "burntforest,desert,wasteland")
        tag = set_tag(bs_data, "township", "bforest_town")
        detail = set_property(tag, "name", "biomes")
        set_value(detail, "burntforest,desert,wasteland")
        tag = set_tag(bs_data, "township", "countrytown")
        detail = set_property(tag, "name", "biomes")
        set_value(detail, "burntforest,desert,snow,wasteland")
        tag = set_tag(bs_data, "township", "town")
        detail = set_property(tag, "name", "biomes")
        set_value(detail, "burntforest,desert,snow,wasteland")
        tag = set_tag(bs_data, "township", "city")
        detail = set_property(tag, "name", "biomes")
        set_value(detail, "burntforest,desert,snow,wasteland")
        tag = set_tag(bs_data, "township", "wasteland_city")
        detail = set_property(tag, "name", "biomes")
        set_value(detail, "burntforest,desert,snow,wasteland")
        tag = set_tag(bs_data, "township", "citybig")
        detail = set_property(tag, "name", "biomes")
        set_value(detail, "burntforest,desert,snow,wasteland")


def smalltownsize(bs_data, wsize="large", choice="default"):
    # global tag
    # global detail
    tag = set_tag(bs_data, "world", wsize)
    if choice == "min":
        detail = set_property(tag, "class", "oldwest")
        detail = set_property(detail, "name", "tiles")
        set_value(detail, "1, 2")
        detail = set_property(tag, "class", "forest_countrytown")
        detail = set_property(detail, "name", "tiles")
        set_value(detail, "2, 4")
        detail = set_property(tag, "class", "bforest_countrytown")
        detail = set_property(detail, "name", "tiles")
        set_value(detail, "3, 5")
        detail = set_property(tag, "class", "bforest_town")
        detail = set_property(detail, "name", "tiles")
        set_value(detail, "4, 6")
        detail = set_property(tag, "class", "countrytown")
        detail = set_property(detail, "name", "tiles")
        set_value(detail, "3, 5")
    elif choice == "smaller":
        detail = set_property(tag, "class", "oldwest")
        detail = set_property(detail, "name", "tiles")
        set_value(detail, "1, 3")
        detail = set_property(tag, "class", "forest_countrytown")
        detail = set_property(detail, "name", "tiles")
        set_value(detail, "3, 4")
        detail = set_property(tag, "class", "bforest_countrytown")
        detail = set_property(detail, "name", "tiles")
        set_value(detail, "4, 5")
        detail = set_property(tag, "class", "bforest_town")
        detail = set_property(detail, "name", "tiles")
        set_value(detail, "5, 7")
        detail = set_property(tag, "class", "countrytown")
        detail = set_property(detail, "name", "tiles")
        set_value(detail, "4, 6")
    elif choice == "default":
        detail = set_property(tag, "class", "oldwest")
        detail = set_property(detail, "name", "tiles")
        set_value(detail, "2, 3")
        detail = set_property(tag, "class", "forest_countrytown")
        detail = set_property(detail, "name", "tiles")
        set_value(detail, "6, 6")
        detail = set_property(tag, "class", "bforest_countrytown")
        detail = set_property(detail, "name", "tiles")
        set_value(detail, "5, 6")
        detail = set_property(tag, "class", "bforest_town")
        detail = set_property(detail, "name", "tiles")
        set_value(detail, "7, 8")
        detail = set_property(tag, "class", "countrytown")
        detail = set_property(detail, "name", "tiles")
        set_value(detail, "5, 6")
    elif choice == "larger":
        detail = set_property(tag, "class", "oldwest")
        detail = set_property(detail, "name", "tiles")
        set_value(detail, "2, 4")
        detail = set_property(tag, "class", "forest_countrytown")
        detail = set_property(detail, "name", "tiles")
        set_value(detail, "6, 10")
        detail = set_property(tag, "class", "bforest_countrytown")
        detail = set_property(detail, "name", "tiles")
        set_value(detail, "5, 10")
        detail = set_property(tag, "class", "bforest_town")
        detail = set_property(detail, "name", "tiles")
        set_value(detail, "7, 15")
        detail = set_property(tag, "class", "countrytown")
        detail = set_property(detail, "name", "tiles")
        set_value(detail, "5, 10")
    elif choice == "max":
        detail = set_property(tag, "class", "oldwest")
        detail = set_property(detail, "name", "tiles")
        set_value(detail, "2, 5")
        detail = set_property(tag, "class", "forest_countrytown")
        detail = set_property(detail, "name", "tiles")
        set_value(detail, "6, 15")
        detail = set_property(tag, "class", "bforest_countrytown")
        detail = set_property(detail, "name", "tiles")
        set_value(detail, "5, 15")
        detail = set_property(tag, "class", "bforest_town")
        detail = set_property(detail, "name", "tiles")
        set_value(detail, "7, 20")
        detail = set_property(tag, "class", "countrytown")
        detail = set_property(detail, "name", "tiles")
        set_value(detail, "5, 15")


def bigtownsize(bs_data, wsize="large", choice="default"):
    tag = set_tag(bs_data, "world", wsize)
    if choice == "min":
        detail = set_property(tag, "class", "town")
        detail = set_property(detail, "name", "tiles")
        set_value(detail, "4, 6")
        detail = set_property(tag, "class", "city")
        detail = set_property(detail, "name", "tiles")
        set_value(detail, "5, 10")
        detail = set_property(tag, "class", "wasteland_city")
        detail = set_property(detail, "name", "tiles")
        set_value(detail, "5, 10")
        detail = set_property(tag, "class", "citybig")
        detail = set_property(detail, "name", "tiles")
        set_value(detail, "10, 20")
    elif choice == "smaller":
        detail = set_property(tag, "class", "town")
        detail = set_property(detail, "name", "tiles")
        set_value(detail, "5, 7")
        detail = set_property(tag, "class", "city")
        detail = set_property(detail, "name", "tiles")
        set_value(detail, "6, 8")
        detail = set_property(tag, "class", "wasteland_city")
        detail = set_property(detail, "name", "tiles")
        set_value(detail, "6, 12")
        detail = set_property(tag, "class", "citybig")
        detail = set_property(detail, "name", "tiles")
        set_value(detail, "16, 30")
    elif choice == "default":
        detail = set_property(tag, "class", "town")
        detail = set_property(detail, "name", "tiles")
        set_value(detail, "7, 8")
        detail = set_property(tag, "class", "city")
        detail = set_property(detail, "name", "tiles")
        set_value(detail, "10, 15")
        detail = set_property(tag, "class", "wasteland_city")
        detail = set_property(detail, "name", "tiles")
        set_value(detail, "7, 14")
        detail = set_property(tag, "class", "citybig")
        detail = set_property(detail, "name", "tiles")
        set_value(detail, "28, 40")
    elif choice == "larger":
        detail = set_property(tag, "class", "town")
        detail = set_property(detail, "name", "tiles")
        set_value(detail, "7, 20")
        detail = set_property(tag, "class", "city")
        detail = set_property(detail, "name", "tiles")
        set_value(detail, "10, 50")
        detail = set_property(tag, "class", "wasteland_city")
        detail = set_property(detail, "name", "tiles")
        set_value(detail, "7, 35")
        detail = set_property(tag, "class", "citybig")
        detail = set_property(detail, "name", "tiles")
        set_value(detail, "28, 120")
    elif choice == "max":
        detail = set_property(tag, "class", "town")
        detail = set_property(detail, "name", "tiles")
        set_value(detail, "7, 40")
        detail = set_property(tag, "class", "city")
        detail = set_property(detail, "name", "tiles")
        set_value(detail, "10, 150")
        detail = set_property(tag, "class", "wasteland_city")
        detail = set_property(detail, "name", "tiles")
        set_value(detail, "7, 80")
        detail = set_property(tag, "class", "citybig")
        detail = set_property(detail, "name", "tiles")
        set_value(detail, "28, 400")


def smalltowncount(bs_data, wsize="large", choice="default"):
    valchoice = ""
    tag = set_tag(bs_data, "world", wsize)
    if choice != "default":
        if choice == "more":
            valchoice = "4, 6, 8"
        elif choice == "max":
            valchoice = "5, 8, 10"
        elif choice == "fewer":
            valchoice = "2, 2, 2"
        elif choice == "min":
            valchoice = "1, 1, 1"
        detail = set_property(tag, "class", "oldwest")
        detail = set_property(detail, "name", "count")
        set_value(detail, valchoice)
        detail = set_property(tag, "class", "forest_countrytown")
        detail = set_property(detail, "name", "count")
        set_value(detail, valchoice)
        detail = set_property(tag, "class", "bforest_countrytown")
        detail = set_property(detail, "name", "count")
        set_value(detail, valchoice)
        detail = set_property(tag, "class", "bforest_town")
        detail = set_property(detail, "name", "count")
        set_value(detail, valchoice)
        detail = set_property(tag, "class", "countrytown")
        detail = set_property(detail, "name", "count")
        set_value(detail, valchoice)
    elif choice == "default" and wsize == "large":
        detail = set_property(tag, "class", "oldwest")
        detail = set_property(detail, "name", "count")
        set_value(detail, "1, 2, 3")
        detail = set_property(tag, "class", "forest_countrytown")
        detail = set_property(detail, "name", "count")
        set_value(detail, "3, 5, 7")
        detail = set_property(tag, "class", "bforest_countrytown")
        detail = set_property(detail, "name", "count")
        set_value(detail, "2, 4, 6")
        detail = set_property(tag, "class", "bforest_town")
        detail = set_property(detail, "name", "count")
        set_value(detail, "0, 1, 2")
        detail = set_property(tag, "class", "countrytown")
        detail = set_property(detail, "name", "count")
        set_value(detail, "3, 4, 6")
    elif choice == "default" and wsize == "tiny":
        detail = set_property(tag, "class", "oldwest")
        detail = set_property(detail, "name", "count")
        set_value(detail, "0, 1, 2")
        detail = set_property(tag, "class", "forest_countrytown")
        detail = set_property(detail, "name", "count")
        set_value(detail, "2, 4, 6")
        detail = set_property(tag, "class", "bforest_countrytown")
        detail = set_property(detail, "name", "count")
        set_value(detail, "2, 2, 4")
        detail = set_property(tag, "class", "bforest_town")
        detail = set_property(detail, "name", "count")
        set_value(detail, "0, 1, 2")
        detail = set_property(tag, "class", "countrytown")
        detail = set_property(detail, "name", "count")
        set_value(detail, "2, 2, 3")
    elif choice == "default" and wsize == "small":
        detail = set_property(tag, "class", "oldwest")
        detail = set_property(detail, "name", "count")
        set_value(detail, "0, 1, 2")
        detail = set_property(tag, "class", "forest_countrytown")
        detail = set_property(detail, "name", "count")
        set_value(detail, "2, 4, 6")
        detail = set_property(tag, "class", "bforest_countrytown")
        detail = set_property(detail, "name", "count")
        set_value(detail, "2, 2, 4")
        detail = set_property(tag, "class", "bforest_town")
        detail = set_property(detail, "name", "count")
        set_value(detail, "0, 1, 2")
        detail = set_property(tag, "class", "countrytown")
        detail = set_property(detail, "name", "count")
        set_value(detail, "2, 2, 3")
    elif choice == "default" and wsize == "medium":
        detail = set_property(tag, "class", "oldwest")
        detail = set_property(detail, "name", "count")
        set_value(detail, "0, 1, 2")
        detail = set_property(tag, "class", "forest_countrytown")
        detail = set_property(detail, "name", "count")
        set_value(detail, "2, 4, 6")
        detail = set_property(tag, "class", "bforest_countrytown")
        detail = set_property(detail, "name", "count")
        set_value(detail, "2, 3, 5")
        detail = set_property(tag, "class", "bforest_town")
        detail = set_property(detail, "name", "count")
        set_value(detail, "0, 1, 2")
        detail = set_property(tag, "class", "countrytown")
        detail = set_property(detail, "name", "count")
        set_value(detail, "2, 2, 3")


def bigtowncount(bs_data, wsize="large", choice="default"):
    valchoice = ""
    tag = set_tag(bs_data, "world", wsize)
    if choice != "default":
        if choice == "more":
            valchoice = "4, 6, 8"
        elif choice == "max":
            valchoice = "5, 8, 10"
        elif choice == "fewer":
            valchoice = "2, 2, 2"
        elif choice == "min":
            valchoice = "1, 1, 1"
        detail = set_property(tag, "class", "town")
        detail = set_property(detail, "name", "count")
        set_value(detail, valchoice)
        detail = set_property(tag, "class", "city")
        detail = set_property(detail, "name", "count")
        set_value(detail, valchoice)
        detail = set_property(tag, "class", "wasteland_city")
        detail = set_property(detail, "name", "count")
        set_value(detail, valchoice)
        detail = set_property(tag, "class", "citybig")
        detail = set_property(detail, "name", "count")
        set_value(detail, valchoice)
    elif choice == "default" and wsize == "large":
        detail = set_property(tag, "class", "town")
        detail = set_property(detail, "name", "count")
        set_value(detail, "2, 3, 5")
        detail = set_property(tag, "class", "city")
        detail = set_property(detail, "name", "count")
        set_value(detail, "2, 3, 5")
        detail = set_property(tag, "class", "wasteland_city")
        detail = set_property(detail, "name", "count")
        set_value(detail, "2, 3, 4")
        detail = set_property(tag, "class", "citybig")
        detail = set_property(detail, "name", "count")
        set_value(detail, "1, 2, 3")
    elif choice == "default" and wsize == "tiny":
        detail = set_property(tag, "class", "town")
        detail = set_property(detail, "name", "count")
        set_value(detail, "1, 1, 3")
        detail = set_property(tag, "class", "city")
        detail = set_property(detail, "name", "count")
        set_value(detail, "1, 2, 3")
        detail = set_property(tag, "class", "wasteland_city")
        detail = set_property(detail, "name", "count")
        set_value(detail, "1, 2, 3")
        detail = set_property(tag, "class", "citybig")
        detail = set_property(detail, "name", "count")
        set_value(detail, "0, 1, 1")
    elif choice == "default" and wsize == "small":
        detail = set_property(tag, "class", "town")
        detail = set_property(detail, "name", "count")
        set_value(detail, "1, 1, 3")
        detail = set_property(tag, "class", "city")
        detail = set_property(detail, "name", "count")
        set_value(detail, "1, 2, 3")
        detail = set_property(tag, "class", "wasteland_city")
        detail = set_property(detail, "name", "count")
        set_value(detail, "1, 2, 3")
        detail = set_property(tag, "class", "citybig")
        detail = set_property(detail, "name", "count")
        set_value(detail, "0, 1, 1")
    elif choice == "default" and wsize == "medium":
        detail = set_property(tag, "class", "town")
        detail = set_property(detail, "name", "count")
        set_value(detail, "1, 2, 4")
        detail = set_property(tag, "class", "city")
        detail = set_property(detail, "name", "count")
        set_value(detail, "1, 2, 4")
        detail = set_property(tag, "class", "wasteland_city")
        detail = set_property(detail, "name", "count")
        set_value(detail, "2, 3, 4")
        detail = set_property(tag, "class", "citybig")
        detail = set_property(detail, "name", "count")
        set_value(detail, "0, 1, 2")


def townrandomizer(bs_data, choice="default"):
    if choice == "optimized":
        randomizer_val = "0.5"
        tag = set_tag(bs_data, "district", "countrytown")
        detail = set_property(tag, "name", "district_spawn_weight")
        set_value(detail, randomizer_val)
        detail = set_property(tag, "name", "district_required_township")
        set_value(detail, "countrytown,forest_countrytown,bforest_countrytown")
        tag = set_tag(bs_data, "district", "countryresidential")
        detail = set_property(tag, "name", "district_spawn_weight")
        set_value(detail, randomizer_val)
        detail = set_property(tag, "name", "district_required_township")
        set_value(detail, "countrytown,forest_countrytown,bforest_countrytown")
        tag = set_tag(bs_data, "district", "commercial")
        detail = set_property(tag, "name", "district_spawn_weight")
        set_value(detail, randomizer_val)
        detail = set_property(tag, "name", "district_required_township")
        set_value(detail, "citybig,wasteland_city,city,town,bforest_town")
        tag = set_tag(bs_data, "district", "industrial")
        detail = set_property(tag, "name", "district_spawn_weight")
        set_value(detail, randomizer_val)
        detail = set_property(tag, "name", "district_required_township")
        set_value(detail, "citybig,wasteland_city,city,town,bforest_town")
        tag = set_tag(bs_data, "district", "residential")
        detail = set_property(tag, "name", "district_spawn_weight")
        set_value(detail, randomizer_val)
        detail = set_property(tag, "name", "district_required_township")
        set_value(detail, "citybig,wasteland_city,city,town,bforest_town")
        tag = set_tag(bs_data, "district", "downtown")
        detail = set_property(tag, "name", "district_spawn_weight")
        set_value(detail, randomizer_val)
        detail = set_property(tag, "name", "district_required_township")
        set_value(detail, "citybig,wasteland_city,city")
        tag = set_tag(bs_data, "district", "oldwest")
        detail = set_property(tag, "name", "district_spawn_weight")
        set_value(detail, "1")
        detail = set_property(tag, "name", "district_required_township")
        set_value(detail, "oldwest")
    elif choice == "chaos":
        randomizer_val = "0.75"
        tag = set_tag(bs_data, "district", "countrytown")
        detail = set_property(tag, "name", "district_spawn_weight")
        set_value(detail, randomizer_val)
        detail = set_property(tag, "name", "district_required_township")
        set_value(detail, "countrytown,forest_countrytown,bforest_countrytown,citybig,wasteland_city,city,oldwest")
        tag = set_tag(bs_data, "district", "countryresidential")
        detail = set_property(tag, "name", "district_spawn_weight")
        set_value(detail, randomizer_val)
        detail = set_property(tag, "name", "district_required_township")
        set_value(detail, "countrytown,forest_countrytown,bforest_countrytown,citybig,wasteland_city,city,oldwest")
        tag = set_tag(bs_data, "district", "commercial")
        detail = set_property(tag, "name", "district_spawn_weight")
        set_value(detail, randomizer_val)
        detail = set_property(tag, "name", "district_required_township")
        set_value(detail, "countrytown,forest_countrytown,bforest_countrytown,citybig,wasteland_city,city,oldwest")
        tag = set_tag(bs_data, "district", "industrial")
        detail = set_property(tag, "name", "district_spawn_weight")
        set_value(detail, randomizer_val)
        detail = set_property(tag, "name", "district_required_township")
        set_value(detail, "countrytown,forest_countrytown,bforest_countrytown,citybig,wasteland_city,city,oldwest")
        tag = set_tag(bs_data, "district", "residential")
        detail = set_property(tag, "name", "district_spawn_weight")
        set_value(detail, randomizer_val)
        detail = set_property(tag, "name", "district_required_township")
        set_value(detail, "countrytown,forest_countrytown,bforest_countrytown,citybig,wasteland_city,city,oldwest")
        tag = set_tag(bs_data, "district", "downtown")
        detail = set_property(tag, "name", "district_spawn_weight")
        set_value(detail, randomizer_val)
        detail = set_property(tag, "name", "district_required_township")
        set_value(detail, "countrytown,forest_countrytown,bforest_countrytown,citybig,wasteland_city,city,oldwest")
        tag = set_tag(bs_data, "district", "oldwest")
        detail = set_property(tag, "name", "district_spawn_weight")
        set_value(detail, randomizer_val)
        detail = set_property(tag, "name", "district_required_township")
        set_value(detail, "countrytown,forest_countrytown,bforest_countrytown,citybig,wasteland_city,city,oldwest")
    elif choice == "default":
        tag = set_tag(bs_data, "district", "countrytown")
        detail = set_property(tag, "name", "district_spawn_weight")
        set_value(detail, "0.5")
        detail = set_property(tag, "name", "district_required_township")
        set_value(detail, "countrytown,forest_countrytown,bforest_countrytown")
        tag = set_tag(bs_data, "district", "countryresidential")
        detail = set_property(tag, "name", "district_spawn_weight")
        set_value(detail, "1")
        detail = set_property(tag, "name", "district_required_township")
        set_value(detail, "countrytown,forest_countrytown,bforest_countrytown")
        tag = set_tag(bs_data, "district", "commercial")
        detail = set_property(tag, "name", "district_spawn_weight")
        set_value(detail, "0.4")
        detail = set_property(tag, "name", "district_required_township")
        set_value(detail, "citybig,wasteland_city,city,town,bforest_town")
        tag = set_tag(bs_data, "district", "industrial")
        detail = set_property(tag, "name", "district_spawn_weight")
        set_value(detail, "0.2")
        detail = set_property(tag, "name", "district_required_township")
        set_value(detail, "citybig,wasteland_city,city,town,bforest_town")
        tag = set_tag(bs_data, "district", "residential")
        detail = set_property(tag, "name", "district_spawn_weight")
        set_value(detail, "0.5")
        detail = set_property(tag, "name", "district_required_township")
        set_value(detail, "citybig,wasteland_city,city,town,bforest_town")
        tag = set_tag(bs_data, "district", "downtown")
        detail = set_property(tag, "name", "district_spawn_weight")
        set_value(detail, "0.3")
        detail = set_property(tag, "name", "district_required_township")
        set_value(detail, "citybig,wasteland_city,city")
        tag = set_tag(bs_data, "district", "oldwest")
        detail = set_property(tag, "name", "district_spawn_weight")
        set_value(detail, "1")
        detail = set_property(tag, "name", "district_required_township")
        set_value(detail, "oldwest")


def districtcolors(bs_data, choice="optimized"):
    if choice == "optimized":
        tag = set_tag(bs_data, "district", "countrytown")
        detail = set_property(tag, "name", "preview_color")
        set_value(detail, "0,0,1")
        tag = set_tag(bs_data, "district", "countryresidential")
        detail = set_property(tag, "name", "preview_color")
        set_value(detail, "0,1,0")
        tag = set_tag(bs_data, "district", "commercial")
        detail = set_property(tag, "name", "preview_color")
        set_value(detail, "0,1,1")
        tag = set_tag(bs_data, "district", "industrial")
        detail = set_property(tag, "name", "preview_color")
        set_value(detail, "1,0,0")
        tag = set_tag(bs_data, "district", "residential")
        detail = set_property(tag, "name", "preview_color")
        set_value(detail, "1,0,1")
        tag = set_tag(bs_data, "district", "rural")
        detail = set_property(tag, "name", "preview_color")
        set_value(detail, "1,1,0")
        tag = set_tag(bs_data, "district", "downtown")
        detail = set_property(tag, "name", "preview_color")
        set_value(detail, "0,0,0")
        tag = set_tag(bs_data, "district", "oldwest")
        detail = set_property(tag, "name", "preview_color")
        set_value(detail, "0,0,1")
        tag = set_tag(bs_data, "district", "gateway")
        detail = set_property(tag, "name", "preview_color")
        set_value(detail, "0.5,0.5,0.5")
    elif choice == "default":
        tag = set_tag(bs_data, "district", "countrytown")
        detail = set_property(tag, "name", "preview_color")
        set_value(detail, "0,0,1")
        tag = set_tag(bs_data, "district", "countryresidential")
        detail = set_property(tag, "name", "preview_color")
        set_value(detail, "0,1,0")
        tag = set_tag(bs_data, "district", "commercial")
        detail = set_property(tag, "name", "preview_color")
        set_value(detail, "0,0,1")
        tag = set_tag(bs_data, "district", "industrial")
        detail = set_property(tag, "name", "preview_color")
        set_value(detail, "1,1,0")
        tag = set_tag(bs_data, "district", "residential")
        detail = set_property(tag, "name", "preview_color")
        set_value(detail, "0,1,0")
        tag = set_tag(bs_data, "district", "rural")
        detail = set_property(tag, "name", "preview_color")
        set_value(detail, "0,1,1")
        tag = set_tag(bs_data, "district", "downtown")
        detail = set_property(tag, "name", "preview_color")
        set_value(detail, "0.5,0.5,0.5")
        tag = set_tag(bs_data, "district", "oldwest")
        detail = set_property(tag, "name", "preview_color")
        set_value(detail, "0.5,0.5,0.1")
        tag = set_tag(bs_data, "district", "gateway")
        detail = set_property(tag, "name", "preview_color")
        set_value(detail, "0.5,0.5,0.1")


def weatherprocessing(bs_data, choice="default"):
    if choice == "default":
        adjust_temp(bs_data, biom_c='snow', weather_c='default', temp_min='26', temp_max='32')
        adjust_temp(bs_data, biom_c='snow', weather_c='fog', temp_min='20', temp_max='30')
        adjust_temp(bs_data, biom_c='snow', weather_c='snow', temp_min='18', temp_max='28')
        adjust_temp(bs_data, biom_c='snow', weather_c='storm', temp_min='12', temp_max='28')
        adjust_weather_prob(bs_data, biom_c='snow', weather_c='default', prob_c='44')
        adjust_weather_prob(bs_data, biom_c='snow', weather_c='fog', prob_c='8')
        adjust_weather_prob(bs_data, biom_c='snow', weather_c='snow', prob_c='40')
        adjust_weather_prob(bs_data, biom_c='snow', weather_c='storm', prob_c='8')
        adjust_temp(bs_data, biom_c='pine_forest', weather_c='default', temp_min='65', temp_max='70')
        adjust_temp(bs_data, biom_c='pine_forest', weather_c='fog', temp_min='65', temp_max='70')
        adjust_temp(bs_data, biom_c='pine_forest', weather_c='rain', temp_min='65', temp_max='70')
        adjust_temp(bs_data, biom_c='pine_forest', weather_c='storm', temp_min='65', temp_max='70')
        adjust_weather_prob(bs_data, biom_c='pine_forest', weather_c='default', prob_c='88')
        adjust_weather_prob(bs_data, biom_c='pine_forest', weather_c='fog', prob_c='5')
        adjust_weather_prob(bs_data, biom_c='pine_forest', weather_c='rain', prob_c='4')
        adjust_weather_prob(bs_data, biom_c='pine_forest', weather_c='storm', prob_c='3')
        adjust_temp(bs_data, biom_c='desert', weather_c='default', temp_min='95', temp_max='105')
        adjust_temp(bs_data, biom_c='desert', weather_c='rain', temp_min='95', temp_max='105')
        adjust_temp(bs_data, biom_c='desert', weather_c='storm', temp_min='95', temp_max='105')
        adjust_weather_prob(bs_data, biom_c='desert', weather_c='default', prob_c='94')
        adjust_weather_prob(bs_data, biom_c='desert', weather_c='rain', prob_c='3')
        adjust_weather_prob(bs_data, biom_c='desert', weather_c='storm', prob_c='3')
        adjust_temp(bs_data, biom_c='water', weather_c='default', temp_min='70', temp_max='70')
        adjust_temp(bs_data, biom_c='onlyWater', weather_c='default', temp_min='70', temp_max='70')
        adjust_temp(bs_data, biom_c='wasteland', weather_c='default', temp_min='50', temp_max='90')
        adjust_temp(bs_data, biom_c='wasteland', weather_c='snow', temp_min='26', temp_max='32')
        adjust_temp(bs_data, biom_c='wasteland', weather_c='rain', temp_min='50', temp_max='90')
        adjust_temp(bs_data, biom_c='wasteland', weather_c='storm', temp_min='50', temp_max='90')
        adjust_weather_prob(bs_data, biom_c='wasteland', weather_c='default', prob_c='83')
        adjust_weather_prob(bs_data, biom_c='wasteland', weather_c='snow', prob_c='0')
        adjust_weather_prob(bs_data, biom_c='wasteland', weather_c='rain', prob_c='10')
        adjust_weather_prob(bs_data, biom_c='wasteland', weather_c='storm', prob_c='7')
        adjust_temp(bs_data, biom_c='burnt_forest', weather_c='default', temp_min='75', temp_max='85')
        adjust_temp(bs_data, biom_c='burnt_forest', weather_c='rain', temp_min='75', temp_max='85')
        adjust_temp(bs_data, biom_c='burnt_forest', weather_c='storm', temp_min='75', temp_max='85')
        adjust_weather_prob(bs_data, biom_c='burnt_forest', weather_c='default', prob_c='86')
        adjust_weather_prob(bs_data, biom_c='burnt_forest', weather_c='rain', prob_c='8')
        adjust_weather_prob(bs_data, biom_c='burnt_forest', weather_c='storm', prob_c='6')
    elif choice == "basic":
        adjust_temp(bs_data, biom_c='snow', weather_c='default', temp_min='-30', temp_max='-20')
        adjust_temp(bs_data, biom_c='snow', weather_c='fog', temp_min='-34', temp_max='-24')
        adjust_temp(bs_data, biom_c='snow', weather_c='snow', temp_min='-38', temp_max='-28')
        adjust_temp(bs_data, biom_c='snow', weather_c='storm', temp_min='-42', temp_max='-32')
        adjust_weather_prob(bs_data, biom_c='snow', weather_c='default', prob_c='43')
        adjust_weather_prob(bs_data, biom_c='snow', weather_c='fog', prob_c='7')
        adjust_weather_prob(bs_data, biom_c='snow', weather_c='snow', prob_c='40')
        adjust_weather_prob(bs_data, biom_c='snow', weather_c='storm', prob_c='10')
        adjust_temp(bs_data, biom_c='pine_forest', weather_c='default', temp_min='65', temp_max='70')
        adjust_temp(bs_data, biom_c='pine_forest', weather_c='fog', temp_min='-20', temp_max='-10')
        adjust_temp(bs_data, biom_c='pine_forest', weather_c='rain', temp_min='65', temp_max='70')
        adjust_temp(bs_data, biom_c='pine_forest', weather_c='storm', temp_min='65', temp_max='70')
        adjust_weather_prob(bs_data, biom_c='pine_forest', weather_c='default', prob_c='75')
        adjust_weather_prob(bs_data, biom_c='pine_forest', weather_c='fog', prob_c='5')
        adjust_weather_prob(bs_data, biom_c='pine_forest', weather_c='rain', prob_c='15')
        adjust_weather_prob(bs_data, biom_c='pine_forest', weather_c='storm', prob_c='5')
        adjust_temp(bs_data, biom_c='desert', weather_c='default', temp_min='160', temp_max='180')
        adjust_temp(bs_data, biom_c='desert', weather_c='rain', temp_min='140', temp_max='160')
        adjust_temp(bs_data, biom_c='desert', weather_c='storm', temp_min='130', temp_max='150')
        adjust_weather_prob(bs_data, biom_c='desert', weather_c='default', prob_c='92')
        adjust_weather_prob(bs_data, biom_c='desert', weather_c='rain', prob_c='4')
        adjust_weather_prob(bs_data, biom_c='desert', weather_c='storm', prob_c='4')
        adjust_temp(bs_data, biom_c='water', weather_c='default', temp_min='-25', temp_max='-20')
        adjust_temp(bs_data, biom_c='onlyWater', weather_c='default', temp_min='-25', temp_max='-20')
        adjust_temp(bs_data, biom_c='wasteland', weather_c='default', temp_min='145', temp_max='160')
        adjust_temp(bs_data, biom_c='wasteland', weather_c='snow', temp_min='-25', temp_max='-20')
        adjust_temp(bs_data, biom_c='wasteland', weather_c='rain', temp_min='50', temp_max='90')
        adjust_temp(bs_data, biom_c='wasteland', weather_c='storm', temp_min='50', temp_max='90')
        adjust_weather_prob(bs_data, biom_c='wasteland', weather_c='default', prob_c='75')
        adjust_weather_prob(bs_data, biom_c='wasteland', weather_c='snow', prob_c='5')
        adjust_weather_prob(bs_data, biom_c='wasteland', weather_c='rain', prob_c='10')
        adjust_weather_prob(bs_data, biom_c='wasteland', weather_c='storm', prob_c='10')
        adjust_temp(bs_data, biom_c='burnt_forest', weather_c='default', temp_min='146', temp_max='164')
        adjust_temp(bs_data, biom_c='burnt_forest', weather_c='rain', temp_min='120', temp_max='140')
        adjust_temp(bs_data, biom_c='burnt_forest', weather_c='storm', temp_min='110', temp_max='130')
        adjust_weather_prob(bs_data, biom_c='burnt_forest', weather_c='default', prob_c='80')
        adjust_weather_prob(bs_data, biom_c='burnt_forest', weather_c='rain', prob_c='11')
        adjust_weather_prob(bs_data, biom_c='burnt_forest', weather_c='storm', prob_c='9')
    elif choice == "realistic":
        adjust_temp(bs_data, biom_c='snow', weather_c='default', temp_min='-40', temp_max='-30')
        adjust_temp(bs_data, biom_c='snow', weather_c='fog', temp_min='-44', temp_max='-33')
        adjust_temp(bs_data, biom_c='snow', weather_c='snow', temp_min='-50', temp_max='-40')
        adjust_temp(bs_data, biom_c='snow', weather_c='storm', temp_min='-80', temp_max='-50')
        adjust_weather_prob(bs_data, biom_c='snow', weather_c='default', prob_c='43')
        adjust_weather_prob(bs_data, biom_c='snow', weather_c='fog', prob_c='7')
        adjust_weather_prob(bs_data, biom_c='snow', weather_c='snow', prob_c='40')
        adjust_weather_prob(bs_data, biom_c='snow', weather_c='storm', prob_c='10')
        adjust_temp(bs_data, biom_c='pine_forest', weather_c='default', temp_min='65', temp_max='70')
        adjust_temp(bs_data, biom_c='pine_forest', weather_c='fog', temp_min='-25', temp_max='-20')
        adjust_temp(bs_data, biom_c='pine_forest', weather_c='rain', temp_min='65', temp_max='70')
        adjust_temp(bs_data, biom_c='pine_forest', weather_c='storm', temp_min='65', temp_max='70')
        adjust_weather_prob(bs_data, biom_c='pine_forest', weather_c='default', prob_c='75')
        adjust_weather_prob(bs_data, biom_c='pine_forest', weather_c='fog', prob_c='5')
        adjust_weather_prob(bs_data, biom_c='pine_forest', weather_c='rain', prob_c='15')
        adjust_weather_prob(bs_data, biom_c='pine_forest', weather_c='storm', prob_c='5')
        adjust_temp(bs_data, biom_c='desert', weather_c='default', temp_min='180', temp_max='200')
        adjust_temp(bs_data, biom_c='desert', weather_c='rain', temp_min='150', temp_max='170')
        adjust_temp(bs_data, biom_c='desert', weather_c='storm', temp_min='140', temp_max='160')
        adjust_weather_prob(bs_data, biom_c='desert', weather_c='default', prob_c='92')
        adjust_weather_prob(bs_data, biom_c='desert', weather_c='rain', prob_c='4')
        adjust_weather_prob(bs_data, biom_c='desert', weather_c='storm', prob_c='4')
        adjust_temp(bs_data, biom_c='water', weather_c='default', temp_min='-25', temp_max='-20')
        adjust_temp(bs_data, biom_c='onlyWater', weather_c='default', temp_min='-25', temp_max='-20')
        adjust_temp(bs_data, biom_c='wasteland', weather_c='default', temp_min='155', temp_max='170')
        adjust_temp(bs_data, biom_c='wasteland', weather_c='snow', temp_min='-34', temp_max='-27')
        adjust_temp(bs_data, biom_c='wasteland', weather_c='rain', temp_min='50', temp_max='90')
        adjust_temp(bs_data, biom_c='wasteland', weather_c='storm', temp_min='50', temp_max='90')
        adjust_weather_prob(bs_data, biom_c='wasteland', weather_c='default', prob_c='75')
        adjust_weather_prob(bs_data, biom_c='wasteland', weather_c='snow', prob_c='5')
        adjust_weather_prob(bs_data, biom_c='wasteland', weather_c='rain', prob_c='10')
        adjust_weather_prob(bs_data, biom_c='wasteland', weather_c='storm', prob_c='10')
        adjust_temp(bs_data, biom_c='burnt_forest', weather_c='default', temp_min='160', temp_max='175')
        adjust_temp(bs_data, biom_c='burnt_forest', weather_c='rain', temp_min='140', temp_max='155')
        adjust_temp(bs_data, biom_c='burnt_forest', weather_c='storm', temp_min='135', temp_max='150')
        adjust_weather_prob(bs_data, biom_c='burnt_forest', weather_c='default', prob_c='80')
        adjust_weather_prob(bs_data, biom_c='burnt_forest', weather_c='rain', prob_c='11')
        adjust_weather_prob(bs_data, biom_c='burnt_forest', weather_c='storm', prob_c='9')
    elif choice == "apocalypse":
        adjust_temp(bs_data, biom_c='snow', weather_c='default', temp_min='-41', temp_max='-32')
        adjust_temp(bs_data, biom_c='snow', weather_c='fog', temp_min='-45', temp_max='-34')
        adjust_temp(bs_data, biom_c='snow', weather_c='snow', temp_min='-52', temp_max='-42')
        adjust_temp(bs_data, biom_c='snow', weather_c='storm', temp_min='-83', temp_max='-53')
        adjust_weather_prob(bs_data, biom_c='snow', weather_c='default', prob_c='30')
        adjust_weather_prob(bs_data, biom_c='snow', weather_c='fog', prob_c='10')
        adjust_weather_prob(bs_data, biom_c='snow', weather_c='snow', prob_c='40')
        adjust_weather_prob(bs_data, biom_c='snow', weather_c='storm', prob_c='20')
        adjust_temp(bs_data, biom_c='pine_forest', weather_c='default', temp_min='65', temp_max='70')
        adjust_temp(bs_data, biom_c='pine_forest', weather_c='fog', temp_min='-25', temp_max='-20')
        adjust_temp(bs_data, biom_c='pine_forest', weather_c='rain', temp_min='65', temp_max='70')
        adjust_temp(bs_data, biom_c='pine_forest', weather_c='storm', temp_min='65', temp_max='70')
        adjust_weather_prob(bs_data, biom_c='pine_forest', weather_c='default', prob_c='55')
        adjust_weather_prob(bs_data, biom_c='pine_forest', weather_c='fog', prob_c='10')
        adjust_weather_prob(bs_data, biom_c='pine_forest', weather_c='rain', prob_c='25')
        adjust_weather_prob(bs_data, biom_c='pine_forest', weather_c='storm', prob_c='10')
        adjust_temp(bs_data, biom_c='desert', weather_c='default', temp_min='180', temp_max='200')
        adjust_temp(bs_data, biom_c='desert', weather_c='rain', temp_min='165', temp_max='175')
        adjust_temp(bs_data, biom_c='desert', weather_c='storm', temp_min='155', temp_max='165')
        adjust_weather_prob(bs_data, biom_c='desert', weather_c='default', prob_c='90')
        adjust_weather_prob(bs_data, biom_c='desert', weather_c='rain', prob_c='5')
        adjust_weather_prob(bs_data, biom_c='desert', weather_c='storm', prob_c='5')
        adjust_temp(bs_data, biom_c='water', weather_c='default', temp_min='-25', temp_max='-20')
        adjust_temp(bs_data, biom_c='onlyWater', weather_c='default', temp_min='-25', temp_max='-20')
        adjust_temp(bs_data, biom_c='wasteland', weather_c='default', temp_min='155', temp_max='170')
        adjust_temp(bs_data, biom_c='wasteland', weather_c='snow', temp_min='-34', temp_max='-27')
        adjust_temp(bs_data, biom_c='wasteland', weather_c='rain', temp_min='150', temp_max='165')
        adjust_temp(bs_data, biom_c='wasteland', weather_c='storm', temp_min='150', temp_max='165')
        adjust_weather_prob(bs_data, biom_c='wasteland', weather_c='default', prob_c='65')
        adjust_weather_prob(bs_data, biom_c='wasteland', weather_c='snow', prob_c='10')
        adjust_weather_prob(bs_data, biom_c='wasteland', weather_c='rain', prob_c='10')
        adjust_weather_prob(bs_data, biom_c='wasteland', weather_c='storm', prob_c='15')
        adjust_temp(bs_data, biom_c='burnt_forest', weather_c='default', temp_min='165', temp_max='180')
        adjust_temp(bs_data, biom_c='burnt_forest', weather_c='rain', temp_min='160', temp_max='175')
        adjust_temp(bs_data, biom_c='burnt_forest', weather_c='storm', temp_min='160', temp_max='175')
        adjust_weather_prob(bs_data, biom_c='burnt_forest', weather_c='default', prob_c='65')
        adjust_weather_prob(bs_data, biom_c='burnt_forest', weather_c='rain', prob_c='20')
        adjust_weather_prob(bs_data, biom_c='burnt_forest', weather_c='storm', prob_c='15')


tier1 = ['farm_12', 'cabin_12', 'funeral_home_01', 'oldwest_business_04', 'oldwest_coal_factory', 'fastfood_05',
         'oldwest_strip_03', 'oldwest_business_01', 'oldwest_business_02', 'lot_country_01', 'fastfood_03',
         'countrytown_business_10', 'diner_02', 'store_grocery_05', 'house_modern_10', 'rest_area_04', 'bar_01',
         'survivor_site_11', 'survivor_site_01', 'survivor_site_07', 'survivor_site_04', 'survivor_site_09',
         'downtown_filler_09', 'oldwest_business_12', 'rest_area_03', 'diner_03',
         'house_construction_04', 'diner_04', 'store_laundry_01', 'survivor_site_10', 'office_01', 'fastfood_04',
         'oldwest_business_03', 'oldwest_church', 'house_construction_03', 'cave_04', 'survivor_site_06',
         'trailer_park_01', 'fastfood_02', 'house_old_mansard_05', 'utility_substation_03', 'gas_station_11',
         'store_grocery_06', 'cabin_08', 'radio_station_03', 'oldwest_business_14', 'cabin_02',
         'cemetery_01', 'survivor_site_05', 'oldwest_strip_04', 'store_grocery_04', 'store_electronics_01',
         'motel_05',
         'motel_02', 'cave_03', 'church_sm_01', 'cabin_11', 'church_02', 'lot_vacant_05', 'parking_lot_01',
         'gas_station_01', 'gas_station_02', 'gas_station_03', 'gas_station_04', 'gas_station_07', 'gas_station_08',
         'gas_station_09', 'gas_station_10', 'cave_02', 'school_daycare_01', 'store_pharmacy_01', 'fastfood_01',
         'survivor_site_03', 'ranger_station_02', 'ranger_station_03', 'ranger_station_04', 'ranger_station_05',
         'oldwest_business_10', 'cabin_06', 'house_modern_25', 'lot_country_02', 'cabin_05', 'oldwest_business_11',
         'cabin_09', 'house_old_modular_07', 'oldwest_business_06', 'cave_01', 'oldwest_business_13',
         'house_modern_20',
         'cabin_16', 'cabin_14', 'house_old_modular_06', 'house_old_bungalow_10', 'countrytown_business_13',
         'house_old_modular_08', 'house_modern_12', 'house_old_modular_05', 'diner_01', 'house_modern_13',
         'house_burnt_03', 'house_old_victorian_08', 'cabin_10', 'house_old_ranch_10', 'house_burnt_01',
         'house_old_victorian_05', 'house_old_bungalow_09', 'cabin_15', 'house_old_modular_01',
         'house_old_bungalow_12',
         'house_old_pyramid_05', 'house_old_gambrel_02', 'house_construction_01', 'survivor_site_08',
         'survivor_site_02', 'cabin_07', 'house_old_ranch_01', 'house_old_tudor_02',
         'oldwest_business_08', 'house_country_01', 'cabin_04', 'cabin_01']
tier2 = ['house_old_bungalow_06', 'auto_mechanic_01', 'countrytown_business_04', 'farm_04', 'bombshelter_01',
         'rural_outdoor_wedding_01', 'house_old_gambrel_04', 'countrytown_business_01', 'downtown_building_04',
         'warehouse_04', 'barn_03', 'downtown_building_05', 'body_shop_01', 'store_book_01',
         'cemetery_02', 'downtown_business_07', 'downtown_parking_lot_01', 'post_office_01', 'downtown_filler_15',
         'oldwest_strip_01', 'utility_electric_co_01', 'commercial_strip_07', 'countrytown_business_02',
         'house_old_bungalow_07', 'fire_station_01', 'school_daycare_03', 'countrytown_business_14', 'farm_14',
         'office_03', 'house_old_bungalow_03', 'farm_03', 'utility_substation_02', 'farm_01', 'carlot_01',
         'downtown_filler_01', 'downtown_filler_13', 'store_bakery_01', 'countrytown_business_07', 'barn_02',
         'farm_17',
         'remnant_waste_05', 'store_electronics_02', 'parking_lot_02', 'oldwest_strip_02', 'parking_garage_03',
         'business_burnt_02', 'fastfood_07', 'fire_station_04', 'motel_01', 'business_burnt_01',
         'store_autoparts_01',
         'cabin_18', 'industrial_business_08', 'bank_01', 'downtown_filler_14', 'house_old_tudor_04',
         'ranger_station_06', 'farm_10', 'countrytown_business_06', 'office_02', 'commercial_strip_01',
         'store_grocery_01', 'apartments_05', 'office_04', 'farm_11', 'commercial_strip_04', 'downtown_business_06',
         'farm_08', 'house_old_bungalow_02', 'house_modern_19', 'house_old_modular_03', 'house_old_tudor_01',
         'house_modern_06', 'house_modern_14', 'house_old_mansard_01', 'house_old_ranch_07', 'apartments_04',
         'house_modern_15', 'house_burnt_05', 'house_old_pyramid_03', 'house_modern_08', 'house_old_victorian_10',
         'house_modern_03', 'cabin_17', 'house_modern_04', 'house_old_ranch_08', 'cabin_13', 'house_old_ranch_03',
         'cabin_03', 'house_modern_16', 'house_old_gambrel_01', 'house_old_ranch_11', 'house_old_ranch_06',
         'house_old_ranch_04', 'house_modern_22', 'house_old_bungalow_05', 'house_old_victorian_12',
         'house_old_victorian_02', 'house_old_ranch_09', 'house_old_pyramid_02', 'house_old_bungalow_08',
         'house_old_tudor_05', 'house_old_ranch_05', 'house_modern_01', 'house_burnt_02', 'house_modern_29',
         'house_old_victorian_11', 'house_burnt_04', 'house_modern_09', 'house_old_victorian_06',
         'house_old_victorian_07', 'farm_07', 'house_modern_17', 'house_modern_11', 'house_old_modular_04',
         'roadside_restaurant_01', 'house_old_bungalow_04', 'house_old_tudor_03', 'commercial_strip_02',
         'store_hardware_01', 'radio_station_02']
tier3 = ['countrytown_business_09', 'office_06', 'house_modern_27', 'downtown_filler_24', 'country_junkyard_02',
         'bowling_alley_02', 'house_old_modular_02', 'house_old_gambrel_03', 'restaurant_02',
         'downtown_building_01',
         'store_grocery_03', 'carlot_02', 'warehouse_07', 'store_book_02', 'downtown_filler_06',
         'downtown_filler_31',
         'commercial_strip_05', 'farm_05', 'fire_station_02', 'downtown_filler_11', 'army_camp_04',
         'downtown_filler_22', 'motel_04', 'motel_03', 'bombshelter_02', 'downtown_filler_23', 'farm_15',
         'utility_substation_01', 'sawmill_01', 'countrytown_business_12', 'house_old_bungalow_11', 'warehouse_08',
         'lodge_01', 'roadside_strip_01', 'downtown_filler_30', 'radio_station_01', 'downtown_filler_02',
         'downtown_filler_25', 'farm_13', 'countrytown_business_11', 'diner_07', 'fire_station_03',
         'roadside_checkpoint_02', 'police_station_03', 'downtown_filler_27', 'warehouse_06', 'house_modern_28',
         'gas_station_12', 'roadside_truckstop_01', 'utility_refinery_01', 'school_daycare_02', 'store_pharmacy_02',
         'downtown_strip_09', 'post_office_02', 'ranger_station_01', 'ranger_station_07', 'store_clothing_02',
         'farm_02', 'downtown_filler_03', 'bank_02', 'field_concert_01', 'warehouse_02', 'store_clothing_01',
         'downtown_filler_05', 'house_old_victorian_01', 'countrytown_business_03', 'apartments_03',
         'downtown_strip_10', 'house_old_mansard_03', 'fastfood_06', 'house_old_pyramid_01', 'cabin_20',
         'house_old_victorian_09', 'house_old_pyramid_04', 'house_modern_21', 'house_old_mansard_04',
         'house_modern_07',
         'house_modern_26', 'house_old_ranch_12', 'house_old_victorian_04', 'house_modern_02', 'house_old_ranch_02',
         'house_old_tudor_06', 'rest_area_05', 'house_modern_05', 'house_old_ranch_13', 'house_old_bungalow_01',
         'store_discount_01', 'house_modern_30', 'downtown_filler_12', 'office_05', 'house_construction_05',
         'commercial_strip_03', 'weigh_station_01', 'rural_church_01', 'countrytown_business_08',
         'store_hardware_02',
         'warehouse_05']
tier4 = ['cave_09', 'countrytown_business_05', 'hotel_04', 'store_gun_02', 'rural_drive_in_01', 'downtown_strip_11',
         'house_modern_18', 'downtown_strip_05', 'downtown_filler_07', 'junkyard_01', 'school_02',
         'downtown_strip_01',
         'army_camp_02', 'army_camp_01', 'army_camp_05', 'army_camp_03', 'army_camp_06', 'apartments_01',
         'downtown_strip_07', 'hotel_01', 'housing_development_01', 'utility_electric_co_02', 'warehouse_03',
         'army_camp_07', 'house_modern_24', 'downtown_strip_04', 'farm_16', 'school_01', 'roadside_checkpoint_05',
         'roadside_checkpoint_04', 'roadside_checkpoint_01', 'roadside_checkpoint_03', 'downtown_strip_12',
         'city_center_01', 'warehouse_01', 'parking_garage_02', 'gas_station_05', 'downtown_building_02',
         'downtown_strip_03', 'bowling_alley_01', 'utility_refinery_02', 'restaurant_01', 'downtown_strip_02',
         'house_burnt_06', 'store_gun_01', 'church_01', 'downtown_building_03', 'store_grocery_02',
         'house_old_mansard_06', 'house_old_mansard_02', 'house_old_mansard_07', 'house_old_victorian_03',
         'skyscraper_04', 'courthouse_med_01', 'store_hardware_03', 'utility_waterworks_01']
tier5 = ['hotel_03', 'skyscraper_02', 'skyscraper_01', 'house_modern_23', 'school_03', 'hotel_02', 'skyscraper_03',
         'theater_stage_01', 'football_stadium', 'prison_01', 'prison_02', 'hospital_01', 'hotel_ostrich',
         'factory_03',
         'installation_red_mesa', 'factory_01', 'factory_02', 'nursing_home_01', 'apartments_06',
         'base_military_01',
         'apartments_02']
navezgane_only_poi = ['docks_05', 'docks_01', 'cave_05', 'docks_02', 'canyon_gift_shop', 'docks_03']

hints = ["Don't create maps below 6k if you care for POI-variety.",
         "Most rare POIs are in rural, industrial or commercial district, "
         "more and large cities help to spawn them.",
         "Priority is : mountains > towns > lakes/canyons.",
         "Different trader can spawn close to each other if you allow them in all biomes.",
         "The \"no forest\" option in \"towns to biomes\" is interesting for roadside traders, "
         "large lakes and more complex and natural landscapes in the forest.",
         "The tradersettings are active for all worldsizes.",
         "The brigthness, temperature and loot settings are active for every map (incl. Navezgane).",
         "The global loot multiplier \"forest\" slows and \"wasteland\" speeds up the game progress. "
         "One example: With a loot stage of 96 in the burned forest at default you have 56 with "
         "forest multiplier and 172 with wasteland multiplier. "
         "It does not affect the zombie spawns in each biom.",
         "The temperature setting \"realistic\" sets the temperature to values where you often experience "
         "temperature debuffs. In both desert and snow biom even mods won't be enough. "
         "The temperature setting \"apocalypse\" sets almost similar temperatures as the \"realistic\" setting, "
         "but with more frequent fog, snow, rain and storm.",
         "The randomizer setting \"chaos\" creates complete chaos!!! "
         "This includes oldwest parts in big cities and downtown districts in small towns.",
         "\"Optimized\" towns to biomes is a mean value between the rather static default setting and the "
         "\"random\" setting (e.g. oldwest is not available in forest and snow).",
         "Size and count of lakes, canyons and so on are not guaranteed but possibilities. "
         "With many large towns in all biomes you won't get a large lake anywhere.",
         "Tradercount ranges from min = 5 to max = 40, the default is 20.",
         "Traderspawns at oldwest and roadside are not guaranteed. "
         "The more towns you have the smaller the percentage to get a trader far away from towns.",
         "Some POIs like Docks are only available in Navezgane and are excluded in the above summary and missing POIs. "
         "Others like gas_station_02 and city_center_01 should be available on random maps, "
         "but they don't spawn without the provided fix in the last frame. ",
         "The combination for \"min\" count of towns and \"max\" size of towns is interesting to "
         "create just 1 town of each kind but these very large.",
         "The setting \"trader to spawn inside towns\" set trader only inside towns. The \"random\" "
         "setting pretty much everywhere, "
         "note that this option is difficult to optimize and therefore marked as experimental. "
         "It's working but not perfect."]

# START GUI
root = Tk()
root.title("Serious XML Helper and Map Check")
root.geometry("1600x1080")
root.iconbitmap(resource_path("cogwheel_options_icon.ico"))
# Backgroundimage
root.resizable(width=False, height=False)
bgimg = Image.open(resource_path("20240719033011_1.png"))  # load the background image
l_background = ttk.Label(root)
l_background.image = ImageTk.PhotoImage(bgimg)
l_background.config(image=l_background.image)
l_background.place(x=0, y=0, relwidth=1, relheight=1)  # make label l to fit the parent window always
content = ttk.Frame(root)
# FileDirectory
selected_directory = tkinter.StringVar()
directory_button = ttk.Button(content,
                              text=r"Set your 7d2d main directory (e.g. D:\Steam\steamapps\common\7 Days To Die)",
                              command=choose_directory)
path_window = ttk.Label(content, text="No directory selected")
selected_directory_map = tkinter.StringVar()
directory_button_map = ttk.Button(content,
                                  text=r"Set your map directory (folder in %appdata%\7DaysToDie\GeneratedWorlds)",
                                  command=choose_map_directory)
path_window_map = ttk.Label(content, text="No directory selected")
# GUI Variables
var_traderexcl = tkinter.StringVar()
var_tradersetup1 = tkinter.StringVar()
var_tradersetup2 = tkinter.StringVar()
var_landscape_detail = tkinter.StringVar()
var_landscape_detail2 = tkinter.StringVar()
var_townexcl = tkinter.StringVar()
var_townsize1 = tkinter.StringVar()
var_townsize2 = tkinter.StringVar()
var_towncount1 = tkinter.StringVar()
var_towncount2 = tkinter.StringVar()
var_districtcolor = tkinter.StringVar()
var_townrandomizer = tkinter.StringVar()
var_worldsize = tkinter.StringVar()
var_tradercount = tkinter.IntVar()
var_lightning = tkinter.StringVar()
var_temperature = tkinter.StringVar()
var_loot = tkinter.StringVar()
var_traderfree = tkinter.StringVar()
var_poifix = tkinter.StringVar()
# GUI Map Check
lbl_text = ttk.Label(content, text="Summary : ", justify="left")
lbl_text_detail = ttk.Label(content, text="Missing POIs: ", justify="left")
lbl_text_hints = ttk.Label(content, text="Hints: ", justify="left")
text = tkinter.Text(content, wrap=WORD, height=13, width=60)
text_detail = tkinter.Text(content, wrap=WORD, height=13, width=70)
text_hints = tkinter.Text(content, wrap=WORD, height=8, width=70)
scrollbar = ttk.Scrollbar(content, orient=tkinter.VERTICAL, command=text_detail.yview)
text_detail['yscrollcommand'] = scrollbar.set
# GUI Frames
columnspan_b = 2
width_b = 1000
height_b = 10
borderwidth_b = 5
frame01 = ttk.Frame(content, borderwidth=borderwidth_b, relief="ridge", width=width_b, height=height_b)
frame01.grid(column=0, row=3, columnspan=columnspan_b, rowspan=1, sticky="EW")
frame011 = ttk.Frame(content, borderwidth=borderwidth_b, relief="solid", width=10, height=5)
frame011.grid(column=1, row=3, columnspan=1, rowspan=1, padx=5, pady=10)
frame02 = ttk.Frame(content, borderwidth=borderwidth_b, relief="ridge", width=width_b, height=height_b)
frame02.grid(column=0, row=4, columnspan=columnspan_b, rowspan=1, sticky="EW")
frame021 = ttk.Frame(content, borderwidth=borderwidth_b, relief="solid", width=10, height=5)
frame021.grid(column=1, row=4, columnspan=1, rowspan=1, padx=5, pady=10)
frame03 = ttk.Frame(content, borderwidth=borderwidth_b, relief="ridge", width=width_b, height=height_b)
frame03.grid(column=0, row=5, columnspan=columnspan_b, rowspan=1, sticky="EW")
frame031 = ttk.Frame(content, borderwidth=borderwidth_b, relief="solid", width=10, height=5)
frame031.grid(column=1, row=5, columnspan=1, rowspan=1, padx=5, pady=10)
frame04 = ttk.Frame(content, borderwidth=borderwidth_b, relief="ridge", width=width_b, height=height_b)
frame04.grid(column=0, row=6, columnspan=columnspan_b, rowspan=1, sticky="EW")
frame041 = ttk.Frame(content, borderwidth=borderwidth_b, relief="solid", width=10, height=5)
frame041.grid(column=1, row=6, columnspan=1, rowspan=1, padx=5, pady=10)
frame05 = ttk.Frame(content, borderwidth=borderwidth_b, relief="ridge", width=width_b, height=height_b)
frame05.grid(column=0, row=7, columnspan=columnspan_b, rowspan=1, sticky="EW")
frame051 = ttk.Frame(content, borderwidth=borderwidth_b, relief="solid", width=10, height=5)
frame051.grid(column=1, row=7, columnspan=1, rowspan=1, padx=5, pady=10)
frame06 = ttk.Frame(content, borderwidth=borderwidth_b, relief="ridge", width=width_b, height=height_b)
frame06.grid(column=0, row=8, columnspan=columnspan_b, rowspan=1, sticky="EW")
frame061 = ttk.Frame(content, borderwidth=borderwidth_b, relief="solid", width=10, height=5)
frame061.grid(column=1, row=8, columnspan=1, rowspan=1, padx=5, pady=10)
frame07 = ttk.Frame(content, borderwidth=borderwidth_b, relief="ridge", width=width_b, height=height_b)
frame07.grid(column=0, row=9, columnspan=columnspan_b, rowspan=1, sticky="EW")
frame071 = ttk.Frame(content, borderwidth=borderwidth_b, relief="solid", width=10, height=5)
frame071.grid(column=1, row=9, columnspan=1, rowspan=1, padx=5, pady=10)
frame08 = ttk.Frame(content, borderwidth=borderwidth_b, relief="ridge", width=width_b, height=height_b)
frame08.grid(column=0, row=10, columnspan=columnspan_b, rowspan=1, sticky="EW")
frame081 = ttk.Frame(content, borderwidth=borderwidth_b, relief="solid", width=10, height=5)
frame081.grid(column=1, row=10, columnspan=1, rowspan=1, padx=5, pady=10)
frame09 = ttk.Frame(content, borderwidth=borderwidth_b, relief="ridge", width=width_b, height=height_b)
frame09.grid(column=0, row=11, columnspan=columnspan_b, rowspan=1, sticky="EW")
frame091 = ttk.Frame(content, borderwidth=borderwidth_b, relief="solid", width=10, height=5)
frame091.grid(column=1, row=11, columnspan=1, rowspan=1, padx=5, pady=10)
frame10 = ttk.Frame(content, borderwidth=borderwidth_b, relief="ridge", width=width_b, height=height_b)
frame10.grid(column=0, row=12, columnspan=columnspan_b, rowspan=1, sticky="EW")
frame101 = ttk.Frame(content, borderwidth=borderwidth_b, relief="solid", width=10, height=5)
frame101.grid(column=1, row=12, columnspan=1, rowspan=1, padx=5, pady=10)
frame11 = ttk.Frame(content, borderwidth=borderwidth_b, relief="ridge", width=width_b, height=height_b)
frame11.grid(column=0, row=13, columnspan=columnspan_b, rowspan=1, sticky="EW")
frame111 = ttk.Frame(content, borderwidth=borderwidth_b, relief="solid", width=10, height=5)
frame111.grid(column=1, row=13, columnspan=1, rowspan=1, padx=5, pady=10)
frame12 = ttk.Frame(content, borderwidth=borderwidth_b, relief="ridge", width=width_b, height=height_b)
frame12.grid(column=0, row=14, columnspan=columnspan_b, rowspan=1, sticky="EW")
frame121 = ttk.Frame(content, borderwidth=borderwidth_b, relief="solid", width=10, height=5)
frame121.grid(column=1, row=14, columnspan=1, rowspan=1, padx=5, pady=10)
frame13 = ttk.Frame(content, borderwidth=borderwidth_b, relief="ridge", width=width_b, height=height_b)
frame13.grid(column=0, row=15, columnspan=columnspan_b, rowspan=1, sticky="EW")
frame131 = ttk.Frame(content, borderwidth=borderwidth_b, relief="solid", width=10, height=5)
frame131.grid(column=1, row=15, columnspan=1, rowspan=1, padx=5, pady=10)
frame14 = ttk.Frame(content, borderwidth=borderwidth_b, relief="ridge", width=width_b, height=height_b)
frame14.grid(column=0, row=16, columnspan=columnspan_b, rowspan=1, sticky="EW")
frame141 = ttk.Frame(content, borderwidth=borderwidth_b, relief="solid", width=10, height=5)
frame141.grid(column=1, row=16, columnspan=1, rowspan=1, padx=5, pady=10)
frame15 = ttk.Frame(content, borderwidth=borderwidth_b, relief="ridge", width=width_b, height=height_b)
frame15.grid(column=0, row=17, columnspan=columnspan_b, rowspan=1, sticky="EW")
frame151 = ttk.Frame(content, borderwidth=borderwidth_b, relief="solid", width=10, height=5)
frame151.grid(column=1, row=17, columnspan=1, rowspan=1, padx=5, pady=10)
frame16 = ttk.Frame(content, borderwidth=borderwidth_b, relief="ridge", width=width_b, height=height_b)
frame16.grid(column=0, row=18, columnspan=columnspan_b, rowspan=1, sticky="EW")
frame161 = ttk.Frame(content, borderwidth=borderwidth_b, relief="solid", width=10, height=5)
frame161.grid(column=1, row=18, columnspan=1, rowspan=1, padx=5, pady=10)
frame17 = ttk.Frame(content, borderwidth=borderwidth_b, relief="ridge", width=width_b, height=height_b)
frame17.grid(column=0, row=19, columnspan=columnspan_b, rowspan=1, sticky="EW")
frame171 = ttk.Frame(content, borderwidth=borderwidth_b, relief="solid", width=10, height=5)
frame171.grid(column=1, row=19, columnspan=1, rowspan=1, padx=5, pady=10)
frame18 = ttk.Frame(content, borderwidth=borderwidth_b, relief="ridge", width=width_b, height=height_b)
frame18.grid(column=0, row=20, columnspan=columnspan_b, rowspan=1, sticky="EW")
frame181 = ttk.Frame(content, borderwidth=borderwidth_b, relief="solid", width=10, height=5)
frame181.grid(column=1, row=20, columnspan=1, rowspan=1, padx=5, pady=10)
# GUI Labels
lbl_traderexcl = ttk.Label(frame01, text="Set traders to biomes: ", justify="left",
                           foreground="blue",
                           font=('Times New Roman', 15, 'bold'))
lbl_tradersetup = ttk.Label(frame02, text="Set where traders can spawn: ", justify="left",
                            foreground="blue",
                            font=('Times New Roman', 15, 'bold'))
lbl_tradercount = ttk.Label(frame03, text="Set the max tradercount: ", justify="left",
                            foreground="blue",
                            font=('Times New Roman', 15, 'bold'))
lbl_worldsize = ttk.Label(frame04, text="Set the worldsize: ", justify="left",
                          foreground="blue",
                          font=('Times New Roman', 15, 'bold'))
lbl_landscape_detail = ttk.Label(frame05, text="Set possible size of lakes, canyons, ...: ", justify="left",
                                 foreground="blue",
                                 font=('Times New Roman', 15, 'bold'))
lbl_landscape_detail2 = ttk.Label(frame06, text="Set possible count of lakes, canyons, ...: ", justify="left",
                                  foreground="blue",
                                  font=('Times New Roman', 15, 'bold'))
lbl_townexcl = ttk.Label(frame07, text="Set towns to biomes: ", justify="left",
                         foreground="blue",
                         font=('Times New Roman', 15, 'bold'))
lbl_townsize1 = ttk.Label(frame08, text="Set size of small towns: ", justify="left",
                          foreground="blue",
                          font=('Times New Roman', 15, 'bold'))
lbl_townsize2 = ttk.Label(frame09, text="Set size of large towns : ", justify="left",
                          foreground="blue",
                          font=('Times New Roman', 15, 'bold'))
lbl_towncount1 = ttk.Label(frame10, text="Set count of small towns: ", justify="left",
                           foreground="blue",
                           font=('Times New Roman', 15, 'bold'))
lbl_towncount2 = ttk.Label(frame11, text="Set count of large towns : ", justify="left",
                           foreground="blue",
                           font=('Times New Roman', 15, 'bold'))
lbl_districtcolor = ttk.Label(frame12, text="Set district color: ", justify="left",
                              foreground="blue",
                              font=('Times New Roman', 15, 'bold'))
lbl_townrandomizer = ttk.Label(frame13, text="Set a randomizer for districts in towns: ", justify="left",
                               foreground="blue",
                               font=('Times New Roman', 15, 'bold'))
lbl_lightning = ttk.Label(frame14, text="Set the brightness at night: ", justify="left",
                          foreground="blue",
                          font=('Times New Roman', 15, 'bold'))
lbl_temperature = ttk.Label(frame15, text="Set the temperature setup: ", justify="left",
                            foreground="blue",
                            font=('Times New Roman', 15, 'bold'))
lbl_loot = ttk.Label(frame16, text="Set global loot multiplier: ", justify="left",
                     foreground="blue",
                     font=('Times New Roman', 15, 'bold'))
lbl_traderfree = ttk.Label(frame17, text="EXPERIMENTAL!!! Set traders to spawn inside towns: ", justify="left",
                           foreground="blue",
                           font=('Times New Roman', 15, 'bold'))
lbl_poifix = ttk.Label(frame18, text="Fixes 7 POIs to spawn in RWG: ", justify="left",
                       foreground="blue",
                       font=('Times New Roman', 15, 'bold'))


lbl_empty = ttk.Label(content, text="       ", font=('Times New Roman', 15, 'bold'))
# GUI Radiobuttons
one_traderexcl = ttk.Radiobutton(frame011, text="default", value="default", variable=var_traderexcl,
                                 style="Default.TRadiobutton")
two_traderexcl = ttk.Radiobutton(frame011, text="random", value="random", variable=var_traderexcl)
var_traderexcl.set("default")
one_tradersetup = ttk.Button(frame021, text="town", state="disabled")
two_tradersetup = ttk.Checkbutton(frame021, text="oldwest", variable=var_tradersetup1)
three_tradersetup = ttk.Checkbutton(frame021, text="roadside", variable=var_tradersetup2)
one_tradercount = ttk.Radiobutton(frame031, text="min", value=5, variable=var_tradercount)
two_tradercount = ttk.Radiobutton(frame031, text="fewer", value=10, variable=var_tradercount)
three_tradercount = ttk.Radiobutton(frame031, text="default", value=20, variable=var_tradercount,
                                    style="Default.TRadiobutton")
var_tradercount.set(20)
four_tradercount = ttk.Radiobutton(frame031, text="more", value=30, variable=var_tradercount)
five_tradercount = ttk.Radiobutton(frame031, text="max", value=40, variable=var_tradercount)
one_worldsize = ttk.Radiobutton(frame041, text="< 5k", value="tiny", variable=var_worldsize)
two_worldsize = ttk.Radiobutton(frame041, text="5k - 7k", value="small", variable=var_worldsize)
three_worldsize = ttk.Radiobutton(frame041, text="7k - 10k", value="medium", variable=var_worldsize,
                                  style="Default.TRadiobutton")
four_worldsize = ttk.Radiobutton(frame041, text="> 10k", value="large", variable=var_worldsize)
var_worldsize.set("large")
one_landscape_detail = ttk.Radiobutton(frame051, text="min", value="min", variable=var_landscape_detail)
two_landscape_detail = ttk.Radiobutton(frame051, text="lower", value="lower", variable=var_landscape_detail)
three_landscape_detail = ttk.Radiobutton(frame051, text="default", value="default", variable=var_landscape_detail,
                                         style="Default.TRadiobutton")
var_landscape_detail.set("default")
four_landscape_detail = ttk.Radiobutton(frame051, text="larger", value="larger", variable=var_landscape_detail)
five_landscape_detail = ttk.Radiobutton(frame051, text="max", value="max", variable=var_landscape_detail)
one_landscape_detail2 = ttk.Radiobutton(frame061, text="min", value="min", variable=var_landscape_detail2)
two_landscape_detail2 = ttk.Radiobutton(frame061, text="fewer", value="fewer", variable=var_landscape_detail2)
three_landscape_detail2 = ttk.Radiobutton(frame061, text="default", value="default", variable=var_landscape_detail2,
                                          style="Default.TRadiobutton")
var_landscape_detail2.set("default")
four_landscape_detail2 = ttk.Radiobutton(frame061, text="more", value="more",
                                         variable=var_landscape_detail2)
five_landscape_detail2 = ttk.Radiobutton(frame061, text="max", value="max", variable=var_landscape_detail2)
one_townexcl = ttk.Radiobutton(frame071, text="default", value="default", variable=var_townexcl,
                               style="Default.TRadiobutton")
two_townexcl = ttk.Radiobutton(frame071, text="optimized", value="optimized", variable=var_townexcl)
three_townexcl = ttk.Radiobutton(frame071, text="random", value="random", variable=var_townexcl)
four_townexcl = ttk.Radiobutton(frame071, text="no forest", value="no forest", variable=var_townexcl)
var_townexcl.set("default")
one_townsize1 = ttk.Radiobutton(frame081, text="min", value="min", variable=var_townsize1)
two_townsize1 = ttk.Radiobutton(frame081, text="smaller", value="smaller", variable=var_townsize1)
three_townsize1 = ttk.Radiobutton(frame081, text="default", value="default", variable=var_townsize1,
                                  style="Default.TRadiobutton")
var_townsize1.set("default")
four_townsize1 = ttk.Radiobutton(frame081, text="larger", value="larger", variable=var_townsize1)
five_townsize1 = ttk.Radiobutton(frame081, text="max", value="max", variable=var_townsize1)
one_townsize2 = ttk.Radiobutton(frame091, text="min", value="min", variable=var_townsize2)
two_townsize2 = ttk.Radiobutton(frame091, text="smaller", value="smaller", variable=var_townsize2)
three_townsize2 = ttk.Radiobutton(frame091, text="default", value="default", variable=var_townsize2,
                                  style="Default.TRadiobutton")
var_townsize2.set("default")
four_townsize2 = ttk.Radiobutton(frame091, text="larger", value="larger", variable=var_townsize2)
five_townsize2 = ttk.Radiobutton(frame091, text="max", value="max", variable=var_townsize2)
one_towncount1 = ttk.Radiobutton(frame101, text="min", value="min", variable=var_towncount1)
two_towncount1 = ttk.Radiobutton(frame101, text="fewer", value="fewer", variable=var_towncount1)
three_towncount1 = ttk.Radiobutton(frame101, text="default", value="default", variable=var_towncount1,
                                   style="Default.TRadiobutton")
var_towncount1.set("default")
four_towncount1 = ttk.Radiobutton(frame101, text="more", value="more", variable=var_towncount1)
five_towncount1 = ttk.Radiobutton(frame101, text="max", value="max", variable=var_towncount1)
one_towncount2 = ttk.Radiobutton(frame111, text="min", value="min", variable=var_towncount2)
two_towncount2 = ttk.Radiobutton(frame111, text="fewer", value="fewer", variable=var_towncount2)
three_towncount2 = ttk.Radiobutton(frame111, text="default", value="default", variable=var_towncount2,
                                   style="Default.TRadiobutton")
var_towncount2.set("default")
four_towncount2 = ttk.Radiobutton(frame111, text="more", value="more", variable=var_towncount2)
five_towncount2 = ttk.Radiobutton(frame111, text="max", value="max", variable=var_towncount2)
one_districtcolor = ttk.Radiobutton(frame121, text="default", value="default", variable=var_districtcolor,
                                    style="Default.TRadiobutton")
two_districtcolor = ttk.Radiobutton(frame121, text="optimized", value="optimized", variable=var_districtcolor)
var_districtcolor.set("default")
one_townrandomizer = ttk.Radiobutton(frame131, text="default", value="default", variable=var_townrandomizer,
                                     style="Default.TRadiobutton")
two_townrandomizer = ttk.Radiobutton(frame131, text="optimized", value="optimized", variable=var_townrandomizer)
three_townrandomizer = ttk.Radiobutton(frame131, text="chaos", value="chaos", variable=var_townrandomizer)
var_townrandomizer.set("default")
one_lightning = ttk.Radiobutton(frame141, text="default", value="default", variable=var_lightning)
var_lightning.set("default")
two_lightning = ttk.Radiobutton(frame141, text="darker", value="darker", variable=var_lightning)
three_lightning = ttk.Radiobutton(frame141, text="realistic", value="realistic", variable=var_lightning,
                                  style="Default.TRadiobutton")
one_temperature = ttk.Radiobutton(frame151, text="default", value="default", variable=var_temperature,
                                  style="Default.TRadiobutton")
var_temperature.set("default")
two_temperature = ttk.Radiobutton(frame151, text="basic", value="basic", variable=var_temperature)
three_temperature = ttk.Radiobutton(frame151, text="realistic", value="realistic", variable=var_temperature)
four_temperature = ttk.Radiobutton(frame151, text="apocalypse", value="apocalypse", variable=var_temperature)
one_loot = ttk.Radiobutton(frame161, text="forest", value="forest", variable=var_loot)
two_loot = ttk.Radiobutton(frame161, text="default", value="default", variable=var_loot,
                           style="Default.TRadiobutton")
var_loot.set("default")
three_loot = ttk.Radiobutton(frame161, text="wasteland", value="wasteland", variable=var_loot)
one_traderfree = ttk.Radiobutton(frame171, text="default", value="default", variable=var_traderfree,
                                 style="Default.TRadiobutton")
var_traderfree.set("default")
two_traderfree = ttk.Radiobutton(frame171, text="inside", value="inside", variable=var_traderfree)
three_traderfree = ttk.Radiobutton(frame171, text="random", value="random", variable=var_traderfree)
one_poifix = ttk.Radiobutton(frame181, text="default", value="default", variable=var_poifix,
                             style="Default.TRadiobutton")
var_poifix.set("default")
two_poifix = ttk.Radiobutton(frame181, text="fix", value="fix", variable=var_poifix)
# GUI Buttons
save_button = ttk.Button(content,
                         text=r"save the configuration",
                         command=xmlprocessing)
exit_button = ttk.Button(content,
                         text=r"exit",
                         command=exitnew)
hint_button = ttk.Button(content,
                         text=r"hint",
                         command=show_hint)
lbl_text_save_info = ttk.Label(content, text="Note that you need to restart 7D2D to make the settings count: ",
                               justify="left")
debug_window = ttk.Label(content, text="Debug-Window")
# GUI Grid
content.grid(column=3, row=10)
directory_button.grid(column=0, row=1, columnspan=1)
path_window.grid(column=0, row=2, padx=5, pady=5, columnspan=1)
directory_button_map.grid(column=2, row=1)
path_window_map.grid(column=2, row=2)

lbl_text.grid(column=2, row=3)
text.grid(column=2, row=4, columnspan=4, rowspan=4, padx=20)
lbl_text_detail.grid(column=2, row=8)
text_detail.grid(column=2, row=9, columnspan=4, rowspan=4, padx=20)
scrollbar.grid(column=5, row=9, rowspan=4, sticky="NSE")
lbl_text_hints.grid(column=2, row=13)
text_hints.grid(column=2, row=13, columnspan=4, rowspan=4, padx=20)

lbl_traderexcl.grid(column=0, row=0, sticky="W", padx=5, pady=5)
one_traderexcl.grid(column=0, row=0, sticky="E", padx=5, pady=5)
two_traderexcl.grid(column=1, row=0, sticky="E", padx=5, pady=5)
lbl_tradersetup.grid(column=0, row=0, sticky="W", padx=5, pady=5)
one_tradersetup.grid(column=3, row=0, sticky="E")
two_tradersetup.grid(column=4, row=0, sticky="E")
three_tradersetup.grid(column=5, row=0, sticky="E")
lbl_townexcl.grid(column=0, row=0, sticky="W", padx=5, pady=5)
one_townexcl.grid(column=2, row=0, sticky="E")
two_townexcl.grid(column=3, row=0, sticky="E")
three_townexcl.grid(column=4, row=0, sticky="E")
four_townexcl.grid(column=5, row=0, sticky="E")
lbl_landscape_detail.grid(column=0, row=0, sticky="W", padx=5, pady=5)
one_landscape_detail.grid(column=1, row=0, sticky="EW")
two_landscape_detail.grid(column=2, row=0, sticky="EW")
three_landscape_detail.grid(column=3, row=0, sticky="EW")
four_landscape_detail.grid(column=4, row=0, sticky="E")
five_landscape_detail.grid(column=5, row=0, sticky="E")
lbl_landscape_detail2.grid(column=0, row=0, sticky="W", padx=5, pady=5)
one_landscape_detail2.grid(column=1, row=0, sticky="EW")
two_landscape_detail2.grid(column=2, row=0, sticky="EW")
three_landscape_detail2.grid(column=3, row=0, sticky="EW")
four_landscape_detail2.grid(column=4, row=0, sticky="E")
five_landscape_detail2.grid(column=5, row=0, sticky="E")
lbl_townsize1.grid(column=0, row=0, sticky="W", padx=5, pady=5)
one_townsize1.grid(column=1, row=0, sticky="E")
two_townsize1.grid(column=2, row=0, sticky="E")
three_townsize1.grid(column=3, row=0, sticky="E")
four_townsize1.grid(column=4, row=0, sticky="E")
five_townsize1.grid(column=5, row=0, sticky="E")
lbl_townsize2.grid(column=0, row=0, sticky="W", padx=5, pady=5)
one_townsize2.grid(column=1, row=0, sticky="E")
two_townsize2.grid(column=2, row=0, sticky="E")
three_townsize2.grid(column=3, row=0, sticky="E")
four_townsize2.grid(column=4, row=0, sticky="E")
five_townsize2.grid(column=5, row=0, sticky="E")
lbl_towncount1.grid(column=0, row=0, sticky="W", padx=5, pady=5)
one_towncount1.grid(column=1, row=0, sticky="E")
two_towncount1.grid(column=2, row=0, sticky="E")
three_towncount1.grid(column=3, row=0, sticky="E")
four_towncount1.grid(column=4, row=0, sticky="E")
five_towncount1.grid(column=5, row=0, sticky="E")
lbl_towncount2.grid(column=0, row=0, sticky="W", padx=5, pady=5)
one_towncount2.grid(column=1, row=0, sticky="E")
two_towncount2.grid(column=2, row=0, sticky="E")
three_towncount2.grid(column=3, row=0, sticky="E")
four_towncount2.grid(column=4, row=0, sticky="E")
five_towncount2.grid(column=5, row=0, sticky="E")
lbl_districtcolor.grid(column=0, row=0, sticky="W", padx=5, pady=5)
one_districtcolor.grid(column=0, row=0, sticky="E", padx=5, pady=5)
two_districtcolor.grid(column=1, row=0, sticky="E", padx=5, pady=5)
lbl_townrandomizer.grid(column=0, row=0, sticky="W", padx=5, pady=5)
one_townrandomizer.grid(column=3, row=0, sticky="E")
two_townrandomizer.grid(column=4, row=0, sticky="E")
three_townrandomizer.grid(column=5, row=0, sticky="E")
lbl_worldsize.grid(column=0, row=0, sticky="W", padx=5, pady=5)
one_worldsize.grid(column=2, row=0, sticky="E")
two_worldsize.grid(column=3, row=0, sticky="E")
three_worldsize.grid(column=4, row=0, sticky="E")
four_worldsize.grid(column=5, row=0, sticky="E")
lbl_tradercount.grid(column=0, row=0, sticky="W", padx=5, pady=5)
one_tradercount.grid(column=1, row=0, sticky="E")
two_tradercount.grid(column=2, row=0, sticky="E")
three_tradercount.grid(column=3, row=0, sticky="E")
four_tradercount.grid(column=4, row=0, sticky="E")
five_tradercount.grid(column=5, row=0, sticky="E")
lbl_lightning.grid(column=0, row=0, sticky="W", padx=5, pady=5)
one_lightning.grid(column=1, row=0, sticky="E")
two_lightning.grid(column=2, row=0, sticky="E")
three_lightning.grid(column=3, row=0, sticky="E")
lbl_temperature.grid(column=0, row=0, sticky="W", padx=5, pady=5)
one_temperature.grid(column=1, row=0, sticky="E")
two_temperature.grid(column=2, row=0, sticky="E")
three_temperature.grid(column=3, row=0, sticky="E")
four_temperature.grid(column=4, row=0, sticky="E")
lbl_loot.grid(column=0, row=0, sticky="W", padx=5, pady=5)
one_loot.grid(column=1, row=0, sticky="E")
two_loot.grid(column=2, row=0, sticky="E")
three_loot.grid(column=3, row=0, sticky="E")
lbl_traderfree.grid(column=0, row=0, sticky="W", padx=5, pady=5)
one_traderfree.grid(column=1, row=0, sticky="E")
two_traderfree.grid(column=2, row=0, sticky="E")
three_traderfree.grid(column=3, row=0, sticky="E")
lbl_poifix.grid(column=0, row=0, sticky="W", padx=5, pady=5)
one_poifix.grid(column=1, row=0, sticky="E")
two_poifix.grid(column=2, row=0, sticky="E")
save_button.grid(column=2, row=17, padx=20, pady=5)
hint_button.grid(column=2, row=16, padx=20, pady=5)
exit_button.grid(column=4, row=17, padx=20, pady=5)
lbl_text_save_info.grid(column=2, row=18, padx=20, pady=5)

root.mainloop()
