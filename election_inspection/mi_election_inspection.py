import argparse 
from data_cleaning.import_data import process_data
from stat_analysis.match_vtd_to_districts import run_matching

def run_analysis():
    '''
    Main function to run election inspection analysis.
    '''

    # Run script to collect and clean data
    process_data()
    
    print("Cleaned csv file outputted to 'data_cleaning/data' directory.\n")
    input('Press any key to continue...')

    # Run scripts to perform analysis
    run_matching()
    print("Created mapping of vtds to new districts and output csvs to "
                                    "'stat_analysis/' directory.\n")
    input('Press any key to continue...')

    exec('stat_analysis/estimation.py')
    print("Created mapping of vtds to new districts and output csvs to"
                                    "'stat_analysis/' directory.\n")
    input('Press any key to continue...')

    exec('stat_analysis/get_geojson.py')
    print("Created geojsons of the estimation results for proposed districts"
                                    "in the 'visual_analysis/' directory.\n")
    input('Press any key to continue...')

    # Create visualization dashboard
    exec('visual_analysis/dash_map.py')
    print("Started visualization dashboard.\n")
    input('Press any key to continue...')