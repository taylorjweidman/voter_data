from base_imports import *

def knn_col_names(extras=[]):
    """ Generate column names for knn statistics. """
    
    names = ['idu'] + [party+'0' for party in party_list]
    for k in k_list:
        names += [party+str(k) for party in party_list]
        names += [extra+str(k) for extra in extras]
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
                
        print_log[data_name]['sublog'] = ['   || Proximity: '+str(round(100*len(Pd)/len(SNd),3))+'%']
        printer(print_log)
        
        with open(path_4+'/Pd/Pd_' + file_desc,'wb') as f:
            pickle.dump(Pd, f)
    
    print_log[data_name]['sublog'] = []
    printer(print_log)
    
    return Pd, POPd




