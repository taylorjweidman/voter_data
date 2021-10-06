from base_imports import *

k_list = [5,10,25,50,100,150,200,250,300,400,500]

date_map = {'2005': 20051125,
            '2006': 20060210,
            '2007': 20070119,
            '2008': 20081104,
            '2009': 20090101,
            '2010': 20100101,
            '2011': 20110101,
            '2012': 20120101,
            '2013': 20130101,
            '2015': 20150101,
            '2016': 20161108,
            '2017': 20170101,
            '2018': 20180101,
            '2019': 20190101}

party_color = {'D':'royalblue','R':'firebrick'}
parties = [p for p in party_color]
party_map = {'R':'REP','D':'DEM'}


class Voter:
    """
    Voter stores voter level attributes. 
    Immutable attributes are initialized. 
    Mutable attributes are included by voter file year.
    """
    
    def __init__(self):
        self.idu = None
        self.first = None
        self.middle = None
        self.last = None
        self.birthyear = None # This is more like the age they are when they vote in Nov.
        self.gender = None
        self.race = None
        self.birthplace = None
        self.state = None
        
    def attributes(self, x):
        idu, first, middle, last, birthyear, gender, race, birthplace, state = x
        self.idu = idu
        self.first = first
        self.middle = middle
        self.last = None
        self.birthyear = None # This is more like the age they are when they vote in Nov.
        self.gender = None
        self.race = None
        self.birthplace = None
        self.state = None
    
    def history(self, x):
        self.party = None
        
    def geocode(self):
        """Go to the gecoded file, find the """
        pass
    
    def neighborhood(self):
        pass
    
    def knn(self):
        pass
    

