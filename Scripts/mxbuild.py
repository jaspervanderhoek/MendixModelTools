import subprocess, random, os, shutil, json, urllib.request, os.path, tarfile, argparse, platform, glob, sys

## Setup all input arguments 
parser = argparse.ArgumentParser(description='Automatically export the latest revision and build an .mda  using mxbuild.' ) 
parser.add_argument('-java', action="store", dest="java", help='the Java home directory: \r\n   (Usually \'/usr/lib/jvm/java-8-oracle\' or \'C:\Program Files\Java\jdk1.8.0_144\')')

parser.add_argument('-teamserver', '-t', action="store", dest="svnTeamServer", help='The url of your teamserver repository, including the development line. Generally: \'https://teamserver.sprintr.com/44fc890d-9a19-4afc-8e0a-29768a2b97e1/trunk\' ')
parser.add_argument('-user', '-u', action="store", dest="svnUser", help='Your Username used to sign in on the TeamServer (and modeler) ')
parser.add_argument('-password','-p', action="store", dest="svnPass", help='Your Password used to sign in on the TeamServer (and modeler) ')
parser.add_argument('-revision','-r', action="store", dest="svnRevision", type=int, default=-1, help='The revision you want to build, defaults to the latest revision ')

parser.add_argument('-mprName','-m', action="store", dest="mpr", help='Optionally specify the file name of the mpr file, if you have multiple mpr files this argument is mandarory')
parser.add_argument('-outputFile','-o', action="store", dest="output", help='The path, including the filename where the .mda should be exported')
parser.add_argument('-version','-v', action="store", dest="version", help='Tag the build revision with this specific version number, without only an mda is created. By adding this version a tag will be added too')

parser.add_argument('-debug', '-d', action="store", dest="debug", default=False, help='Enable debug logging')

args = parser.parse_args()

_exportDirectory = os.getcwd() + "/exports/"
_mxLibraryDirectory = os.getcwd() + "/mxLib/"
_buildOutputDirectory =  os.getcwd() + "/builds/"

####
# 		Validate all input arguments, and make sure the user either used an argument or enters it through the CL
####

javaLocation = args.java
#If Java isn't part of the args, ask the user for the Java home directory
while( javaLocation == None or javaLocation.isspace() or not javaLocation.strip()):
	javaLocation = input("Please specify the Java home directory: \r\n   (Usually '/usr/lib/jvm/java-8-oracle' or 'C:\Program Files\Java\jdk1.8.0_144') \n > ")


svnRepo = args.svnTeamServer
# If TeamServer isn't part of the arguments, ask the user to enter a full url
while( svnRepo == None or svnRepo.isspace() or not svnRepo.strip()):
	svnRepo = input("Please specify the TeamServer repository URL: \r\n   (Should be the full url: 'https://teamserver.sprintr.com/[ProjectId]/trunk') \n > ")

svnPass = args.svnPass
# If Password isn't part of the arguments, ask the user to enter a full url
while( svnPass == None or svnPass.isspace() or not svnPass.strip()):
	svnPass = input("Please provide your TeamServer password:\n > ")

svnUser = args.svnUser
# If Username isn't part of the arguments, ask the user to enter a full url
while( svnUser == None or svnUser.isspace() or not svnUser.strip()):
	svnUser = input("Please provide your TeamServer username:\n > ")

# Just copy the svn Revision, it defaults to -1 if nothing was specified
svnRev = args.svnRevision

mprFileName = args.mpr
outputFile = args.output
version = args.version

debugEnabled = args.debug

#######################################
#  Functions 
#######################################

def debug( msg ):
	if debugEnabled:
		print( "  *  " +  msg )

## Create the base SVN command line that includes the expected repo, username and password parameters
def buildSVNclCmd(repo, revision, username, password, targetFolder=None):
	clCmd = ""
	if revision > 1:
		clCmd += " -r {} ".format( revision )
	
	# Add repo url 
	clCmd += " \"{}\"".format( repo )
	# Add destination folder
	if targetFolder is not None:
		clCmd += " \"{}\"".format( targetFolder )
	# Add username and password
	clCmd += " --non-interactive --no-auth-cache --username \"{}\" --password \"{}\"".format( username, password) 
	
	return clCmd
