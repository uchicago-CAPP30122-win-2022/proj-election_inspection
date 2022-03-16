import os 
cwd = os.getcwd()
print(cwd)
from mi_election_inspection import run_analysis


if __name__=="__main__":
    run_analysis()