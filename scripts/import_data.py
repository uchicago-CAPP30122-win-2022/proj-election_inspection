'''
Election Inspection

Christian Jordan, Alejandro Navarrete, Victor Perez

Script to process data and output a csv to be used for model 
estimation.

Author: Christian Jordan
'''

import pandas as pd
import numpy as np
import re


def process_data():
    '''
    Function to process datasets from Redistricing Data Hub and the
    Census Bureau. 

    Output:
        Outputs processed csv file to the 'data' directory.
    '''
    ## Data from Redistricting Data Hub (VTD-2020 level)
    # 2020 election turnout data
    turnout2020_df = pd.read_csv('../data/csv/MI_l2_turnout_stats_vtd20.csv',
                                     header=0)
    turnout2020_df = turnout2020_df.loc[:, ['vtd_geoid20', 'g20201103_reg_all',
                                                        'g20201103_voted_all']]
    turnout2020_df = turnout2020_df.rename(columns={'vtd_geoid20': 'GEOID20',
                                    'g20201103_voted_all': 'total2020_voted'})
    turnout2020_df['turnout2020_registered'] = (
                                    turnout2020_df['total2020_voted'] /
                                    turnout2020_df['g20201103_reg_all'])
    missing_obs = [geoid[-1] != 'Z' for geoid in turnout2020_df['GEOID20']]
    turnout2020_df = turnout2020_df[missing_obs]
    turnout2020_df['GEOID20'] = turnout2020_df['GEOID20'].astype('int64')
    vtd_registered_voters_dict = {row[0]: row[1] 
                                    for _, row in turnout2020_df.iterrows()}
    turnout2020_df = turnout2020_df.drop(['g20201103_reg_all'], axis=1)

    # Lagged 2018 election data (voter turnout in 2018 midterms)
    lagged_2018_elections_df = pd.read_csv('../data/csv/'
                                            'mi_2018_2020_vtd.csv', header=0)
    lagged_2018_elections_df = lagged_2018_elections_df.loc[:, ['GEOID20',
                                    'G18GOVRSCH', 'G18GOVDWHI', 'G18GOVLGEL', 
                                    'G18GOVTSCH', 'G18GOVGKUR', 'G18GOVNBUT']]
    # Turnout in 2018 calculated by summing votes in gubernatorial race
    lagged_2018_elections_df['turnout2018'] = (
                                        lagged_2018_elections_df['G18GOVRSCH']
                                        + lagged_2018_elections_df['G18GOVDWHI']
                                        + lagged_2018_elections_df['G18GOVLGEL']
                                        + lagged_2018_elections_df['G18GOVTSCH']
                                        + lagged_2018_elections_df['G18GOVGKUR']
                                        + lagged_2018_elections_df['G18GOVNBUT'])
    lagged_2018_elections_df = lagged_2018_elections_df.drop(['G18GOVRSCH',
                                    'G18GOVDWHI', 'G18GOVLGEL', 'G18GOVTSCH',
                                    'G18GOVGKUR', 'G18GOVNBUT'], axis=1)
    missing_obs = [geoid[-1] != 'Z' for geoid 
                        in lagged_2018_elections_df['GEOID20']]
    lagged_2018_elections_df = lagged_2018_elections_df[missing_obs]
    lagged_2018_elections_df['GEOID20'] = (lagged_2018_elections_df['GEOID20']
                                                            .astype('int64'))
    lagged_2018_elections_df['turnout2018_registered'] = [row[1] / 
                            vtd_registered_voters_dict[row[0]] 
                            if vtd_registered_voters_dict.get(row[0]) else np.nan
                            for _, row in lagged_2018_elections_df.iterrows()]
    lagged_2018_elections_df = lagged_2018_elections_df.drop(
                                                    ['turnout2018'], axis=1)

    # Ethnic groupings data (percentage of ethnic groupings)
    race_census_df = pd.read_csv('../data/csv/mi_pl2020_vtd.csv', header=0)
    race_census_df = race_census_df.loc[:, ['GEOID20', 'COUNTY', 'VTD', 'POP100',
                                            'P0010002', 'P0010003', 'P0010004', 
                                            'P0010005', 'P0010006', 'P0010007', 
                                            'P0010009', 'P0010026', 'P0010047', 
                                            'P0010063', 'P0010070']]
    race_census_df['total_pop_log'] = np.log(race_census_df['POP100'])
    race_census_df['pop_three_or_more_races'] = (race_census_df['P0010026']
                                                + race_census_df['P0010047']
                                                + race_census_df['P0010063']
                                                + race_census_df['P0010070'])
    race_census_df = race_census_df.rename(columns={'POP100': 'total_pop',
                                            'P0010002': 'pop_one_race',
                                            'P0010003': 'pop_white_alone',
                                            'P0010004': 'pop_black_alone',
                                            'P0010005': 'pop_am_indian_alone',
                                            'P0010006': 'pop_asian_alone',
                                            'P0010007': 'pop_pac_islander_alone',
                                            'P0010009': 'pop_two_races'})
    race_census_df = race_census_df.drop(['P0010026', 'P0010047',
                                        'P0010063', 'P0010070'], axis=1)
    missing_obs = [geoid[-1] != 'Z' for geoid in race_census_df['GEOID20']]
    race_census_df = race_census_df[missing_obs]
    race_census_df['GEOID20'] = race_census_df['GEOID20'].astype('int64')

    # 2020 presidential election race closeness data 
    election2020_closeness_df = pd.read_csv('../data/csv/mi_2020_2020_vtd.csv',
                                                                     header=0)
    # Election closeness calculated by taking difference of top two candidates
    election2020_closeness_df['2020_vote_share_diff'] = abs(
        election2020_closeness_df['G20PRERTRU']
        - election2020_closeness_df['G20PREDBID'])
    election2020_closeness_df = election2020_closeness_df.loc[:,
                                ['GEOID20', '2020_vote_share_diff']]
    missing_obs = [geoid[-1] != 'Z' for geoid in 
                                        election2020_closeness_df['GEOID20']]
    election2020_closeness_df = election2020_closeness_df[missing_obs]
    election2020_closeness_df['GEOID20'] = (election2020_closeness_df['GEOID20']
                                                                .astype('int64'))


    ## Data from Census Bureau (County level)
    # Migration data (percent of county population that either came to or 
    # left the county)
    migration_census_df = pd.read_excel('../data/csv/county-to-county-2015-2019-'
                                        'ins-outs-nets-gross.xlsx',
                                        sheet_name='Michigan',
                                        header=2)
    migration_census_df = migration_census_df.iloc[:, [1, 5, 14]]
    migration_census_df = migration_census_df.rename(columns={
        migration_census_df.columns[0]: 'county_code',
        migration_census_df.columns[1]: 'county_name',
        migration_census_df.columns[2]: 'gross_county_migration'})
    migration_census_df = migration_census_df.dropna()
    migration_census_df['county_code'] = migration_census_df[
        'county_code'].astype('int64')
    migration_census_df['county_name'] = [re.sub(r'(County$)', '',
                                        county).strip() for county in
                                        migration_census_df['county_name']]
    
    # Create a 'county name' to 'county_code' mapping for use below
    county_name_to_code = {row[1]: row[0] for _, row in 
                                            migration_census_df.iterrows()}
    migration_census_df = migration_census_df.drop(['county_name'], axis=1)
    migration_census_df = migration_census_df.groupby('county_code').sum()
    migration_census_df = migration_census_df.reset_index()

    # Create a census tract to 'county_code' mapping for use below
    tract_to_county_df = pd.read_csv('../data/csv/mi_pl2020_t.csv', header=0)
    tract_to_county_df = tract_to_county_df.loc[:, ['GEOID', 'COUNTY']]
    tract_to_county_dict = {row[0]: row[1] for _, row in 
                                                tract_to_county_df.iterrows()}

    # Home ownership data (percent of owner occupied of total housing units)
    home_ownership_census_df = pd.read_csv(
        '../data/csv/ACSDP5Y2018.DP04_data_with_overlays_2022-03-12T164813.csv',
                                                                    header=0)
    home_ownership_census_df = home_ownership_census_df.loc[:, 
                                ['GEO_ID', 'DP04_0001E', 'DP04_0080E']]
    home_ownership_census_df['county_code'] = [tract_to_county_dict[geoid] 
                                if tract_to_county_dict.get(geoid) else np.nan
                                for geoid in home_ownership_census_df['GEO_ID']]
    home_ownership_census_df = (home_ownership_census_df[1:]
                                        .drop(['GEO_ID'], axis=1))
    home_ownership_census_df = home_ownership_census_df.dropna()
    home_ownership_census_df['DP04_0001E'] = (
                        home_ownership_census_df['DP04_0001E'].astype('int64'))
    home_ownership_census_df['DP04_0080E'] = (
                        home_ownership_census_df['DP04_0080E'].astype('int64'))
    home_ownership_census_df = (home_ownership_census_df
                                        .groupby('county_code').sum())
    home_ownership_census_df = home_ownership_census_df.reset_index()
    home_ownership_census_df['c_perc_owner_occupied_house'] = (
                                    home_ownership_census_df['DP04_0080E'] / 
                                    home_ownership_census_df['DP04_0001E'])
    home_ownership_census_df = home_ownership_census_df.drop(['DP04_0001E', 
                                                        'DP04_0080E'], axis=1)
    home_ownership_census_df['county_code'] = (
                        home_ownership_census_df['county_code'].astype('int64'))

    # Population growth data (rate of change from 2018 to 2019)
    pop_2019_census_df = pd.read_csv(
        '../data/csv/ACSDT5Y2019.B01003_data_with_overlays_2021-11-17T211211.csv', 
        header=0)
    pop_2019_census_df = pop_2019_census_df.loc[1:, ['GEO_ID', 'B01003_001E']]
    pop_2018_census_df = pd.read_csv(
        '../data/csv/ACSDT5Y2018.B01003_data_with_overlays_2022-03-15T163934.csv', 
        header=0)
    pop_2018_census_df = pop_2018_census_df.loc[1:, ['GEO_ID', 'B01003_001E']]
    growth_census_df = pop_2019_census_df.merge(
                pop_2018_census_df, on='GEO_ID', suffixes={'_2019', '_2018'})
    growth_census_df['county_code'] = [tract_to_county_dict[geoid] 
                                if tract_to_county_dict.get(geoid) else np.nan
                                for geoid in growth_census_df['GEO_ID']]
    growth_census_df['B01003_001E_2018'] = (growth_census_df['B01003_001E_2018']
                                                                .astype('int64'))
    growth_census_df['B01003_001E_2019'] = (growth_census_df['B01003_001E_2019']
                                                                .astype('int64'))
    growth_census_df = growth_census_df.groupby(['county_code']).sum()
    growth_census_df = growth_census_df.reset_index()
    growth_census_df['c_pop_perc_change'] = (
            (growth_census_df['B01003_001E_2019'] - 
            growth_census_df['B01003_001E_2018']) /
            growth_census_df['B01003_001E_2019'])
    growth_census_df = growth_census_df.drop(
                            ['B01003_001E_2018', 'B01003_001E_2019'], axis=1)

    # Urban population data (percent of population living in an urban area)
    urban_pop_census_df = pd.read_excel('../data/csv/PctUrbanRural_County.xls',
                                         header=0)
    urban_pop_census_df = urban_pop_census_df[urban_pop_census_df['STATENAME'] ==
                                                                    'Michigan']
    urban_pop_census_df = urban_pop_census_df.loc[:, ['COUNTY', 'POP_COU', 
                                                                'POP_URBAN']]
    urban_pop_census_df['c_pop_pct_urban'] = (
                                            urban_pop_census_df['POP_URBAN'] /
                                            urban_pop_census_df['POP_COU'])
    urban_pop_census_df = urban_pop_census_df.drop(['POP_COU', 'POP_URBAN'], 
                                                                        axis=1)
    urban_pop_census_df['COUNTY'] = [int(str(county).lstrip('0'))
                                    for county in urban_pop_census_df['COUNTY']]
    urban_pop_census_df = urban_pop_census_df.rename(columns=
                                                    {'COUNTY': 'county_code'})

    # Income inequality data (gini index per county)
    gini_census_df = pd.read_csv(
                        '../data/csv/ACSDT5Y2019.B19083-2022-03-14T021522.csv',
                        header=0)
    gini_census_df = gini_census_df.iloc[:, [i for i in range(1, 167, 2)]]
    gini_census_df = gini_census_df.transpose()
    gini_census_df = gini_census_df.reset_index()
    gini_census_df.columns = ['county_name', 'c_gini_index']
    gini_census_df['county_name'] = [re.sub(r'(County, Michigan!!Estimate$)', '',
                                            county).strip('. ') for county in
                                        gini_census_df['county_name']]
    gini_census_df['county_code'] = [county_name_to_code[county]
                                    for county in gini_census_df['county_name']]
    gini_census_df = gini_census_df.drop(['county_name'], axis=1)

    # Education data (percent of population that falls within certain 
    # educational levels)
    edu_census_df = pd.read_csv(
                        '.../data/csv/ACSST5Y2019.S1501-2022-03-16T014444.csv',
                        header=0, index_col=0)
    edu_census_df = edu_census_df.iloc[[9, 15], [i for i in range(2, 996, 12)]]
    edu_census_df = edu_census_df.transpose()
    edu_census_df = edu_census_df.reset_index()
    edu_census_df.columns = ['county_name', 'c_perc_hs_grad', 'c_perc_uni_grad']
    edu_census_df['county_name'] = [re.sub(
                                r'(County, Michigan!!Percent!!Estimate$)', '',
                                county).strip('. ') for county in
                                edu_census_df['county_name']]
    edu_census_df['county_code'] = [county_name_to_code[county]
                                    for county in edu_census_df['county_name']]
    edu_census_df = edu_census_df.drop(['county_name'], axis=1)
    edu_census_df['c_perc_hs_grad'] = [float(perc.strip('%')) * 0.01 for perc in 
                                                edu_census_df['c_perc_hs_grad']]
    edu_census_df['c_perc_uni_grad'] = [float(perc.strip('%')) * 0.01 for perc in 
                                                edu_census_df['c_perc_uni_grad']]


    ## VTD to County FIPS code mapping
    vtd_to_county_map = {row[0]: row[1] for _, row in 
                                                race_census_df.iterrows()}
    race_census_df = race_census_df.drop(['COUNTY'], axis=1)

    
    ## Merging of datasets
    participation_df = (turnout2020_df
                    .merge(race_census_df, how='left', on='GEOID20')
                    .merge(lagged_2018_elections_df, how='left', on='GEOID20')
                    .merge(election2020_closeness_df, how='left', on='GEOID20'))
    participation_df['county_code'] = [int(vtd_to_county_map[geoid]) 
                                        for geoid in participation_df['GEOID20']]
    participation_df = (participation_df
                    .merge(migration_census_df, how='left', on='county_code')
                    .merge(urban_pop_census_df, how='left', on='county_code')
                    .merge(growth_census_df, how='left', on='county_code')
                    .merge(home_ownership_census_df, how='left', on='county_code')
                    .merge(gini_census_df, how='left', on='county_code')
                    .merge(edu_census_df, how='left', on='county_code'))


    ## Aggregate VTD population for each county in dictionary
    c_pop_df = participation_df.loc[:, ['county_code', 'total_pop']]
    c_pop_df = c_pop_df.groupby(['county_code']).sum()
    c_pop_df = c_pop_df.reset_index()
    c_pop_dict = {row[0]: row[1] for _, row in c_pop_df.iterrows()}
    # Create county aggregated population column
    participation_df['c_total_pop'] = [c_pop_dict[cc] 
                                for cc in participation_df['county_code']]
    

    ## Final features calculations (transform population totals to percentages)
    participation_df['c_pop_perc_migration'] = (
                                    participation_df['gross_county_migration'] /
                                    participation_df['c_total_pop'])
    participation_df['pop_perc_one_race'] = (
                                    participation_df['pop_one_race'] /
                                    participation_df['total_pop'])
    participation_df['pop_perc_two_races'] = (
                                    participation_df['pop_two_races'] /
                                    participation_df['total_pop'])
    participation_df['pop_perc_three_or_more_races'] = (
                                    participation_df['pop_three_or_more_races'] /
                                    participation_df['total_pop'])
    participation_df['pop_perc_white'] = (
                                    participation_df['pop_white_alone'] /
                                    participation_df['total_pop'])
    participation_df['pop_perc_black'] = (
                                    participation_df['pop_black_alone'] /
                                    participation_df['total_pop'])
    participation_df['pop_perc_am_indian'] = (
                                    participation_df['pop_am_indian_alone'] /
                                    participation_df['total_pop'])
    participation_df['pop_perc_asian'] = (
                                    participation_df['pop_asian_alone'] /
                                    participation_df['total_pop'])
    participation_df['pop_perc_pac_islander'] = (
                                    participation_df['pop_pac_islander_alone'] /
                                    participation_df['total_pop'])
    participation_df = participation_df.drop(['gross_county_migration',
                    'pop_one_race', 'pop_two_races', 'pop_three_or_more_races',
                    'pop_white_alone', 'pop_black_alone', 'pop_am_indian_alone',
                    'pop_asian_alone', 'pop_pac_islander_alone', 'c_total_pop'],
                     axis=1)


    ## Reordering of dataframe
    participation_df = participation_df.rename(columns=
                                                {'county_code': 'COUNTY_FIPS'})
    participation_df = participation_df[['GEOID20', 'VTD', 'COUNTY_FIPS', 
                        'total_pop', 'total_pop_log', 'turnout2018_registered', 
                        '2020_vote_share_diff', 'pop_perc_one_race', 
                        'pop_perc_two_races', 'pop_perc_three_or_more_races', 
                        'pop_perc_white', 'pop_perc_black', 'pop_perc_am_indian', 
                        'pop_perc_asian', 'pop_perc_pac_islander',  
                        'c_pop_pct_urban', 'c_pop_perc_change', 
                        'c_pop_perc_migration', 'c_gini_index', 'c_perc_hs_grad',
                        'c_perc_uni_grad', 'c_perc_owner_occupied_house',  
                        'total2020_voted', 'turnout2020_registered']]


    participation_df.to_csv('../data/participation.csv')


if __name__ == '__main__':
    process_data()