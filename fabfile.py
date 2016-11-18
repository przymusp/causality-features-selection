from fabric.api import *

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
    outdir = 'results/' + timeseries.split("/")[-1].split(".")[0]
    local('mkdir -p ' + outdir)

    # guess interpreter type
    methodtype = method.split("/")[-1].split(".")[1]

    local('python ' + method + ' ' + timeseries + ' ' + outdir)



