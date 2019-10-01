Function Get-Branch($headers, $url, $appName, $branchName) {
    irm -Headers $headers ${url}apps/$appName/branches/$branchName
}
 
Function Start-Build($headers, $url, $appName, $branchName, $revision, $version) {
    $buildinput = "{
        'Branch' = '$branchName',
        'Revision' = $revision,
        'Version' = '$version',
        'Description' = 'CI Build $((Get-Date).ToString('s'))'
    }"
 
    Write-Host "Start build with the following input: $buildinput"
    $buildResult = $buildinput | irm -Headers $headers -ContentType "application/json" -Method Post ${url}apps/$appName/packages/
    $buildResult.PackageId
}
 
Function Wait-For-Built($headers, $url, $appName, $packageId, $timeOutSeconds) {
   $date = Get-Date
 
    while($true) {
        $duration = ((Get-Date) - $date).TotalSeconds
 
        if($duration -gt $timeOutSeconds) {
            Write-Host "Build timed out after $duration"
 
            return $false
        }
 
        sleep -s 10
        $package = Get-Package $headers $url $appName $packageId
 
        if($package.Status -eq 'Succeeded') {
            Write-Host "Built package: $package"
 
            return $true
        }
    }
}
 
Function Get-Package($headers, $url, $appName, $packageId) {
    irm -Headers $headers ${url}apps/$appName/packages/$packageId
}
 
Function Transport-Package($headers, $url, $appName, $environment, $packageId) {
    $transportInput = "{ 'PackageId' = '$packageId' }"
    Write-Host "Transport package with the following input: $transportInput"
    $transportInput | irm -Headers $headers -ContentType "application/json" -Method Post ${url}apps/$appName/environments/$environment/transport
}
 
Function Stop-App($headers, $url, $appName, $environment) {
    Write-Host "Stop app $appName ($environment)"
    irm -Headers $headers -Method Post ${url}apps/$appName/environments/$environment/stop
}
 
Function Start-App($headers, $url, $appName, $environment) {
    Write-Host "Start app $appName ($environment)"
    $startJob = "{ 'AutoSyncDb' = true }" | irm -Headers $headers -ContentType "application/json" -Method Post ${url}apps/$appName/environments/$environment/start
    $startJob.JobId
}
 
Function Get-Start-App-Status($headers, $url, $appName, $environment, $jobId) {
    irm -Headers $headers ${url}apps/$appName/environments/$environment/start/$jobId
}
 
Function Wait-For-Start($headers, $url, $appName, $environment, $jobId, $timeOutSeconds) {
   $date = Get-Date
 
    while($true) {
        $duration = ((Get-Date) - $date).TotalSeconds
 
        if($duration -gt $timeOutSeconds) {
            Write-Host "Start app timed out after $duration"
 
            return $false
        }
 
        sleep -s 10
        $startStatus = Get-Start-App-Status $headers $url $appName $environment $jobId
 
        if($startStatus.Status -eq 'Started') {
            return $true
        }
    }
}
 
Function Clean-App($headers, $url, $appName, $environment) {
    Write-Host "Clean app $appName ($environment)"
    irm -Headers $headers -Method Post ${url}apps/$appName/environments/$environment/clean
}
 
$url = 'https://deploy.mendix.com/api/0.1/'
$headers = @{
    'Mendix-Username' = 'richard.ford51@example.com'
    'Mendix-ApiKey' = '26587896-1cef-4483-accf-ad304e2673d6'
}
 
$appName = 'richardford'
$environment = 'Acceptance'
$branchName = 'trunk'
 
$branch = Get-Branch $headers $url $appName $branchName
"Branch to build: $branch"
$latestBuiltRevision = $branch.LatestTaggedVersion.Substring($branch.LatestTaggedVersion.LastIndexOf('.') + 1)
 
if ($latestBuiltRevision -eq $branch.LatestRevisionNumber) {
    "It is not needed to build, as the latest revision is already built."
    exit
}
 
$versionWithoutRevision = $branch.LatestTaggedVersion.Remove($branch.LatestTaggedVersion.LastIndexOf('.'))
$packageId = Start-Build $headers $url $appName $branchName $latestBuiltRevision $versionWithoutRevision
$built = Wait-For-Built $headers $url $appName $packageId 600
 
if($built -eq $false) {
    "No build succeeded within 10 minutes."
    exit
}
 
Stop-App $headers $url $appName $environment
Clean-App $headers $url $appName $environment
Transport-Package $headers $url $appName $environment $packageId
$startJobId = Start-App $headers $url $appName $environment
$started = Wait-For-Start $headers $url $appName $environment $startJobId 600
 
if($started -eq $true) {
    "App successfully started."
}