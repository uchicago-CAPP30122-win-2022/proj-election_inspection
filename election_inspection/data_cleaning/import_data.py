'''
Election Inspection

Christian Jordan, Alejandro Navarrete, Victor Perez

Script to process data and output a csv to be used for model 
estimation.

Author: Christian Jordan
'''

from election_inspection.data_cleaning.census_data_collector import CensusQuery
import pandas as pd
import numpy as np


def process_data():
    '''
    Function to process datasets from Redistricing Data Hub and the
    Census Bureau. 

    Output:
        Outputs processed csv file to the 'data' directory.
    '''

    ## Data from Redistricting Data Hub (VTD-2020 level)
    # 2020 election turnout data
    turnout2020_df = pd.read_csv('election_inspection/data_cleaning/data/MI_l2_turnout_stats_vtd20.csv',
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
    lagged_2018_elections_df = pd.read_csv('election_inspection/data_cleaning/data/'
                                            'mi_2018_2020_vtd.csv', header=0)
    lagged_2018_elections_df = lagged_2018_elections_df.loc[:, ['GEOID20',
                                    'G18GOVRSCH', 'G18GOVDWHI', 'G18GOVLGEL', 
                                    'G18GOVTSCH', 'G18GOVGKUR', 'G18GOVNBUT']]
    # Turnout in 2018 calculated by summing votes in gubernatorial race
    lagged_2018_elections_df['tot_turnout2018'] = (
                                        lagged_2018_elections_df['G18GOVRSCH']
                                        + lagged_2018_elections_df['G18GOVDWHI']
                                        + lagged_2018_elections_df['G18GOVLGEL']
                                        + lagged_2018_elections_df['G18GOVTSCH']
                                        + lagged_2018_elections_df['G18GOVGKUR']
                                        + lagged_2018_elections_df['G18GOVNBUT'])
    # Election closeness calculated by taking difference of top two candidates
    lagged_2018_elections_df['election2018_closeness'] = (
                                        lagged_2018_elections_df['G18GOVRSCH']
                                        + lagged_2018_elections_df['G18GOVDWHI'])
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

    # Ethnic groupings data (percentage of ethnic groupings)
    race_census_df = pd.read_csv(
            'election_inspection/data_cleaning/data/mi_pl2020_vtd.csv', header=0)
    race_census_df = race_census_df.loc[:, ['GEOID20', 'COUNTY', 'VTD', 'POP100',
                                            'P0010002', 'P0010003', 'P0010004', 
                                            'P0010005', 'P0010006', 'P0010007', 
                                            'P0010009', 'P0010026', 'P0010047', 
                                            'P0010063', 'P0010070']]
    race_census_df['total_pop_log'] = [np.log(log_pop) if log_pop else 0 
                                        for log_pop in race_census_df['POP100']]
    race_census_df['pop_three_or_more_races'] = (race_census_df['P0010026']
                                                + race_census_df['P0010047']
                                                + race_census_df['P0010063']
                                                + race_census_df['P0010070'])
    race_census_df = race_census_df.rename(columns={'POP100': 'total_pop',
                                            'P0010002': 'pop_one_race',
                                            'P0010003': 'tot_pop_white',
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


    ## 2019 Data from Census Bureau (County level data)
    # Home ownership data (percent of owner occupied of total housing units)
    HomeOwnershipQuery = CensusQuery()
    home_ownership_census_df = HomeOwnershipQuery.retrieve_data(
                    2019, 'acs/acs5', ['B25001_001E', 'B25003_002E'], 'county', 
                    'owner occupied housing')
    if home_ownership_census_df is None:
        home_ownership_census_df = HomeOwnershipQuery.retry_retrieval()
    # Clean data
    home_ownership_census_df = home_ownership_census_df.astype('int')
    home_ownership_census_df['c_perc_owner_occupied_house'] = (
                                    home_ownership_census_df['B25003_002E'] / 
                                    home_ownership_census_df['B25001_001E'])
    home_ownership_census_df = home_ownership_census_df.drop(['B25003_002E', 
                                                    'B25001_001E'], axis=1)

    # Population growth data (rate of change from 2018 to 2019)
    Pop2019Query = CensusQuery()
    pop_2019_census_df = Pop2019Query.retrieve_data(2019, 'acs/acs5', 
                                ['B01003_001E'], 'county', '2019 population')
    if pop_2019_census_df is None:
        pop_2019_census_df = Pop2019Query.retry_retrieval()
    Pop2018Query = CensusQuery()
    pop_2018_census_df = Pop2018Query.retrieve_data(2018, 'acs/acs5', 
                                ['B01003_001E'], 'county', '2018 population')
    if pop_2018_census_df is None:
        pop_2018_census_df = Pop2018Query.retry_retrieval()
    # Clean data
    growth_census_df = pop_2019_census_df.merge(
                pop_2018_census_df, on='county', suffixes=('_2019', '_2018'))
    growth_census_df = growth_census_df.astype('int')
    growth_census_df['c_pop_perc_change'] = (
                            (growth_census_df['B01003_001E_2019'] - 
                            growth_census_df['B01003_001E_2018']) /
                            growth_census_df['B01003_001E_2019'])
    growth_census_df = growth_census_df.rename(
                                columns={'B01003_001E_2019': 'c_total_pop'})
    growth_census_df = growth_census_df.drop(['B01003_001E_2018'], axis=1)

    # Urban population data (percent of population living in an urban area)
    UrbanPopQuery = CensusQuery()
    urban_pop_census_df = UrbanPopQuery.retrieve_data(2020, 'pdb/statecounty', 
                ['Tot_Population_CEN_2010', 'URBANIZED_AREA_POP_CEN_2010'], 
                'county', 'urban population')
    if urban_pop_census_df is None:
        urban_pop_census_df = UrbanPopQuery.retry_retrieval()
    # Clean data
    urban_pop_census_df = urban_pop_census_df.astype('int')
    urban_pop_census_df['c_pop_perc_urban'] = (
                        urban_pop_census_df['URBANIZED_AREA_POP_CEN_2010'] /
                        urban_pop_census_df['Tot_Population_CEN_2010'])
    urban_pop_census_df = urban_pop_census_df.rename(
                        columns={'URBANIZED_AREA_POP_CEN_2010': 'c_tot_urban_pop'})
    urban_pop_census_df = urban_pop_census_df.drop(
                                        ['Tot_Population_CEN_2010'], axis=1)
    
    # Migration data (population that moved in or moved out of county)
    MigrationQuery = CensusQuery()
    migration_census_df = MigrationQuery.retrieve_data(2019, 'acs/flows', 
                            ['MOVEDIN', 'MOVEDOUT'], 'county', 'migration')
    if migration_census_df is None:
        migration_census_df = MigrationQuery.retry_retrieval()
    # Clean data
    migration_census_df = migration_census_df.fillna(0)
    migration_census_df = migration_census_df.astype('int')
    migration_census_df['gross_county_migration'] = (
                                [row['MOVEDIN'] + row['MOVEDOUT']
                                for _, row in migration_census_df.iterrows()])
    migration_census_df = migration_census_df.drop(['MOVEDIN', 'MOVEDOUT'],
                                                                    axis=1)
    migration_census_df = migration_census_df.groupby('county').sum()
    migration_census_df = migration_census_df.reindex()

    # Income inequality data (gini index per county)
    GiniIndexQuery = CensusQuery()
    gini_census_df = GiniIndexQuery.retrieve_data(2019, 'acs/acs5', 
                                    ['B19083_001E'], 'county', 'gini index')
    if gini_census_df is None:
        gini_census_df = GiniIndexQuery.retry_retrieval()
    # Clean data
    gini_census_df.county = gini_census_df.county.astype('int')
    gini_census_df = gini_census_df.rename(columns={'B19083_001E': 'c_gini_index'})  

    # Education data (population that falls within certain educational levels)
    EduQuery = CensusQuery()
    edu_census_df = EduQuery.retrieve_data(2019, 'acs/acs5', ['B15003_001E', 
                                'B15003_017E', 'B15003_022E', 'B15003_023E', 
                                'B15003_024E', 'B15003_025E'], 'county', 
                                'education')
    if edu_census_df is None:
        edu_census_df = EduQuery.retry_retrieval()
    # Clean data
    edu_census_df = edu_census_df.astype('int')
    edu_census_df['c_perc_hs_grad'] = (edu_census_df['B15003_017E'] /
                                        edu_census_df['B15003_001E'])
    edu_census_df['c_perc_uni_grad'] = ((edu_census_df['B15003_022E'] +
                                        edu_census_df['B15003_023E'] +
                                        edu_census_df['B15003_024E'] +
                                        edu_census_df['B15003_025E']) /
                                        edu_census_df['B15003_001E'])
    edu_census_df = edu_census_df.rename(
                            columns={'B15003_017E': 'c_tot_hs_grad'})
    edu_census_df = edu_census_df.drop(['B15003_001E', 
                                        'B15003_022E', 'B15003_023E', 
                                        'B15003_024E', 'B15003_025E'],
                                        axis=1)


    ## VTD to County FIPS code mapping
    vtd_to_county_map = {row[0]: row[1] for _, row in 
                                                race_census_df.iterrows()}
    race_census_df = race_census_df.drop(['COUNTY'], axis=1)

    
    ## Merging of datasets
    participation_df = (turnout2020_df
                    .merge(race_census_df, how='left', on='GEOID20')
                    .merge(lagged_2018_elections_df, how='left', on='GEOID20'))
    participation_df['county'] = [int(vtd_to_county_map[geoid]) 
                                        for geoid in participation_df['GEOID20']]
    participation_df = (participation_df
                    .merge(migration_census_df, how='left', on='county')
                    .merge(urban_pop_census_df, how='left', on='county')
                    .merge(growth_census_df, how='left', on='county')
                    .merge(home_ownership_census_df, how='left', on='county')
                    .merge(gini_census_df, how='left', on='county')
                    .merge(edu_census_df, how='left', on='county'))
 

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
                                    participation_df['tot_pop_white'] /
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
    participation_df = participation_df.drop(['VTD', 'county', 
                    'gross_county_migration', 'pop_one_race', 'pop_two_races', 
                    'pop_three_or_more_races', 'pop_black_alone', 
                    'pop_am_indian_alone', 'pop_asian_alone', 
                    'pop_pac_islander_alone', 'c_total_pop', 'tot_pop_white', 
                    'tot_turnout2018', 'c_tot_hs_grad', 'c_tot_urban_pop'], 
                    axis=1)


    ## Reordering of dataframe
    participation_df = participation_df[['GEOID20',  
                        'total_pop', 'total_pop_log', 'turnout2018_registered', 
                        'election2018_closeness', 'pop_perc_one_race', 
                        'pop_perc_two_races', 'pop_perc_three_or_more_races', 
                        'pop_perc_white', 'pop_perc_black', 'pop_perc_am_indian', 
                        'pop_perc_asian', 'pop_perc_pac_islander',  
                        'c_pop_perc_urban', 'c_pop_perc_change', 
                        'c_pop_perc_migration', 'c_gini_index', 'c_perc_hs_grad',
                        'c_perc_uni_grad', 'c_perc_owner_occupied_house',  
                        'total2020_voted', 'turnout2020_registered']]


    participation_df.to_csv(
        'election_inspection/data_cleaning/participation_dataset.csv', mode='x', index=False)


if __name__ == '__main__':
    process_data()