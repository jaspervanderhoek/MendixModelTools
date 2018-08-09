import subprocess, random, os, shutil, json, urllib.request, os.path, tarfile

svnRepo = "https://teamserver.sprintr.com/44fc890d-9a19-4afc-8e0a-29768a2b97e1/trunk"
svnRev = 100
svnUser = "jasper.van.der.hoek@mendix.com"
svnPass = "@3Wesdxc"







def generateFolderName(): 
		return "/{}/".format( random.randint(100000000,1000000000) )

def debug( msg ):
	print( msg )


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
	clCmd += " --username \"{}\" --password \"{}\"".format( username, password) 
	
	return clCmd

## Run an SVN export, returns the full path of the export location
def exportSVNFolder(repo, revision, username, password):
	targetFolder = os.getcwd() + generateFolderName()
	
	clCmd = "svn export {}".format( buildSVNclCmd(repo, revision, username, password, targetFolder) )
	debug( "Running script : " + clCmd )
		
	p = subprocess.Popen( clCmd, stdout=subprocess.PIPE, shell=True)
	(output, err) = p.communicate()
	
	#debug("Revision is", output)

	return targetFolder

## Get the Mendix version number from the Revision metadata
def getSVNMetaVersion(repo, revision, username, password, targetFolder):
	clCmd = "svn propget \"mx:metadata\" --revprop {}".format( buildSVNclCmd(repo, revision, username, password) )
	debug( "Running script : " + clCmd  )
		
	p = subprocess.Popen( clCmd, stdout=subprocess.PIPE, shell=True)
	(output, err) = p.communicate()
	
	output = output.decode("utf-8") 

	return json.loads(output)['ModelerVersion']
	


exportFolder = exportSVNFolder( svnRepo, svnRev, svnUser, svnPass )
print( "svn export completed into folder ", exportFolder )


mxVersion = getSVNMetaVersion( svnRepo, svnRev, svnUser, svnPass, exportFolder )
print( "The repository is in Mx Version ", mxVersion )


## Check if we need the tar.gz build package.   
## If we don't have that on disk yet, download the tar file and extract it
targetMxBuild = "{}/mxLib/{}".format(os.getcwd()mxVersion)
if not os.path.exists( targetMxBuild ): 
	targetMxBuildZip =  "mxbuild-{}.tar.gz".format(mxVersion)
	print("start downloading: " + targetMxBuildZip)
	urllib.request.urlretrieve("http://cdn.mendix.com/runtime/" + targetMxBuildZip, "./mxLib/" + targetMxBuildZip )

	print("Download finished, extracting ...")
	tar = tarfile.open( "./mxLib/" + targetMxBuildZip )
	tar.extractall( targetMxBuild )
	tar.close()
	shutil.remove( targetMxBuildZip )
	print("MxBuild extracted to " + targetMxBuild )
	
# We already have the MxBuild files, so nothing to do here
else:
	print("Mx Build : {} already downloaded".format( targetMxBuild ) )


## TODO finish this script
buildCL = targetMxBuild + "/modeler/mxbuild.exe -o=package.mda " + exportFolder + " --java-home=bla-bla-bla"
print( buildCL )
p = subprocess.Popen( buildCL,  shell=True)
(output, err) = p.communicate()



try: 
	print( "Start removing ", exportFolder)
	shutil.rmtree( exportFolder )
	print( "Finshed removing ", exportFolder)
	
except e: 
	print( "Unable to remove folder: {} because of error: {}".format( exportFolder, e ) )
	

