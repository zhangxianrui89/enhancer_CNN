"""
Creates the H3K27ac data vs. the new negative non-enhancers data, for all species.
Sets a fixed partition to train, validation and test data for each species.
write all created data samples and labels both as text files and as numpy binary files.
run with python2.7 !!!
"""
import os
import sys
from DataLoaderH3K27acvsNeg import DataLoaderH3K27acvsNeg
# get the directory of the script being run:
base_path = os.path.dirname(os.path.abspath(__file__))
projects_base_path = base_path[:-len('/H3K27ac_vs_negative_data')]
sys.path.insert(0, projects_base_path+'/CNN/')
import test_CNN
import data_handle


def main():
    project = test_CNN.get_project_and_check_arguments(sys.argv, "run_data_loader.py")
    # data_handle.remove_files(project.text_samples_base_dir, ".txt", project.species)
    print "start creating data for project: ", project.project_name
    data_loader = DataLoaderH3K27acvsNeg(project)
    data_loader.get_all_positive_and_negative_samples()
    data_loader.create_data_for_each_species()
    data_loader.create_data_from_all_species_together()
    print "End!"

if __name__ == "__main__":
    main()
