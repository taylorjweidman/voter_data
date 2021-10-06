from base_imports import *

""" Spatial Interpolation """

def return_nc_acs_summary():
    if 'acs_2004_2019.csv' not in os.listdir('data0_raw/census/'):
        ipums = pd.read_csv('data0_raw/census/usa_00034.csv')
        ipums_keepcols = ['year', 'sample', 'statefip', 'countyfip', 'puma', 'rent', 'hhincome', 'valueh', 'perwt', 'sex', 'age', 'race', 'educ', 'empstat', 'occ', 'incwage', 'trantime']
        ipums = ipums[ipums_keepcols]
        ipums = ipums.replace({'age': {'Less than 1 year old':'0','100 (100+ in 1960-1970)':'100', '90 (90+ in 1980 and 1990)': '90'}})
        ipums.age = ipums.age.astype(int)
        ipums = ipums.replace({'race': {'Black/African American/Negro': 'Black', 'Chinese': 'Other', 'Japanese': 'Other', 
                                       'American Indian or Alaska Native': 'Other', 'Other race, nec': 'Other', 
                                       'Other Asian or Pacific Islander': 'Other', 'Two major races': 'Other', 'Three or more major races': 'Other'}})
        ipums = ipums.replace({'educ': {'N/A or no schooling': 'No College', 'Nursery school to grade 4': 'No College', 'Grade 5, 6, 7, or 8': 'No College', 
                                        'Grade 9': 'No College', 'Grade 10': 'No College', 'Grade 11': 'No College', 'Grade 12': 'No College', 
                                        '1 year of college': 'Some College', '2 years of college': 'Some College', '3 years of college': 'Some College',
                                        '4 years of college': 'College', '5+ years of college': 'College'} })
        ipums = ipums[ipums.empstat.isin(['Employed', 'Not in labor force', 'Unemployed'])]

        census_years = [1960,1980,1990,2000]
        census = ipums[ipums.year.isin(census_years)]
        census.to_csv('data0_raw/census/census_1980_2000.csv')
        del census

        acs_years = [2001, 2002, 2003, 2004, 2005, 2006, 2007, 2008, 2009, 2010, 2011, 2012, 2013, 2014, 2015, 2016, 2017, 2018, 2019]
        acs = ipums[ipums.year.isin(acs_years)]
        del ipums
        acs.to_csv('data0_raw/census/acs_2004_2019.csv')
    else:
        acs = pd.read_csv('data0_raw/census/acs_2004_2019.csv')
    
    nc_acs = acs[acs.statefip=='North Carolina']

    education = ['College','Some College','No College']

    yearlist_acs = [x for x in nc_acs.year.unique() if x >=2005]
    nc_acs_summary = {year:np.nan for year in yearlist_acs}

    for year in yearlist_acs:
        nc_year = nc_acs[(nc_acs.year == year)]
        nc_puma_list = [x for x in nc_year.puma.unique() if x >= 0]

        average_data = []
        for puma in nc_puma_list:
            averages,col_names = [puma],['puma']

            subdata = nc_year[(nc_year.puma == puma)]
            population = sum(subdata.perwt)
            white_pop = sum(subdata[subdata.race == 'White'].perwt)
            black_pop = sum(subdata[subdata.race == 'Black'].perwt)
            averages = averages + [population, white_pop, black_pop]
            col_names = col_names + ['POP','WHITE','BLACK']

            subdata = subdata[(subdata.age >= 18)]
            averages = averages + [sum(subdata.perwt)]
            col_names = col_names + ['VOTING_POP']

            subdata = subdata[(subdata.empstat != 'Not in labor force')]
            averages = averages + [sum(subdata.perwt)]
            col_names = col_names + ['LABOR']

            averages = averages + [sum(subdata.age*subdata.perwt)/sum(subdata.perwt), sum(subdata.trantime*subdata.perwt)/sum(subdata.perwt)]
            col_names = col_names + ['AGE', 'TRANTIME']

            for ed_type in education:
                ed_type_data = subdata[subdata.educ == ed_type]
                ed_type = ed_type.upper().replace(' ','_')
                averages = averages + [sum(ed_type_data.perwt)]
                col_names = col_names + [ed_type]

                ed_type_data = ed_type_data[ed_type_data.empstat == 'Employed']
                averages = averages + [sum(ed_type_data.perwt), sum(ed_type_data.incwage*ed_type_data.perwt)/sum(ed_type_data.perwt)]
                col_names = col_names + [ed_type+'_EMPLOYED', ed_type+'_WAGE']

            average_data.append(averages)
        average_data = pd.DataFrame(average_data, columns=col_names)

        nc_acs_summary[year] = average_data
    return nc_acs_summary

