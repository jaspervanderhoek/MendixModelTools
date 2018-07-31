# MendixModelTools
Random collection of undocumented modelling resources


## ExecuteMicroflowInNewTransaction_7.14.1.mpk
Use this to execute a microflow in a different context and transaction. It clones the microflow context, which captures the user and session information. This will let the logic run in it’s own short lived transaction. 
The 2 parameters are optional, if you need more parameters you can add them by adding the input parameters to the Java following the pattern ParameterX and ParameterXName. and copy the line 47/48 with the new input parameter names. 
