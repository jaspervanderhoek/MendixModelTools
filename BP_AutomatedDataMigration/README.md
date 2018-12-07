# Modeling Tips: Automate Data Migration

Often when you have been developing and testing your application for a while you have to start making larger changes in your data structure. All is well until you find that your data on your Test/Accp/Prod server is no longer correct. 
Now you need to build some logic to convert and restore your data hierarchy. 

But don't forget to click that button only once on all your servers.
A few days later you publish your app to the next environment, and since this you skipped several commits you now find that you have to click more and more buttons in production to correct your data.


Why not automate your data migration, this way you can make sure that all migration steps are executed in the right order.

## Why do you have to be conserned about data migration
Imagine the following scenario. 
 * On your local environment you are making 5 changes to your domain model and after each change your start your application.
 * After a few hours you commit all 5 changes through a single commit
 * After a day you've made 10 changes in the domain model, through 3 commits. 
   You push these changes to your Test server.   (The Mendix app now has 10 changes that it needs to correct)
 * After a few more releases to Test, you now promote a version to Acceptance. 
   Acceptance was further behind. e.g. the version now includes 40 domain model changes through 20 commits. 
 * When you finally release to production you are publishing 60+ domain model changes through 30+ commits

It's not uncommon if you've made several larger changes that this can cause issues and you need to fix the data in your database. You can off course make a button somewhere on an admin page, but from experience it's easy enough to forget this or execute the different data conversions in the wrong order. 
Automating these actions in a specific sequence makes these migration steps a lot more reliable. 


## How to automate the migration activities
This folder holds an example on how you can achieve this. (Note: copy this logic into your own admin module and use it as a quick-start)
Download the module mpk here: https://github.com/jaspervanderhoek/MendixModelTools/raw/master/BP_AutomatedDataMigration/dist/DataMigrationTemplate_v1.0.0.mpk

The domain model has 1 entity with 2 attributes. This entity is a Singleton, that means you should only have 1 instance of this in your database. 
  If you have a multi-tenant solution, you can customize this. Setup a 1-* assocation between your tenant and the MigrationTracker and customize the FindAndCreate microflow. Doing this allows you to customize and time the migration separately for each tenant. 

All your migration logic should be placed in the microflow: ASu_EvaluateAndRunDataMigration
This microflow first retrieves the migration tracker and based on the stored DataVersion the microflow can execute specific migration activities. 
With this simple microflow you can execute your migration logic sequentially. 

### Development priniciples
To get the most out of this concept always immediately design the migration logic. That means that as soon as you change your domain model, add logic to convert the data on your local machine. If all developers consistently add their migration steps in the correct sequence in this logic it becomes significantly easier to move the software version to production.
