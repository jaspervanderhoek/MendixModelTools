# Mendix Python Build Script
This script is capable of creating an svn export of your teamserver repository and then create an mda file based on this export. 
The script will automatically attempt to download the required mxbuild file

This script is built on python and has the following prerequisites:
-	Python 3.x installed
-	Svn command line tools installed
-	Script is run from a folder that contains 3 additional folders: builds, exports, mxLib   (same as github repo)


Example 1, export Revision 100 and tag as version 1.0.0

 > python .\mxbuild.py -t "https://teamserver.sprintr.com/[ProjectId]/trunk" -u "email@mendix.com" -p "[Password]" -java "C:/Program Files/Java/jdk1.8.0_144/" -v "1.0.0" -r100


Example 1, export the latest Revision, untagged

 > python .\mxbuild.py -t "https://teamserver.sprintr.com/[ProjectId]/trunk" -u "email@mendix.com" -p "[Password]" -java "C:/Program Files/Java/jdk1.8.0_144/"


It is also possible to start the script without any parameters, the script will then prompt you for all mandatory values. For running this as part of the CICD pipeline you should run the script with the arguments as per the example. In the CICD pipeline it's not recommended to use debugging, but this can be enabled by adding the argument "-debug=True"



This script follows the following steps:
1.	SVN export into a temporary folder in ./exports/
2.	SVN lookup for the modeler version nr
3.	Lookup of the mxbuild package
a.	If the right mxbuild version isn’t present in the mxLib folder download and extract the right version  (this takes a few minutes since it downloads and extracts 400Mb)
4.	Start the mxbuild script 
5.	Output an .mda file in the builds folder
6.  Optionally create an svn version tag
7.	Remove the temporary svn export folder



The file arguments are documented in the script.

```
> python .\mxbuild.py - h

usage: mxbuild.py [-h] [-java JAVA] [-teamserver SVNTEAMSERVER]
                  [-user SVNUSER] [-password SVNPASS] [-revision SVNREVISION]
                  [-mprName MPR] [-outputFile OUTPUT] [-version VERSION]
                  [-debug DEBUG]

Automatically export the latest revision and build an .mda using mxbuild.

optional arguments:  
  -h, --help            show this help message and exit 
  -java JAVA            the Java home directory: (Usually 
                        '/usr/lib/jvm/java-8-oracle' or 'C:\Program 
                        Files\Java\jdk1.8.0_144') 
  -teamserver SVNTEAMSERVER, -t SVNTEAMSERVER 
                        The url of your teamserver repository, including the 
                        development line. Generally: 'https://teamserver.sprin 
                        tr.com/44fc890d-9a19-4afc-8e0a-29768a2b97e1/trunk' 
  -user SVNUSER, -u SVNUSER 
                        Your Username used to sign in on the TeamServer (and
                        modeler)
  -password SVNPASS, -p SVNPASS
                        Your Password used to sign in on the TeamServer (and
                        modeler)
  -revision SVNREVISION, -r SVNREVISION
                        The revision you want to build, defaults to the latest
                        revision
  -mprName MPR, -m MPR  Optionally specify the file name of the mpr file, if
                        you have multiple mpr files this argument is mandarory
  -outputFile OUTPUT, -o OUTPUT
                        The path, including the filename where the .mda should
                        be exported
  -version VERSION, -v VERSION
                        Tag the build revision with this specific version
                        number, without only an mda is created. By adding this
                        version a tag will be added too
  -debug DEBUG, -d DEBUG
                        Enable debug logging
>
>
```
