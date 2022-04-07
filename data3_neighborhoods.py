from base_imports import *

keep_cols = ['idu', 'lat', 'lon', 'party', 'race', 'status']

                
def setup_dictionaries(meters, state, data_name, print_it = True):

    if 'Ad_' + str(meters) + 'm.pkl' in os.listdir(folder + state + '/'):
        if print_it:
            print_log[data_name]['log'] = ['  Step 0 | Load Grid']
            printer(print_log)
        with open(folder + state + '/LLd_' + str(meters) + 'm.pkl','rb') as f: 
            LLd = pickle.load(f)
        with open(folder + state + '/Ad_' + str(meters) + 'm.pkl','rb') as f: 
            Ad = pickle.load(f)
        with open(folder + state + '/Cd_' + str(meters) + 'm.pkl','rb') as f: 
            Cd = pickle.load(f)
    
    else:
        if print_it:
            print_log[data_name]['log'] = ['  Step 0 | Generate Grid']
            printer(print_log)
        path_2_geo = path_2+state+'_'+str(2010)+'_geo.pkl'
        with open(path_2_geo,'rb') as f: 
            voter_data = pickle.load(f)
        Lats, Lons = define_squares(voter_data, meters)
        Ad, LLd, Cd = adjacency_matrix(Lats, Lons, data_name, print_log, path_3)
        with open(folder + state + '/LLd_' + str(meters) + 'm.pkl','wb') as f: 
            pickle.dump(LLd, f)
        with open(folder + state + '/Ad_' + str(meters) + 'm.pkl','wb') as f: 
            pickle.dump(Ad, f)
        with open(folder + state + '/Cd_' + str(meters) + 'm.pkl','wb') as f: 
            pickle.dump(Cd, f)

    return LLd, Ad, Cd


def define_squares(data, meters):
    """ Generate lists of all possible (lat,lon) corners. """
    
    median = (data.lat.median(), data.lon.median())
    east = inverse_haversine(median, meters, Direction.EAST, unit=Unit.METERS)
    north = inverse_haversine(median, meters, Direction.NORTH, unit=Unit.METERS)

    east_diff = list(np.abs(np.array(median) - np.array(east)))
    north_diff = list(np.abs(np.array(median) - np.array(north)))

    lat_del = max(east_diff[0], north_diff[0])
    lon_del = max(east_diff[1], north_diff[1])

    Lats = np.arange(data.lat.min(), data.lat.max() + lat_del, lat_del)
    Lons = np.arange(data.lon.min(), data.lon.max() + lon_del, lon_del)

    return Lats, Lons # H, W


def adjacency_matrix(Lats, Lons, data_name, print_log, path_3):
    """ Generate the three dictionaries, taking a neighborhood index and returning:
            Ad: a list of adjacent square neighborhood indices.
            LLd: the coordinates of a square neighborhood's corners.
            Cd: the square's centroid (lat,lon) """
    
    Lat_num = len(Lats)-1 # number of squares is one less than the number of Lats/Lons
    Lon_num = len(Lons)-1 # number of squares is one less than the number of Lats/Lons
    Lat_index, Lon_index = np.arange(Lat_num), np.arange(Lon_num)
    Lat_dict = {i:(Lats[i],Lats[i+1]) for i in Lat_index} # H
    Lon_dict = {i:(Lons[i],Lons[i+1]) for i in Lon_index} # W
    
    Ad, LLd, Cd, finished = {}, {}, {}, []    
    for j in Lat_dict:
        for i in Lon_dict:
            """ 
            Index:
            1. Starts at 0 in the upper left
            2. Runs to the right
            3. Then starts again one row down on the left. 
            """
            index = int(j*Lon_num + i)
            LLd[index] = {
                'lat_l':Lats[j], 
                'lat_u':Lats[j+1], 
                'lon_l':Lons[i], 
                'lon_u':Lons[i+1]
            }
            Cd[index] = {'lat':(Lats[j]+Lats[j+1])/2, 'lon':(Lons[i]+Lons[i+1])/2}

            if (i>0) & (i<Lon_num-1): # Horizontal Interior
                Wi = [-1,0,1]
            else: # Side
                if (i==0): # Left Edge
                    Wi = [0,1]
                else: # Right Edge
                    Wi = [-1,0]
            if (j>0) & (j<Lat_num-1): # Vertical Interior
                Hj = [-1,0,1]
            else:
                if (j==0): # Top Edge
                    Hj = [0,1]
                else: # Bottom Edge
                    Hj = [-1,0]

            A_x = []
            for wi in Wi:
                for hj in Hj:
                    if abs(wi)+abs(hj) != 0:
                        a = int((j+hj)*Lon_num + i + wi)
                        A_x.append(a)

            Ad[index] = A_x
        finished.append(j)
        print_log[data_name]['sublog'] = ['   || Adjacency: '+str(round(100*len(finished)/Lat_num,3))+'%']
        printer(print_log)

    return Ad, LLd, Cd


