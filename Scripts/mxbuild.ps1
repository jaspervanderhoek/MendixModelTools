<#
.SYNOPSIS
Create an SVN export from your repository and run mxbuild to create an mda

.DESCRIPTION

.PARAMETER repository
The full url of your project repository, this should include /trunk or /branches/brancheName

.PARAMETER revision 
The specific revision you want to use to build, set to -1 if you want the latest version

.EXAMPLE
mxbuild -repository "https://teamserver.sprintr.com/b76e1c3c-5073-4d1c-b9dd-d8b2608bb305/trunk" -revision -1


#>

param(

[Parameter(Mandatory=$true)][string]$repository,
[Parameter(Mandatory=$true)][string]$revision
)

echo ('Repo: ' . $repository )
echo 'Rev: ' . $revision