import pandas as pd
import geopandas as gpd
import numpy as np
import matplotlib.pyplot as plt
import time
from datetime import datetime
import os
import random
import seaborn as sns
import math
import gc
import multiprocessing.dummy as mp
from shapely.geometry import Point, Polygon
from shapely import wkt
import pickle
from IPython.display import clear_output
import json
import requests
import sys
from functools import partial
from shapely import wkt
from zipfile import ZipFile
import re
import csv
import censusgeocode as cg

from haversine import haversine, haversine_vector, Unit, inverse_haversine, Direction # https://github.com/mapado/haversine

print_log = {}
state = 'NC'
path_0 = 'data0_raw/NC/'
path_0_zip = path_0+'snapshots/'
path_0_csv = path_0+'unpacked/'
path_1 = 'data1_clean/'+state+'/'
path_2 = 'data2_geocode/'+state+'/'

folder = 'data3_neighborhoods/'
path_3 = folder+state+'/'
path_4 = 'data4_knn/' + state + '/'
path_4_pre = path_4 + 'split_pre/'
path_4_post = path_4 + 'split_post/'

path_link = 'datalink/' + state + '/'

k_list = [10, 50, 200, 500] + [1000, 2000]
k_max = max(k_list) + 50
meters = 2000
party_list = ['D', 'R', 'O']

def printer(print_log):
    """ Take a Print Log and print it in a pretty way. """
    clear_output(wait=True)
    for l in print_log:
        print(l)
        for t in print_log[l]:
            for p in print_log[l][t]:
                if type(print_log[l][t]) == type({}):
                    print(p,print_log[l][t][p])
                else:
                    print(p)
                    
def string_printer(print_log):
    """ Take a Print Log and print it in a pretty way. """
    
    string_print = ''
    for l in print_log:
        string_print += l + ' \n'
        for t in print_log[l]:
            for p in print_log[l][t]:
                if type(print_log[l][t]) == type({}):
                    string_print += p + print_log[l][t][p] + ' \n'
                else:
                    string_print += p + ' \n'
    return string_print


yearlist = [2006, 2007, 2008, 2009, 2010, 2011, 2012, 2013, 2015, 2016, 2017, 2018, 2019]

class Voter:
    def __init__(self):
        self.first_name = None
        self.last_name = None
        self.birthplace = None
        self.DOUBLE_ID = None
        
    def knn():
        pass
        
class Neighborhood:
    def __init__(self):
        self.id = None
        self.geography = None
        self.corners = None
        
    def create_polygon():
        pass
    
    