def cut_in_half(four, ll_key):
    """ Cut ll_key dimension in half. """
    
    LL_four_list = []
    
    """ Setup input data. """
    data, LLd = four['N'], four['LLd']
    LL = [LLd[i][ll_key+'_l'] for i in LLd] + [LLd[i][ll_key+'_u'] for i in LLd]
    LL = list(set(LL))
    ll_median = sorted(LL)[len(LL)//2]
    ll_min, ll_max = min(LL), max(LL)

    """ Select lower half. """
    LL_four_list.append({
        'N':data[(ll_min <= data[ll_key]) & (data[ll_key] < ll_median)],
        'LLd':{i:LLd[i] for i in LLd if LLd[i][ll_key+'_u'] <= ll_median}
    })
    """ Select upper half. """
    LL_four_list.append({
        'N':data[(ll_median <= data[ll_key]) & (data[ll_key] <= ll_max)],
        'LLd':{i:LLd[i] for i in LLd if ll_median <= LLd[i][ll_key+'_l']}
    })
    
    return LL_four_list


def foursquare(four):
    """ 
    Divide an input square neighborhood into (up to) four output square neighborhoods.
    This method optimizes the populate_squares function to run in n log_2(n) time. 
    """
    
    """ Width (lon) """
    W_four_list = []

    """ Cut width (lon) in half. """
    if len(four['LLd']) > 1:
        W_four_list = W_four_list + cut_in_half(four, 'lon')
    else:
        W_four_list.append(four)
    
    """ Height (lat) """
    H_four_list = []
    for four in W_four_list:

        """ Cut height (lat) in half. """
        if len(four['LLd']) > 1:
            H_four_list = H_four_list + cut_in_half(four, 'lat')
        else:
            H_four_list.append(four)
    
    return H_four_list


def populate_squares(data, LLd, print_log, data_name, meters, demographics = False):
    """ Generate two dictionaries, both taking a neighborhood index and returning:
        SNd: the square neighborhood's contents
        POPd: its population """
    
    print_log[data_name]['sublog'] = ['   || Creating Lists']
    printer(print_log)
    
    four_list, keep_going = [{'N':data, 'LLd':LLd}], True
    
    while keep_going:
        new_four_list, keep_going = [], False
        for four in four_list:
            if len(four['N']) > 0:
                if len(four['LLd']) > 1:
                    keep_going += True
                    add_four_list = foursquare(four)
                    new_four_list += add_four_list
                if len(four['LLd']) == 1:
                    new_four_list.append(four)
                    
        four_list = new_four_list
        print_log[data_name]['sublog'] = ['   || Creating Squares (' + str(len(four_list)) + ')']
        printer(print_log)
    
    POPd = {i:0 for i in LLd} # Include even empty neighborhoods
    SNd, finished = {}, []
    
    for four in four_list:
        n = four['N']
        if len(n) > 0:
            index, = list(four['LLd'])
            lat_lon = four['LLd'][index]
            h_l, h_u, w_l, w_u = [lat_lon[k] for k in lat_lon]
            n.loc[:,'geometry'] = Polygon([(w_l,h_l), (w_u,h_l), (w_u,h_u), (w_l,h_u)])
            n.loc[:,'sn_i'] = index
            POPd[index] = len(n)
            
            if demographics:
                n['M_'+str(meters)+'m'] = sum((n.gender == 'M')*1)
                n['F_'+str(meters)+'m'] = sum((n.gender == 'F')*1)
                n['BLACK_'+str(meters)+'m'] = sum((n.race == 'BLACK or AFRICAN AMERICAN')*1)
                n['WHITE_'+str(meters)+'m'] = sum((n.race == 'WHITE')*1)
                n['OTHER_'+str(meters)+'m'] = sum((~n.race.isin(['BLACK or AFRICAN AMERICAN','WHITE']))*1)
                n['D_'+str(meters)+'m'] = n.D.sum()
                n['R_'+str(meters)+'m'] = n.R.sum()
                n['O_'+str(meters)+'m'] = n.O.sum()
                n['MEAN_AGE_'+str(meters)+'m'] = n.age.astype(float).mean()
            
            SNd[index] = n
            
        finished.append(index)
        populated_squares = str(round(100*len(finished)/len(four_list),3))
        print_log[data_name]['sublog'] = ['   || Populating: ' + populated_squares + '%']
        printer(print_log)
    
    print_log[data_name]['sublog'] = []
    printer(print_log)
    
    return SNd, POPd


##########################


def foursquare_old(four):
    """ Divide an input square neighborhood into (up to) four output square neighborhoods, optimizing the populate_squares function to run in n log_2(n) time. """
    
    data, LLd = four['N'], four['LLd']
    W = [LLd[i]['lon_l'] for i in LLd]
    if len(W) > 1:
        w_median = sorted(W)[len(W)//2]
        w_min = min(W)
        w_max = max(W)
        W_four_list = [
            {'N':data[(data.lon < w_median) & (data.lon >= w_min)],
             'LLd':{i:LLd[i] for i in LLd if LLd[i]['lon_u'] <= w_median}},
            {'N':data[(data.lon >= w_median) & (data.lon <= w_max)],
             'LLd':{i:LLd[i] for i in LLd if LLd[i]['lon_l'] >= w_median}} 
        ]
    else:
        W_four_list = [four]

    H_four_list = []
    for four in W_four_list:
        data, LLd = four['N'], four['LLd']
        H = [LLd[i]['lat_l'] for i in LLd]
        if len(H) > 1:
            h_median = sorted(H)[len(H)//2]
            h_min = min(H)
            h_max = max(H)
            H_four_list.append({
                'N':data[(data.lat < h_median) & (data.lat >= h_min)],
                'LLd':{i:LLd[i] for i in LLd if LLd[i]['lat_u'] <= h_median}
            })
            H_four_list.append({
                'N':data[(data.lat >= h_median) & (data.lat <= h_max)],
                'LLd':{i:LLd[i] for i in LLd if LLd[i]['lat_l'] >= h_median}
            })
        else:
            H_four_list.append(four)
    return H_four_list