### End buildSVNclCmd


## Run an SVN export, returns the full path of the export location
def exportSVNFolder(repo, revision, username, password):
	targetFolder = "{}{}/".format( _exportDirectory, random.randint(100000000,1000000000) )
	
	clCmd = "svn export {}".format( buildSVNclCmd(repo, revision, username, password, targetFolder) )
	debug( "Running script : " + clCmd )
		
	try:
		p = subprocess.Popen( clCmd, stdout=subprocess.PIPE, shell=True)
		(output, err) = p.communicate()
	except Exception as e:
		print( "Unable to create an SVN export, is this a valid Mendix repository? \r\n")
		sys.exit(-1)
	
	return targetFolder
### End exportSVNFolder()


## Create a SVN tags branch for full release versioning of the project
def tagRevision( repo, revision, username, password, version ):

	if not version is None: 
		debug( "Attempting to tag revision with version number: {}".format(version) )
		clCmd = "svn cp"
		if revision > 1:
			clCmd += " -r {} ".format( revision )
		
		# Add repo url 
		clCmd += " \"{}\"".format( repo )
		# Add repo url 
		firstSlashAfterPrjId = repo.find("/",32)
		clCmd += " \"{}/tags/{}/\"".format( repo[0:firstSlashAfterPrjId], version)
		
		try: 
			debug( "Runnning script: " + clCmd )
			p = subprocess.Popen( clCmd, stdout=subprocess.PIPE, shell=True)
			(output, err) = p.communicate()
		except Exception as e: 
			print( "Unable to create version tag: [{}] because of error: {}".format( " \"{}/tags/{}/\"".format( repo[0:firstSlashAfterPrjId], version), e ) )
			
### End tagRevision()


## Get the Mendix version number from the Revision metadata
def getSVNMetaVersion(repo, revision, username, password):
	clCmd = "svn propget \"mx:metadata\" --revprop {}".format( buildSVNclCmd(repo, revision, username, password) )
	debug( "Running script : " + clCmd  )
		
	p = subprocess.Popen( clCmd, stdout=subprocess.PIPE, shell=True)
	(output, err) = p.communicate()
	
	output = output.decode("utf-8") 
	debug( "Retrieved metadata: " + output)

	try:
		modelVersion = json.loads(output)['ModelerVersion']
	except Exception as e:
		print( "Unable to find Mendix version information, is this a valid Mendix repository? \r\n")
		sys.exit(-1)
	
	return modelVersion
### End getSVNMetaVersion()


## Review te MxVersion number, and  download the MxBuild files if they don't exist yet
def getMxBuildFiles( mxVersion ):
	## Check if we need the tar.gz build package.   
	## If we don't have that on disk yet, download the tar file and extract it
	targetMxBuild = _mxLibraryDirectory + mxVersion
	if not os.path.exists( targetMxBuild ): 
		targetMxBuildZip =  "mxbuild-{}.tar.gz".format(mxVersion)
		
		if not os.path.exists( _mxLibraryDirectory + targetMxBuildZip ): 
			debug("Start downloading: " + targetMxBuildZip)
			urllib.request.urlretrieve("http://cdn.mendix.com/runtime/" + targetMxBuildZip, _mxLibraryDirectory + targetMxBuildZip )

			debug("Download finished, extracting ...")
		else:
			debug("MxBuild .tar.gz file found, extracting ..." + targetMxBuild)
		
		tar = tarfile.open( _mxLibraryDirectory + targetMxBuildZip )
		tar.extractall( targetMxBuild )
		tar.close()
		os.unlink( _mxLibraryDirectory + targetMxBuildZip )
		debug("MxBuild extracted to " + targetMxBuild )
		
	# We already have the MxBuild files, so nothing to do here
	else:
		debug("Mx Build : {} already downloaded".format( targetMxBuild ) )

	return targetMxBuild
