import argparse 
from data_cleaning.import_data import process_data
from stat_analysis.match_vtd_to_districts import run_matching
from stat_analysis.estimation import run_estimation
from stat_analysis.get_geojson import run_get_geojson
#from visual_analysis.dash_map import run_dash
import os

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

    run_estimation()
    print("Created mapping of vtds to new districts and output csvs to"
                                    "'stat_analysis/' directory.\n")
    input('Press any key to continue...')

    run_get_geojson()
    print("Created geojsons of the estimation results for proposed districts"
                                    "in the 'visual_analysis/' directory.\n")
    input('Press any key to continue...')

    # Create visualization dashboard
    exec('election_inspection/visual_analysis/dash_map.py')
    print("Started visualization dashboard.\n")
    input('Press any key to continue...')