def spatial_interpolate(SNd,nc_acs_summary,data_name,print_log,year):
    """
    I want to pick up average characteristics by cross-tab and maybe the neighborhood average characteristics

    To pick up average neighboorhood characteristics, I should use overlapping neighborhoods
        for every neighborhood in the dataset
            overlay the neighborhood on the acs data
            interpolate
            select all voters in this neighborhood
            apply new neighborhood variables to these voters
            add these voters to a list
        concat list and save

    To pick up fuzzing matches, I should use non-overlapping neighborhoods
        for every block group in the acs dataset
            select every voter in the block group
            for every permutation category (age,gender,race)
                select every voter in the category
                assign average characteristics in the acs to them
                add these voters to a list
        concat list and save
    """
    
    nc_year_summary = nc_acs_summary[year]
    if year < 2012:
        puma = gpd.read_file('data0_raw/shapefiles/ipums_puma_2000/ipums_puma_2000.shp')
    if year >= 2012:
        puma = gpd.read_file('data0_raw/shapefiles/ipums_puma_2010/ipums_puma_2010.shp')    
    nc_puma = puma[puma.STATEFIP == '37']
    nc_puma.PUMA = nc_puma.PUMA.astype(int)

    zipcode = gpd.read_file('data0_raw/shapefiles/census_zta_2018/cb_2018_us_zcta510_500k.shp')
    nc_puma = nc_puma.to_crs(zipcode.crs)
    nc_puma_buffer0 = nc_puma.buffer(0)

    SNd_int = {}
    counter,count_total = 0,len(SNd)
    for i in SNd:
        n = gpd.GeoDataFrame(SNd[i])
        n.crs = zipcode.crs

        try:
            n_intersection = nc_puma.intersection(n.iloc[0]['geometry'])
        except:
            n_intersection = nc_puma_buffer0.intersection(n.iloc[0]['geometry'])
        n_intersection = n_intersection[n_intersection.area > 0]
        n_intersection_i = list(n_intersection.index)
        pumas = list(nc_puma.loc[n_intersection_i].PUMA.unique())

        intersected_pumas = nc_puma[nc_puma.PUMA.isin(pumas)]
        weights = (n_intersection.area/intersected_pumas.area).reset_index(drop=True)
        proportions = (n_intersection.area/sum(n_intersection.area)).reset_index(drop=True)

        intersected_pumas_i = list(nc_puma[nc_puma.PUMA.isin(pumas)].PUMA.unique())
        subdata = nc_year_summary[nc_year_summary.puma.isin(intersected_pumas_i)].reset_index(drop=True)

        weight_cols = ['POP', 'WHITE', 'BLACK', 'VOTING_POP', 'LABOR',  'COLLEGE', 'COLLEGE_EMPLOYED', 'SOME_COLLEGE', 'SOME_COLLEGE_EMPLOYED', 'NO_COLLEGE', 'NO_COLLEGE_EMPLOYED']
        proportion_cols = ['AGE', 'TRANTIME', 'COLLEGE_WAGE', 'SOME_COLLEGE_WAGE', 'NO_COLLEGE_WAGE']
        #weighted = [sum(subdata[col]*weights) for col in weight_cols]
        #proportioned = [sum(subdata[col]*proportions) for col in proportion_cols]

        for col in weight_cols:
            n[col] = sum(subdata[col]*weights)
        for col in proportion_cols:
            n[col] = sum(subdata[col]*proportions)

        SNd_int[i] = n
        print_log[data_name]['sublog'] = ['   || Spatial Interpolation '+str(round(100*counter/count_total,2))+'%']
        printer(print_log)
        counter += 1
    print_log[data_name]['sublog'] = []
    
    return SNd_int


