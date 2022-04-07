from base_imports import *

nc_rename = {
    'idu':'idu',
    'first_name':'first',
    'midl_name':'middle',
    'last_name':'last',
    'age':'age',
    'sex_code':'gender',
    'race_desc':'race',
    'birth_place':'birthplace',
    
    'party_cd':'party',
    'area_cd':'area_code',
    'phone_num':'phone',
    'registr_dt':'registration_date',
    'cancellation_dt':'cancel_date',
    'reason_cd':'cancel_reason',
    'status_cd':'status', # 'voter_status_desc', 'voter_status_reason_desc'
    'voter_status_reason_desc':'status_reason', 
    
    'house_num':'house_number',
    'half_code':'half_code',
    'street_dir':'street_direction', # NC
    'street_name':'street_name',
    'street_type_cd':'street_type', # NC
    'street_sufx_cd':'street_sufx_cd',
    
    'state_cd':'state',
    'county_desc':'county',
    'res_city_desc':'city', # mail_city
    'zip_code':'zipcode',
    'precinct_desc':'precinct',
    
    'cong_dist_desc':'congressional',
    'county_commiss_desc':'commissioner',
    'fire_dist_desc':'fire',
    'judic_dist_desc':'judicial',
    'nc_house_desc':'state_house',
    'nc_senate_desc':'state_senate',
    'sanit_dist_desc':'sanitation',
    'rescue_dist_desc':'rescue',
    'school_dist_desc':'school',
    'sewer_dist_desc':'sewer',
    'super_court_desc':'court',
    'township_desc':'township',
    'municipality_desc':'municipality', # munic_dist_desc alt
    'vtd_desc':'voter_district',
    'ward_desc':'ward',
    'water_dist_desc':'water',
    # 'dist_1_desc'
    # 'vtd_desc'
}

def clean_NC(voters, history, date, nc_rename, run_elections=False):
    
    print('  || Generate')
    voters['idu'] = voters['ncid'].astype(str) + voters['voter_reg_num'].astype(str)
    
    print('  || Drop')
    nc_keep = [k for k in nc_rename]
    nc_keep = [k for k in nc_keep if k in voters.columns.values]
    voters = voters[nc_keep]

    print('  || Rename')
    voters = voters.rename(columns=nc_rename)
    
    print('  || Reformat')
    voters['house_number'] = [str(x).strip(' ') for x in voters.house_number]
    voters['half_code'] = [str(x).strip(' ') for x in voters.half_code]
    voters['street_direction'] = [str(x).strip(' ') for x in voters.street_direction]
    voters['street_name'] = [str(x).strip(' ') for x in voters.street_name]
    voters['street_type'] = [str(x).strip(' ') for x in voters.street_type]
    voters['street_sufx_cd'] = [str(x).strip(' ') for x in voters.street_sufx_cd]
    
    voters['cancel_date'] = [str(x).split('-')[0] for x in voters.cancel_date]
    voters['registr_date'] = [str(x).split('-')[0] for x in voters.registration_date]
    voters = voters[voters['cancel_date'].isin(['nan','1900'])]
    
    print('  || Post Generate')
    voters['address'] = voters.house_number + ' ' + voters.half_code + ' ' + voters.street_direction +' ' + voters.street_name + ' ' + voters.street_type + ' ' + voters.street_sufx_cd
    #voters['birthyear'] = int(year) - voters['age'].astype(float) # a.k.a. year minus age at export
    voters['party'] = [str(str(x)[0]) for x in voters['party']]
    
    voters['D'] = (voters.party == 'D')*1
    voters['R'] = (voters.party == 'R')*1
    voters['O'] = (1-voters['D'])*(1-voters['R'])
    
    voters['present_hist'] = voters.idu.isin(history.idu.unique())*1

    if run_elections:
        elections = history.election_desc.unique()
        
        for election in elections:
            election_data = history[history.election_desc == election]
            voters['voted_' + election] = voters.idu.isin(election_data.idu.unique())*1
    
    return voters

