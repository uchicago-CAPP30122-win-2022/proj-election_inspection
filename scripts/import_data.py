import pandas as pd
import numpy as np
import re

# Data import and cleaning

# Data from Redistricting Data Hub (VTD-2020 level)

# 2020 election turnout data
turnout2020_df = pd.read_csv('../data/csv/MI_l2_turnout_stats_vtd20.csv', header=0)
turnout2020_df = turnout2020_df.loc[:, ['vtd_geoid20', 'g20201103_reg_all',
                                        'g20201103_voted_all']]
turnout2020_df = turnout2020_df.rename(columns={'vtd_geoid20': 'GEOID20',
                                                'g20201103_voted_all': 'total2020_voted'})
turnout2020_df['turnout2020_registered'] = (turnout2020_df['total2020_voted'] /
                                            turnout2020_df['g20201103_reg_all'])
turnout2020_df = turnout2020_df.drop(['g20201103_reg_all'], axis=1)
missing_obs = [geoid[-1] != 'Z' for geoid in turnout2020_df['GEOID20']]
turnout2020_df = turnout2020_df[missing_obs]
turnout2020_df['GEOID20'] = turnout2020_df['GEOID20'].astype('int64')

# Ethnic groupings data
race_census_df = pd.read_csv('../data/csv/mi_pl2020_vtd.csv', header=0)
race_census_df = race_census_df.loc[:, ['GEOID20', 'COUNTY', 'VTD', 'POP100',
                                        'P0010002', 'P0010003', 'P0010004', 'P0010005',
                                        'P0010006', 'P0010007', 'P0010009', 'P0010026',
                                        'P0010047', 'P0010063', 'P0010070']]
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
                                      'P0010063', 'P0010070'],
                                     axis=1)
missing_obs = [geoid[-1] != 'Z' for geoid in race_census_df['GEOID20']]
race_census_df = race_census_df[missing_obs]
race_census_df['GEOID20'] = race_census_df['GEOID20'].astype('int64')

# Lagged election data
lagged_2018_elections_df = pd.read_csv('../data/csv/mi_2018_2020_vtd.csv', header=0)
lagged_2018_elections_df = lagged_2018_elections_df.loc[:, ['GEOID20',
                                'G18GOVRSCH', 'G18GOVDWHI', 'G18GOVLGEL', 'G18GOVTSCH',
                                'G18GOVGKUR', 'G18GOVNBUT']]
# Turnout in 2018 calculated by summing votes in gubernatorial race
lagged_2018_elections_df['turnout2018'] = (lagged_2018_elections_df['G18GOVRSCH']
                                            + lagged_2018_elections_df['G18GOVDWHI']
                                            + lagged_2018_elections_df['G18GOVLGEL']
                                            + lagged_2018_elections_df['G18GOVTSCH']
                                            + lagged_2018_elections_df['G18GOVGKUR']
                                            + lagged_2018_elections_df['G18GOVNBUT'])
lagged_2018_elections_df = lagged_2018_elections_df.drop(['G18GOVRSCH',
                                'G18GOVDWHI', 'G18GOVLGEL', 'G18GOVTSCH',
                                'G18GOVGKUR', 'G18GOVNBUT'], axis=1)
missing_obs = [geoid[-1] != 'Z' for geoid in lagged_2018_elections_df['GEOID20']]
lagged_2018_elections_df = lagged_2018_elections_df[missing_obs]
lagged_2018_elections_df['GEOID20'] = lagged_2018_elections_df['GEOID20'].astype('int64')

# Election race closeness data
election2020_closeness_df = pd.read_csv('../data/csv/mi_2020_2020_vtd.csv', header=0)
election2020_closeness_df['2020_vote_share_diff'] = abs(
    election2020_closeness_df['G20PRERTRU']
    - election2020_closeness_df['G20PREDBID'])
election2020_closeness_df = election2020_closeness_df.loc[:,
                            ['GEOID20', '2020_vote_share_diff']]
missing_obs = [geoid[-1] != 'Z' for geoid in election2020_closeness_df['GEOID20']]
election2020_closeness_df = election2020_closeness_df[missing_obs]
election2020_closeness_df['GEOID20'] = election2020_closeness_df['GEOID20'].astype('int64')

# Data from Census Bureau (County level)