def spatial_interpolate_old(SNd,data_name,print_log):
    
    SNd_acs = {}
    acs_population = pd.read_csv('data0_raw/acs/NC/DECENNIALSF12010.P1_data_with_overlays_2020-05-13T144212.csv', header=1)
    zipcode = gpd.read_file('data0_raw/shapefiles/cb_2018_us_zcta510_500k.shp')
    
    def inner_interpolate(SNd):
        count_total = len(SNd)
        counter = 0
        for i in SNd:
            n = gpd.GeoDataFrame(SNd[i]) # eventually this will be returned from GEOd
            n.crs = zipcode.crs
            
            acs_ZCTA = [x.strip('ZCTA5 ').strip(', North Carolina') for x in acs_population['Geographic Area Name']]
            acs_population['ZCTA5CE10_r'] = acs_ZCTA
            acs = zipcode[zipcode['ZCTA5CE10'].isin(acs_ZCTA)].reset_index(drop=True)
            acs = acs.merge(acs_population[['Total','ZCTA5CE10_r']], left_on='ZCTA5CE10', right_on='ZCTA5CE10_r')
            acs_intersection_list = acs.intersection(n.iloc[0]['geometry'])
            acs_intersection = acs_intersection_list[acs_intersection_list.area > 0]
            acs_intersection_index = acs_intersection.index
            intersected_acs = acs[acs.index.isin(acs_intersection_index)]
            intersected_acs['intersection'] = acs_intersection
            intersected_acs['intersection_ratio'] = acs_intersection.area / intersected_acs.area
            #intersected_acs['perc_land'] = intersected_acs['ALAND10']/(intersected_acs['ALAND10']+intersected_acs['AWATER10'])
            # I can do better, by adjusting for water area
            intersected_acs['pop_impute'] = intersected_acs['intersection_ratio']*intersected_acs['Total']
            n['pop_impute'] = sum(intersected_acs['pop_impute'])

            SNd_acs[i] = n
            print_log[data_name]['sublog'] = ['   || Spatial Interpolation '+str(round(100*counter/count_total,2))+'%']
            printer(print_log)
            counter += 1
    
    inner_interpolate(SNd)
    
    #m = mp.Manager()
    #event = m.Event()
    #pool = mp.Pool(processes = 8)
    #pool.map(spatial_interpolate,I)
    
    return SNd_acs


""" ACS? """


state_names = ["Alabama", "Arkansas", "Arizona", "California", "Colorado", "Connecticut", "Delaware", "Florida", "Georgia","Hawaii", "Iowa", "Idaho", "Illinois", 
               "Indiana", "Kansas", "Kentucky", "Louisiana", "Massachusetts", "Maryland", "Maine", "Michigan", "Minnesota", "Missouri", "Mississippi", "Montana", "North Carolina", 
               "North Dakota", "Nebraska", "New Hampshire", "New Jersey", "New Mexico", "Nevada", "New York", "Ohio", "Oklahoma", "Oregon", "Pennsylvania", 
               "Rhode Island", "South Carolina", "South Dakota", "Tennessee", "Texas", "Utah", "Virginia", "Vermont", "Washington", "Wisconsin", "West Virginia", "Wyoming"]


