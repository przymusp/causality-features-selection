from fabric.api import *
import glob
import os

__RESULTS_DIRECTORY_PREFIX='results/'

def update_python_requirements():
    local('pipreqs --force .')

def get_uci_dataset():
    with lcd("src/tools/download_uci_ml/"):
        local("scrapy crawl uci")

def __run_method(method, timeseries, method_prefix):
    """Runs any method on a timeseries file

    :method: path to the method
    :timeseries: path to timeseries file
    :returns: None

    """

    # create output directory
    outdir = __RESULTS_DIRECTORY_PREFIX + method_prefix + timeseries.split("/")[-1].split(".")[0]
    local('mkdir -p ' + outdir)

    # guess interpreter type
    methodtype = method.split("/")[-1].split(".")[1]

    # Select runner to run script (R or Python)
    _run = run_Python_method
    if methodtype == "R":
        _run = run_R_method
    _run([method, timeseries, outdir])

def pre_selection(timeseries, methods=None):

    """Runs pre_selection methods found in src/pre_selection on a timeseries file

    :timeseries: path to timeseries file
    :methods: globing expresion in quotes for methods selection
    :returns: None

    """
    __run_methods(methods, timeseries, 'pre_selection')

def selection(timeseries, methods=None):

    """Runs selection methods found in src/selection on a timeseries file

    :timeseries: path to timeseries file
    :methods: globing expresion in quotes for methods selection
    :returns: None

    """
    __run_methods(methods, timeseries, 'selection')

def __run_methods(methods, timeseries, methods_prefix):

    if methods is None:
        scripts = glob.glob("src/%s/*.py"%(methods_prefix,))
        scripts.extend(glob.glob("src/%s/*.R"%(methods_prefix,)))
    else:
        scripts = glob.glob(methods)

    for method in scripts:
        __run_method(method, timeseries, '%s/'%(methods_prefix,))

def run_R_method(args):
    """Runs R script with args,

    :args: list of args to run with R script

    """

    with settings(warn_only=True), lcd("src/prediction/"):#, shell_env(R_COMPILE_PKGS='TRUE', R_ENABLE_JIT='3'):
        local("Rscript --vanilla " + " ".join(args))

def run_Python_method(args):
    """Runs Python method with args

    :args: list of args to run with Python script

    """
    with shell_env(PYTHONPATH="$PYTHONPATH:src/"):
        local(' python ' + " ".join(args))

def prediction(timeseries, method = "src/prediction/prediction.R", ):
    # create output directory
    selection_step_directory = __RESULTS_DIRECTORY_PREFIX + 'selection/' + timeseries.split("/")[-1].split(".")[0]
    outdir = __RESULTS_DIRECTORY_PREFIX + 'prediction/' + timeseries.split("/")[-1].split(".")[0] + "/"
    local('mkdir -p ' + outdir)

    method = os.path.abspath(method)
    outdir = os.path.abspath(outdir) + '/'

    files = glob.glob(selection_step_directory + "/*.csv")
    for f in files:
        f_in = os.path.abspath(f)
        run_R_method([method, f_in, outdir])