# Migration data
migration_census_df = pd.read_excel('../data/csv/county-to-county-2015-2019-ins-outs'
                                    '-nets-gross.xlsx',
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
# Create a 'county name' to 'county code' mapping for later use
county_name_to_code = {row[1]: row[0] for _, row in migration_census_df.iterrows()}
migration_census_df = migration_census_df.drop(['county_name'], axis=1)
migration_census_df = migration_census_df.groupby('county_code').sum()
migration_census_df = migration_census_df.reset_index()

# Population growth data
growth_census_df = pd.read_excel('../data/csv/co-est2019-annchg-26.xlsx', skiprows=2,
                                 header=0)
growth_census_df = growth_census_df.iloc[:, [0, 4]]
growth_census_df = growth_census_df.dropna()
growth_census_df = growth_census_df.rename(columns={
    growth_census_df.columns[0]: 'county_name',
    growth_census_df.columns[1]: 'c_pop_perc_change'})
growth_census_df = growth_census_df.drop([2], axis=0)
growth_census_df['county_name'] = [re.sub(r'(County, Michigan$)', '',
                                          county).strip('. ') for county in
                                   growth_census_df['county_name']]
growth_census_df['county_code'] = [county_name_to_code[county]
                                   for county in growth_census_df['county_name']]
growth_census_df = growth_census_df.drop(['county_name'], axis=1)

# Home ownership data
# Still working on code
home_ownership_census_df = pd.read_csv('../data/csv/ACSDP1Y2019.DP04-2022-03-11T175751.csv',
                                       header=0)

# Urban population data
urban_pop_census_df = pd.read_excel('../data/csv/PctUrbanRural_County.xls', header=0)
urban_pop_census_df = urban_pop_census_df[urban_pop_census_df['STATENAME']
                                          == 'Michigan']
urban_pop_census_df = urban_pop_census_df.loc[:, ['COUNTY',
                                                  'POP_COU',
                                                  'POP_URBAN']]
urban_pop_census_df['c_pop_pct_urban'] = (urban_pop_census_df['POP_URBAN'] /
                                        urban_pop_census_df['POP_COU'])
urban_pop_census_df = urban_pop_census_df.drop(['POP_COU', 'POP_URBAN'], axis=1)
urban_pop_census_df['COUNTY'] = [int(str(county).lstrip('0'))
                                 for county in urban_pop_census_df['COUNTY']]
urban_pop_census_df = urban_pop_census_df.rename(columns={'COUNTY': 'county_code'})

# Income inequality data
# Still working on code
gini_census_df = pd.read_csv('../data/csv/ACSDT1Y2019.B19083-2022-03-11T182331.csv',
                             header=0)

# Mappings for data joining

# VTD to County FIPS code mapping
vtd_to_county_map = {row[0]: row[1] for _, row in race_census_df.iterrows()}
race_census_df = race_census_df.drop(['COUNTY'], axis=1)

# Census tract to County FIPS code mapping


# Merge datasets
participation_df = (turnout2020_df.merge(race_census_df, how='left', on='GEOID20')
                    .merge(lagged_2018_elections_df, how='left', on='GEOID20')
                    .merge(election2020_closeness_df, how='left', on='GEOID20'))
participation_df['county_code'] = [int(vtd_to_county_map[geoid]) for geoid in participation_df['GEOID20']]

participation_df = (participation_df.merge(migration_census_df, how='left', on='county_code')
                    .merge(urban_pop_census_df, how='left', on='county_code')
                    .merge(growth_census_df, how='left', on='county_code'))
participation_df['c_pop_perc_migration'] = (participation_df['gross_county_migration'] /
                                          participation_df['total_pop'])
participation_df['pop_perc_one_race'] = (participation_df['pop_one_race'] /
                                         participation_df['total_pop'])
participation_df['pop_perc_two_races'] = (participation_df['pop_two_races'] /
                                          participation_df['total_pop'])
participation_df['pop_perc_three_or_more_races'] = (participation_df['pop_three_or_more_races'] /
                                                    participation_df['total_pop'])
participation_df['pop_perc_white'] = (participation_df['pop_white_alone'] /
                                      participation_df['total_pop'])
participation_df['pop_perc_black'] = (participation_df['pop_black_alone'] /
                                      participation_df['total_pop'])
participation_df['pop_perc_am_indian'] = (participation_df['pop_am_indian_alone'] /
                                          participation_df['total_pop'])
participation_df['pop_perc_asian'] = (participation_df['pop_asian_alone'] /
                                      participation_df['total_pop'])
participation_df['pop_perc_pac_islander'] = (participation_df['pop_pac_islander_alone'] /
                                             participation_df['total_pop'])

participation_df = participation_df.drop(['gross_county_migration',
                'pop_one_race', 'pop_two_races', 'pop_three_or_more_races',
                'pop_white_alone', 'pop_black_alone', 'pop_am_indian_alone',
                'pop_asian_alone', 'pop_pac_islander_alone'], axis=1)

participation_df = participation_df.rename(columns={'county_code': 'COUNTY_FIPS'})
participation_df = participation_df[['GEOID20', 'VTD', 'total_pop', 'total_pop_log',
                                     'turnout2018', '2020_vote_share_diff', 'pop_perc_one_race',
                                     'pop_perc_two_races', 'pop_perc_three_or_more_races',
                                     'pop_perc_white', 'pop_perc_black',
                                     'pop_perc_am_indian', 'pop_perc_asian',
                                     'pop_perc_pac_islander', 'COUNTY_FIPS',
                                     'c_pop_pct_urban', 'c_pop_perc_change',
                                     'c_pop_perc_migration', 'total2020_voted',
                                     'turnout2020_registered']]

participation_df.to_csv('participation.csv')