### End getMxBuildFiles()


## Build the MxBuild comand line operation and run the build script
def buildMendixDeploymentArchive(  mxBuildFolder, javaLocation, mprFile, outputFile, version ):
	javaExeLocation = javaLocation
	if not javaExeLocation.endswith("\\") and not javaExeLocation.endswith("/") :  	javaLocation += "/"
	
	# Windows and linux require a different Java.exe reference
	if platform.system() == "Windows":		javaExeLocation = javaLocation + "bin/java.exe"
	else : 		javaExeLocation = javaLocation + "bin/java"
	
	# If our java path ends with a \ make sure we escape it
	if javaLocation.endswith("\\") :  	javaLocation += "\\"
	
	## Build the OutputFile location if this wasn't specified through the arguments
	# Default to builds/[mprName][-version].mda
	if outputFile is None: 
		idx = mprFile.rfind("/")
		idx2 = mprFile.rfind("\\")
		idx = max( idx, idx2 )
		
		if( not version is None ):		outputFile = _buildOutputDirectory + "{}-{}.mda".format( mprFile[idx:len(mprFile)-4], version )
		else:										outputFile = _buildOutputDirectory + "{}.mda".format( mprFile[idx:len(mprFile)-4] )
	
	elif ( not "/" in outputFile and not "\\" in outputFile ):
		outputFile = _buildOutputDirectory + outputFile
	
	buildCL = "{}/modeler/mxbuild.exe \"{}\" --java-home=\"{}\" --java-exe-path=\"{}\" --output=\"{}\" ".format( mxBuildFolder, mprFile, javaLocation, javaExeLocation, outputFile )
	debug( "Running script : " + buildCL )
	
	p = subprocess.Popen( buildCL,  shell=True)
	(output, err) = p.communicate()

### End runMxBuild()




##
##	Main execution 
##
print("* Starting svn export of revision: {}".format(svnRev) )
exportFolder = exportSVNFolder( svnRepo, svnRev, svnUser, svnPass )

mxVersion = getSVNMetaVersion( svnRepo, svnRev, svnUser, svnPass )
print( "* Created export of revision, {} using Mx Version ", svnRev, mxVersion )

mxBuildFolder = getMxBuildFiles( mxVersion )
print( "* Located MxBuild files, start building using: {} ", mxBuildFolder)


## Attempt to locate the mpr file
mprFiles = glob.glob(exportFolder + "/*.mpr")
if len(mprFiles) == 1:
	print( "* Starting build process" )
	buildMendixDeploymentArchive( mxBuildFolder, javaLocation, mprFiles[0], outputFile, version )
	tagRevision( svnRepo, svnRev, svnUser, svnPass, version )
	
## If we've found more than 1 mpr file, lookup the target file either in the arguments or ask the user for input
elif len(mprFiles) > 1:
	while( mprFileName is None or mprFileName.isspace() or not mprFileName.strip() or not mprFileName.endswith(".mpr") or ( "/" in mprFileName) or ("\\" in mprFileName) ):
		mprFileName = input("The following .mpr files are found, which one would you like to use in the build?\n" + "\n".join(mprFiles) +"\nOnly enter the mpr name without path\n > " )
	
	print( "* Starting build process" )
	buildMendixDeploymentArchive( mxBuildFolder, javaLocation, exportFolder + "/" + mprFileName, outputFile, version )
	tagRevision( svnRepo, svnRev, svnUser, svnPass, version )
	
elif len(mprFiles) < 1:
	print( "No mpr files were found in the exported svn folder, aborting build. " + exportFolder)
	


try: 
	print( "* Process Completed, start removing svn folder: ", exportFolder)
	shutil.rmtree( exportFolder )
	print( "Process successfully completed ")
	
except e: 
	print( "Unable to remove folder: {} because of error: {}".format( exportFolder, e ) )
	
