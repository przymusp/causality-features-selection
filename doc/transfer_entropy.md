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
