from election_inspection.data_cleaning.import_data import process_data
from election_inspection.stat_analysis.match_vtd_to_districts import run_matching
from election_inspection.stat_analysis.estimation import run_estimation
from election_inspection.stat_analysis.get_geojson import run_get_geojson
from election_inspection.visual_analysis.dash_map import run_dash
import os


def run_analysis():
    '''
    Main function to run election inspection analysis.
    '''

    # Clean directories of old run data
    old_data = ['election_inspection/data_cleaning/participation_dataset.csv', 
                'district_map.html', 'election_inspection/stat_analysis/vtd_results.csv']
    for file in old_data:
        if os.path.exists(file):
            os.remove(file)

    map_names = ['apple', 'birch', 'chestnut', 'lange', 'szetela']
    for map_name in map_names:
        joined = 'election_inspection/stat_analysis/' + map_name + '_vtd_joined.csv'
        results = 'election_inspection/stat_analysis/' + map_name + '_results.csv'
        if os.path.exists(joined):
            os.remove(joined)
            os.remove(results)

    # Run script to collect and clean data
    process_data()
    print("Cleaned csv file outputted to 'data_cleaning/data' directory.\n")
    input('Press enter to continue...')

    # Run scripts to perform analysis
    print("Creating mapping of vtds to new districts and output csvs to "
                                    "'stat_analysis/' directory.\n")
    run_matching()
    input('Press enter to continue...')

    print("Estimating the regression model of voter turnout and outputting csvs to"
                                    "'stat_analysis/' directory.\n")
    run_estimation()
    input('Press enter to continue...')

    print("Creating geojsons of the estimation results for proposed districts "
                                    "in the 'visual_analysis/' directory.\n")
    run_get_geojson()    
    input('Press enter to continue...')

    # Create visualization dashboard
    print("Starting visualization dashboard.\n")
    print("Select option to open dashboard in browser...\n\n\n\n")
    run_dash()
