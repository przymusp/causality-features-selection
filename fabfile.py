from fabric.api import *
import glob
import os

__RESULTS_DIRECTORY_PREFIX='results/'

def update_python_requirements():
    local('pipreqs --force .')

def get_uci_dataset():
    with lcd("src/tools/download_uci_ml/"):
        local("scrapy crawl uci")

def run_selection(method, timeseries):
    """Runs selection method on a timeseries file

    :method: path to selection method
    :timeseries: path to timeseries file
    :returns: None

    """

    # create output directory
    outdir = __RESULTS_DIRECTORY_PREFIX + 'selection/' + timeseries.split("/")[-1].split(".")[0]
    local('mkdir -p ' + outdir)

    # guess interpreter type
    methodtype = method.split("/")[-1].split(".")[1]

    # TODO: maybe use Shebang approach for all scripts

    with shell_env(PYTHONPATH="$PYTHONPATH:src/"):
        local(' python ' + method + ' ' + timeseries + ' ' + outdir)


def run_prediction(timeseries, method = "src/prediction/prediction.R", ):
    # create output directory
    selection_step_directory = __RESULTS_DIRECTORY_PREFIX + 'selection/' + timeseries.split("/")[-1].split(".")[0]
    outdir = __RESULTS_DIRECTORY_PREFIX + 'prediction/' + timeseries.split("/")[-1].split(".")[0] + "/"
    local('mkdir -p ' + outdir)

    method = os.path.abspath(method)
    outdir = os.path.abspath(outdir)

    files = glob.glob(selection_step_directory + "/*.csv")
    with settings(warn_only=True), lcd("src/prediction/"):
        for f in files:
            f_in = os.path.abspath(f)
            local("Rscript " +" ".join([method, f_in, outdir]))



