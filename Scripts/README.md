# MendixModelTools
Random collection of undocumented modelling resources



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