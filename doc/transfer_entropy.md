# Transfer entropy

**Problems**

  * libtransferentropy:
    * problems compiling on MAC OS X
    * works on single core
    * Lag parameter set to 1 (TODO: see if this could be changed in the pairwise entropy code)

## Ideas:

  * Build own transferentropy using conditional mutual information (several existing packages python and C)
  * https://github.com/trentool/TRENTOOL3
     * Popular matlab library writen in c++ and cuda
     * problems using outside of matlab
  * https://github.com/olavolav/te-causality
    * Looks resonable
    * problems with compiling dependencies (https://github.com/ChristophKirst/SimKernel)
    * seems abandoned (last commits form April 2015)
  * MUTE http://mutetoolbox.guru/downloads/#
    * another popular matlab transfer entropy toolbox
  * TIM http://www.cs.tut.fi/%7Etimhome/tim/tim.htm
    * matlab and standalone toolbox
    * Looks resonable, uses some strange console parser, but maybe could be used
  * JIDT https://github.com/jlizier/jidt
    * Writen in Java, active development
    * Has some bindings to Python and R

## JIDT:

```bash
cd demos/AutoAnalyser
java -classpath "../java:../../infodynamics.jar" infodynamics.demos.autoanalysis.AutoAnalyserTE
# Set data and params and generate python code
```

Sample python code
```python
from jpype import *
import numpy
# I think this is a bit of a hack, python users will do better on this:
sys.path.append("../python")
import readFloatsFile

# Add JIDT jar library to the path

jarLocation = "../../infodynamics.jar"
# Start the JVM (add the "-Xmx" option with say 1024M if you get crashes due to not enough memory space)
startJVM(getDefaultJVMPath(), "-ea", "-Djava.class.path=" + jarLocation)

# 0. Load/prepare the data:
dataRaw = readFloatsFile.readFloatsFile("/home/eror/src/jidt/demos/data/SFI-heartRate_breathVol_bloodOx.txt")
# As numpy array:
data = numpy.array(dataRaw)
source = data[:,0]
dest = data[:,1]

# 1. Construct the calculator:
calcClass = JPackage("infodynamics.measures.continuous.kraskov").TransferEntropyCalculatorKraskov
calc = calcClass()
# 2. Set any properties to non-default values:
calc.setProperty("DELAY", "122")
# 3. Initialise the calculator for (re-)use:
calc.initialise()
# 4. Supply the sample data:
calc.setObservations(source, dest)
# 5. Compute the estimate:
result = calc.computeAverageLocalOfObservations()
print("TE_Kraskov (KSG)(col_0 -> col_1) = %.4f nats\n" % result)
```
