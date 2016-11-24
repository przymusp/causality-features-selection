from fabric.api import *
import glob
import os

__RESULTS_DIRECTORY_PREFIX='results/'

def update_requirements():
    local('gawk \'/^library/{test = gensub(/library\((.*)\).*/,"\\\\1","g"); A[test]=0}; BEGIN{printf("chooseCRANmirror()\\n");}END{for (k in A) printf("install.packages(\\\"%s\\\")\\n",k);}\' `find . -name "*.R"` > requirements.R')
    local('pipreqs --force .')

def get_uci_dataset():
    with lcd("src/tools/download_uci_ml/"):
        local("scrapy crawl uci")

def __run_method(method, timeseries, method_prefix, timeseries_prefix=None):
    """Runs any method on a timeseries file

    :method: path to the method
    :timeseries: path to timeseries file
    :returns: None

    """

    # create output directory
    outdir = __RESULTS_DIRECTORY_PREFIX + method_prefix + timeseries.split("/")[-1].split(".")[0]
    if timeseries_prefix is not None:
        outdir = __RESULTS_DIRECTORY_PREFIX + method_prefix + timeseries_prefix
    local('mkdir -p ' + outdir)

    # guess interpreter type
    methodtype = method.split("/")[-1].split(".")[1]

    # Select runner to run script (R or Python)
    _run = run_Python_method
    if methodtype == "R": _run = run_R_method

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

def __run_methods(methods, timeseries, methods_prefix, timeseries_prefix=None):

    if methods is None:
        scripts = glob.glob("src/%s/*.py"%(methods_prefix,))
        scripts.extend(glob.glob("src/%s/*.R"%(methods_prefix,)))
    else:
        scripts = glob.glob(methods)

    for method in scripts:
        __run_method(method, timeseries, '%s/'%(methods_prefix,), timeseries_prefix)

def run_R_method(args):
    """Runs R script with args,

    :args: list of args to run with R script

    """
    method = os.path.abspath(args[0])
    ts = os.path.abspath(args[1])
    outdir = os.path.abspath(args[2]) + '/'

    with settings(warn_only=True), lcd(os.path.dirname(method)):#, shell_env(R_COMPILE_PKGS='TRUE', R_ENABLE_JIT='3'):
        local("Rscript --vanilla " + " ".join([method, ts, outdir]))

def run_Python_method(args):
    """Runs Python method with args

    :args: list of args to run with Python script

    """
    with shell_env(PYTHONPATH="$PYTHONPATH:src/"):
        local(' python ' + " ".join(args))

def prediction(timeseries, methods = None):
    timeseries_prefix = timeseries.split("/")[-1].split(".")[0]
    selection_step_directory = __RESULTS_DIRECTORY_PREFIX + 'selection/' + timeseries_prefix

    files = glob.glob(selection_step_directory + "/*.csv")
    for f in files:
        __run_methods(methods, f, 'prediction', timeseries_prefix)
