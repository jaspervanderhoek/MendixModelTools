# MendixModelTools
Random collection of undocumented modelling resources


## ExecuteMicroflowInNewTransaction_7.14.1.mpk
Use this to execute a microflow in a different context and transaction. It clones the microflow context, which captures the user and session information. This will let the logic run in it’s own short lived transaction. 
The 2 parameters are optional, if you need more parameters you can add them by adding the input parameters to the Java following the pattern ParameterX and ParameterXName. and copy the line 47/48 with the new input parameter names. 

## PrinterService_7.1.0_20170805.mpk
A tested concept module that can print Mendix generated PDF documents to a network printer. The easiest way to use this is to have the printer installed on the machine, but network printers worked too.
The print action can and should be customized with the right margins and page sizes to get the best results.

This module only serves as a starting point to finish and customize the printing process.  (Not Cloud compatible since it requires network access to the printer)
