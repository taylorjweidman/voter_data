from base_imports import *

def knn_col_names():
    """ Generate column names for knn statistics. """
    
    names = ['idu'] + [party+'0' for party in party_list]
    for k in k_list:
        for party in party_list:
            names.append(party+str(k))
        names += [str(k)+'_lat',str(k)+'_lon',str(k)+'_dist']
    return names


def proximity_matrix(SNd, year, print_log, state = state, meters = meters):
    """ Find the neighborhoods within a variable radius containing k_max voters. """
    
    data_name = year + ' @ ' + str(k_max) + 'k'
    file_desc = str(year) + '_' + str(meters) + 'm_' + str(k_max) + 'k.pkl'
    with open(path_3 + 'POPd_' + str(year) + '_' + str(meters) + 'm.pkl','rb') as f: 
        POPd = pickle.load(f)
    
    if 'Pd_' + file_desc in os.listdir(path_4 + 'Pd'):
        print_log[data_name]['sublog'] = ['   || Loading Pd']
        printer(print_log)
        with open(path_4 + 'Pd/Pd_' + file_desc,'rb') as f: 
            Pd = pickle.load(f)
    
    else:
        print_log[data_name]['sublog'] = ['   || Generating Pd']
        printer(print_log)
        with open(path_3 + 'Ad_' + str(meters) + 'm.pkl','rb') as f: 
            Ad = pickle.load(f)
        with open(path_3 + 'Cd_' + str(meters) + 'm.pkl','rb') as f: 
            Cd = pickle.load(f)

        Pd = {}
        for ni in SNd:
            ni_P, radius = [x for x in Ad[ni]], meters*1.1
            
            while sum([POPd[a] for a in ni_P]) < k_max:
                """ Check whether the population of the neighborhood is less than k_max in curcles of increasing radius. """
                
                ni_PX = [Ad[adj] for adj in ni_P] # Find neighborhoods adjacent to ni_P
                ni_PX = set([i for sublist in ni_PX for i in sublist]) # Flatten; unique
                ni_PX = [a for a in ni_PX if a not in ni_P + [ni]] # Select new neighborhoods
                
                def centroid_dist(ni, a):
                    """ Measure distance between two centroids. """
                    ni_lat_lon = (Cd[ni]['lat'], Cd[ni]['lon'])
                    a_lat_lon = (Cd[a]['lat'], Cd[a]['lon'])
                    return haversine(ni_lat_lon, a_lat_lon, Unit.METERS)
                ni_P += [a for a in ni_PX if (centroid_dist(ni, a) < radius)]
                
                radius = radius + meters/2
            Pd[ni] = {'P': ni_P, 'radius': radius}
            
            if len(Pd)%100 == 0:
                print_log[data_name]['sublog'] = ['   || Proximity: '+str(round(100*len(Pd)/len(SNd),3))+'%']
                printer(print_log)
        
        with open(path_4+'/Pd/Pd_' + file_desc,'wb') as f:
            pickle.dump(Pd, f)
    
    print_log[data_name]['sublog'] = []
    printer(print_log)
    
    return Pd, POPd


#def distance(x,y):
#    """ Take two dictionaries and measure the distance between their lat lon combinations in meters. """
    
#    x_lat, x_lon = float(x['lat']), float(x['lon'])
#    y_lat, y_lon = float(y['lat']), float(y['lon'])
    
#    R = 6371000 # meters
    
#    lat1,lat2 = math.radians(x_lat),math.radians(y_lat)
#    latdif = math.radians(y_lat-x_lat)
#    londif = math.radians(y_lon-x_lon)
#    a = math.sin(latdif/2) * math.sin(latdif/2) + math.cos(lat1) * math.cos(lat2) * math.sin(londif/2) * math.sin(londif/2)
#    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
#    return R*c


#def distance_matrix_(n, N): 
#    """Return a matrix of distances between every voter in n1 and every voter in n2"""
#    """ Is my slow handwritten code: 0.0016806126 sec vs 2.4040441513 sec. """
    
#    for vi,v in n.iterrows():
#        v_pair = {'lat':v.lat, 'lon':v.lon}
#        D.loc[v.idu] = [distance(v_pair,{'lat':V.lat, 'lon':V.lon}) for Vi,V in N.iterrows()] # Vectorize this?
        
#    return pd.DataFrame(D)







