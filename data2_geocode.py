from base_imports import *

    




































# OLD THINGS, WILL USE TO FORMAT AS NC, BUT NOT IN THIS WAY

def PA_geocode(allvoters):
    rename_cols = {'ID Number':'ID_NUM', 'Last Name':'NAME_LAST', 'First Name':'NAME_FIRST',
                   'Gender':'GENDER', 'Registration Date':'REG_DATE', 'Voter Status':'STATUS',
                   'Status Change Date':'STATUS_CHANGE_DATE', 'Party Code':'PARTY',
                   'House Number':'ADDR_NUM', 'Street Name':'ST_NAME', 'City':'CITY',
                   'Zip':'ZIP_CODE', 'Last Vote Date':'LAST_VOTE_DATE', 
                   'Precinct Code':'PRECINCT','Date Last Changed':'DATE_LAST_CHANGED'}
    allvoters = allvoters.rename(columns=rename_cols)

    for col in allvoters.columns.values:
        allvoters.loc[:,col] = [str(x).strip('""') for x in allvoters[col]]
    allvoters['ADDRESS'] = allvoters['ADDR_NUM'] + ' ' + allvoters['ST_NAME']
    
    keep_cols = ['ID_NUM','NAME_LAST','NAME_FIRST','GENDER','DOB',
                    'REG_DATE','STATUS','STATUS_CHANGE_DATE','PARTY',
                    'ADDR_NUM','ST_NAME','CITY','ZIP_CODE',
                    'LAST_VOTE_DATE','PRECINCT','DATE_LAST_CHANGED','ADDRESS']
    pa_election_cols = [x for x in allvoters.columns.values if str(x.split(' ')[0]) in ['2016','2017','2018']]
    allvoters = allvoters[keep_cols+pa_election_cols]

    return allvoters


def PA_unify(pa):
    pa.loc[:,'REG_YEAR'] = [str(i).split('/')[-1] for i in pa['REG_DATE']]
    
    def pa_age(x,year):
        if x == 'nan':
            return 'nan'
        else:
            return int(year) - int(x.split('/')[-1])
    pa.loc[:,'AGE'] = [pa_age(str(i),year) for i in pa['DOB']]
    
    pa_keep_cols = [
        'ID_NUM', 'ADDRESS', 'ADDR_NUM', 'ST_NAME', 'CITY', 'STATE', 'ZIP_CODE', 
        'NAME_LAST', 'NAME_FIRST', 'GENDER', 'DOB', 'AGE',

        'PARTY', 'REG_DATE', 'REG_YEAR', 'STATUS', 
        'STATUS_CHANGE_DATE', 'DATE_LAST_CHANGED', 'LAST_VOTE_DATE', # PA SPECIFIC

        'PRECINCT', 'address_parsed_results', 'block_results', 'countyfp_results', 
        'matchtype_results', 'tract_results', 'lat', 'lon'
    ]
    pa_election_cols = [x for x in allvoters.columns.values if str(x.split(' ')[0]) in ['2016','2017','2018']]
    
    return pa[pa_keep_cols + pa_election_cols]