county_icp_dict = {10:'Alamance', 30:'Alexander', 50:'Alleghany', 70:'Anson', 90:'Ashe', 110:'Avery', 130:'Beaufort', 150:'Bertie', 170:'Bladen', 190:'Brunswick', 
                   210:'Buncombe', 230:'Burke', 250:'Cabarrus', 270:'Caldwell', 290:'Camden', 310:'Carteret', 330:'Caswell', 350:'Catawba', 370:'Chatham', 390:'Cherokee',
                   410:'Chowan', 430:'Clay', 450:'Cleveland', 470:'Columbus', 490:'Craven', 510:'Cumberland', 530:'Currituck', 550:'Dare', 570:'Davidson', 590:'Davie',
                   610:'Duplin', 630:'Durham', 650:'Edgecombe', 670:'Forsyth', 690:'Franklin', 710:'Gaston', 730:'Gates', 750:'Graham', 770:'Granville', 790:'Greene',
                   810:'Guilford', 830:'Halifax', 850:'Harnett', 870:'Haywood', 890:'Henderson', 910:'Hertford', 930:'Hoke', 950:'Hyde', 970:'Iredell', 990:'Jackson', 
                   1010:'Johnston', 1030:'Jones', 1050:'Lee', 1070:'Lenoir', 1090:'Lincoln', 1110:'McDowell', 1130:'Macon', 1150:'Madison', 1170:'Martin', 1190:'Mecklenburg', 
                   1210:'Mitchell', 1230:'Montgomery', 1250:'Moore', 1270:'Nash', 1290:'New Hanover', 1310:'Northampton', 1330:'Onslow', 1350:'Orange', 1370:'Pamlico', 1390:'Pasquotank', 
                   1410:'Pender', 1430:'Perquimans', 1450:'Person', 1470:'Pitt', 1490:'Polk', 1510:'Randolph', 1530:'Richmond', 1550:'Robeson', 1570:'Rockingham', 1590:'Rowan',
                   1610:'Rutherford', 1630:'Sampson', 1650:'Scotland', 1670:'Stanly', 1690:'Stokes', 1710:'Surry', 1730:'Swain', 1750:'Transylvania', 1770:'Tyrrell', 1790:'Union', 
                   1810:'Vance', 1830:'Wake', 1835:'Walton', 1850:'Warren', 1870:'Washington', 1890:'Watauga', 1910:'Wayne', 1930:'Wilkes', 1950:'Wilson', 1970:'Yadkin', 1990:'Yancey'}

def rename_columns(col,year):
    def sub_rename(col):
        if 'County' in col:
            return 'County'
        if col == 'state':
            return 'state'
        if 'Clinton' in col:
            return 'D'+'_'+str(year)
        if 'Obama' in col:
            return 'D'+'_'+str(year)
        if 'Obama' in col:
            return 'D'+'_'+str(year)
        if 'Gore' in col:
            return 'D'+'_'+str(year)
        if 'Gore' in col:
            return 'D'+'_'+str(year)
        
        if 'Unpledged ElectorsDemocratic' in col:
            return 'O'
        if 'Social Democratic' in col:
            return 'O'
        if 'Independent Democratic' in col:
            return 'O'
        if 'Southern Democratic' in col:
            return 'O'
        if ' Democratic' in col:
            return 'O'
        if ' Democrat' in col:
            return 'O'
        if 'Democrat' in col:
            return 'D'+'_'+str(year)
        if 'Democratic' in col:
            return 'D'+'_'+str(year)
        
        if 'Trump' in col:
            return 'R'+'_'+str(year)
        if 'Romney' in col:
            return 'R'+'_'+str(year)
        if 'McCain' in col:
            return 'R'+'_'+str(year)
        if 'Bush' in col:
            return 'R'+'_'+str(year)

        if 'Black and Tan Republican' in col:
            return 'O'
        if 'Republican' in col:
            return 'R'+'_'+str(year)
        
        else:
            return 'O'
        
    if type(col) == tuple:
        for subcol in col:
            return sub_rename(subcol)
    if type(col) == str:
        return sub_rename(col)