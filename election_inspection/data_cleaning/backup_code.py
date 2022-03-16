
   #     migration_census_df = pd.read_excel('../data/csv/county-to-county-2015-2019-'
    #                                         'ins-outs-nets-gross.xlsx',
    #                                         sheet_name='Michigan',
    #                                         header=2)
    #     migration_census_df = migration_census_df.iloc[:, [1, 5, 14]]
    #     migration_census_df = migration_census_df.rename(columns={
    #         migration_census_df.columns[0]: 'county_code',
    #         migration_census_df.columns[1]: 'county_name',
    #         migration_census_df.columns[2]: 'gross_county_migration'})
    # migration_census_df = migration_census_df.dropna()
    # migration_census_df.county = (migration_census_df.county.astype('int'))
    # migration_census_df['county_name'] = [re.sub(r'(County$)', '',
    #                                     county).strip() for county in
    #                                     migration_census_df['county_name']]

    
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

    # Education data (percent of county population that falls within certain 
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
