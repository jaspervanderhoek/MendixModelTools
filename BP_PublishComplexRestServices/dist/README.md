# Publishing Rest (or SOAP) Services, what to keep in mind  

Microservices and integrations are everywhere, and each system needs to be connected to each other, which means you need to create more and more APIs. But APIs can create dependencies, and when you have a system that is depending on your API any change you make can impact the downstream systems. If you've been developing software long enough you've probably found yourself in the situation that you have to make a change of a service that impacts the depending systems, now you have to make the decision to rebuild most of your logic or coordinate a combined release of the two systems. Both choices are less than ideal, so why not spend a little bit of extra time and make sure your structure is flexible enough to support most changes.  
Most autonomy problems can be prevented by using the right structure. This best-practice and [template module](https://github.com/jaspervanderhoek/MendixModelTools/raw/master/BP_PublishComplexRestServices/dist/RestWrapperExample_v0.1.0.mpk) are created so that you don't have to reinvent what we've already thought of.  

This page will talk you through the concepts that you need to keep in mind when publishing services. For each topic you'll find that the template module already contains a solution or place to accommodate the challenges.  

This page does not talk about optimizing the functionality of your service. For more information about the best and fastest ways to model your service's logic please see the performance guidelines.  


## Validation & Consistency  
When exposing services you can have simple services that have no or just primitive parameters, but as soon as you introduce intelligence or complex structures to the input of your service you need to be able to validate and provide a response.  
When your microflow receives bad data you'd either get an exception and your client gets a 500 server exception, or no data at all. The caller now knows he didn't provide the right information, but it's not very helpful. Just like with your application UX you also should focus on creating a good DX (Developer Experience) when working with your service.  

Think about how you can communicate validation messages and make sure you don't need to rewrite your entire mapping and message definition to accommodate this.  

Luckily we're working with the Mendix Platform, which already takes care of a lot of the basic validation. When your service gets called the platform will check that you are receiving valid JSON and if all fields and parameters are of the expected data types. For example if you publish an integer parameter and you pass a string Mendix will return an error message explaining which value is incorrect.  
![Type Error](https://github.com/jaspervanderhoek/MendixModelTools/raw/master/BP_PublishComplexRestServices/dist/Documentation/SwaggerError_TypeCheck.png)

We can't only rely on the platform for data validation. If you publish an integer, do you accept negative numbers? What if parameters aren't provided, how do you want to let the caller know about this?  

You can accommodate this through a simple Response & error entity structure. The image below shows the domain model that exactly matches the standard error response from the platform. This is important because we as Mendix developers know about what the platform does and what we built in a microflow, but we don't need the consuming system to know about it.   
So making the exact same JSON response will allow the consumer to only expect 1 type of error response:  
![Domain_Model](https://github.com/jaspervanderhoek/MendixModelTools/raw/master/BP_PublishComplexRestServices/dist/Documentation/DomainModel_ResponseValidation.png)

To use this entity structure you need to create an instance of the error and response entity, populate them with the response content of your choice, transform to JSON and you're done.  
To make this even easier, you can use the [template module](https://github.com/jaspervanderhoek/MendixModelTools/raw/master/BP_PublishComplexRestServices/dist/RestWrapperExample_v0.1.0.mpk) and call the microflow "CreateSimpleErrorResponse" which will create the necessary JSON response for you:  
![Microflow_CreateSimpleErrorResponse](https://github.com/jaspervanderhoek/MendixModelTools/raw/master/BP_PublishComplexRestServices/dist/Documentation/Microflow_CreateSimpleErrorResponse.png)  
  
As part of this response we are including an 'ErrorCode' / 'StatusCode' variable. This is an enumeration that you should customize for your needs. Your error codes should return a functional description to the consumer along with a http status code that matches the IETF standard, see the "Error Codes (Types)" section further below on this page. 


## Traceability  
In case your consumers are having issues you want to be able to trace why and where your service was behaving different than expected. This starts by being able to identify unique requests. You can try and do that with timestamps too, but imagine with all the different timezones between systems, and the systems might even be a few minutes apart. All-in-all timestamps are difficult to track across systems.   
This template uses a hash as the ResponseId, these hashes are 36 characters and fairly unique. They could be generated twice, but it's almost impossible that the same hash is generated twice around the same time frame.   
Using these hashes we can trace back the individual response. 

Logging can be enabled too. You'd place the log activity immediately before each end-event the action 'LogResponse' is called. This will asynchronously log the information about this response. For most applications this information will suffice, but if you want to log more you could choose to customize: 'LogResponseFromJava'. Keep in mind that the more you evaluate and log the more capacity it requires of your server.  


## Development Speed & Consistency  
By following the example structure you create a consistent repetitive structure. With the structure from the example microflow you can quickly develop your services with consistent functionality and behavior for both your co-developers and consumers.  
With services looking and working the same way it becomes easier for you and your co-worker to support each others work. By using this module you can create your own template that can be duplicated for each new operation that you want to publish.  

Consistency is important for whomever consumes your services. How often did you complain when calling inconsistent and undocumented APIs? Don't be that person that builds that, even if your documentation is lacking as long as all the Operations have the same structure and response codes implementing your service should be easy.  
  
  
## Security  
Always run your published microflow with entity access enabled, this will make sure you don't accidentally expose unwanted information. This also forces you to setup the right security model and hide any records and fields the user shouldn't be able see. Always setup your security model to allow the least access as possible, even if you might not have pages or APIs published to expose the other entities. Through the standard Mendix client APIs it's possible to retrieve any entity you have access to. Always check and make sure you don't have provide unnecessary read/write/delete access.   
Any Mendix user can login on the Mendix Platform through the web-client API and read or write all data that made accessible through the module roles security, even if there are no pages or custom APIs for those entities.

For system-to-system communication always create a separate service user account. This account should have no UI access and has as little access to entities as is possible to run the service (you can limit this to just the input and output parameters).  

With entity access enabled on your published service, and the bare minimum access exposed to your user you will notice at some point to run your microflow logic your service user needs more access than previously configured. You could change the access rules, but better is to move your logic to a sub flow and run that sub-flow without entity access enabled.  
You can see this in the example microflow. The microflow runs with instance access, the service user does not have read/write access to the paging and token entities. To successfully create those records a sub-flow is called to return the data to the user. 

 * Run all published microflows with entity access enabled
 * Create separate user and module roles for your service account(s)
 * Limit the access of the service accounts to the bare possible minimum  
    The minimum generally is:
    * Read access to the output parameters, try and use non-persistent entities or an instance access xpath rule to limit exposure
    * Always use Non-persistent entities for complex input parameters  
      If for any reason you'd need your real persistent entity as input parameter, then enable the 'System.Owner' property and add an instance access rule that your service account can only read/write entities where "[system.owner='[%CurrentUser%]']"

  
## Versioning  
TODO  
  
  
# The Template  
This best-practices is demonstrated through two modules. The "RestWrapper" and "DataModule" modules are both provided as an mpk file for your use.  
The "RestWrapper" is a starter module to help you quickly setup your published rest service. This module should not be considered an 'Appstore Module' meaning that this is NOT a read-only module and you are encouraged to rename and customize it to integrate with your own functionality.  

The "DataModule" is an example implementation on how to use the RestWrapper functionality. This is a simple working example on how to implement the different concepts. Please note: when you implement your own services you should not follow this example of keeping the modules separate. The integration functionality should all be located in the same project specific module.  

## Template Details:  
Structure:  
 * Folders  
   * _V1.0.0  -      the version number of the module  
   * _UseMe   -    All activities you should implement and/or customize are placed in this folder  
   * Internal  -    Additional documents necessary for the rest services, can be customized but isn't necessary  

The easiest way to explain all the components of the _UseMe folder is to walk through the microflow: _ExamplePublishedService  
![Microflow_ExamplePublishedService](https://github.com/jaspervanderhoek/MendixModelTools/raw/master/BP_PublishComplexRestServices/dist/Documentation/Microflow_Example01.png)

1. Create the response entity, this is used later for all endpoints to build the response  

1. First validate the input parameters (optional). You can add a sub-flow to do the validation or add all logic at the top level.  
   If validation fails there are two ways to end the flow, the difference between these two is described further down this page:  
     1. the Sub-flow 'CreateSimpleErrorResponse' and return empty  
     1. the Sub-flow 'RecordErrorMessage' and return the $Response variable  
     
1. Optional Paging. If your rest service has the option to publish large data sets this can cause issues both in your app and for the consumer. Adding paging (a limit and offset) will make consumption much easier.  
     1. Paging works by leveraging the 'Offset' and 'PageSize' field in the Response object. You can choose to let the user specify the PageSize or you can set yourself in the microflow. The example allows the PageSize as input, but not larger than 200.  
     1. The sub-flow 'EvaluatePageTokenInformation' checks the 'Token' input parameter and establishes the offset and PageSize in case this is the request for a second page or later.   
        * A String input parameter for the Token is mandatory to use paging.   
        * The PageToken is a 74 character string that the users passes through a parameter, using this string we can do a lookup in the PageToken entity.  
          This entity tracks the limit and offset so that we can reduce the complexity for the end user.  
        * At the start of the flow variable: 'PageQueryType' was created to hold the enumeration.  
          This enum is to get internal separation of what tokens were requested for. The reason why this is a variable that is passed is to make copy/pasting easier, that way you can copy all logic without making a copy/paste mistake anywhere in the logic.   
          You should customize and extend this enumeration to accommodate all your different page types.  
     1. The sub-flow returns a boolean, if the value is false the sub-flow will have created an error response. The end-event should return empty, the HttpResponse has already been built in the sub-flow.

     1. Note: If you are using paging make sure that your message definition and response mapping publish the 'paging' entity and all fields of 'paging'. Don't publish the 'Offset' and 'PageSize' attribute in 'Response' these two attributes are for internal usage only. 


If you don't need paging you can remove these 2 activities, the 'Create Variable' activity at the start of the microflow, and the 'CreatePagingResponse' sub-flow at the end.


![Microflow_ExamplePublishedService](https://github.com/jaspervanderhoek/MendixModelTools/raw/master/BP_PublishComplexRestServices/dist/Documentation/Microflow_Example02.png)
This next section is all custom for your application, you can retrieve and validate the data as you see fit. If you use paging, this is where you would pull the offset and PageSize from the response entity. The values will be set correctly at this point. If you want to have validations here you can add them too.


![Microflow_ExamplePublishedService](https://github.com/jaspervanderhoek/MendixModelTools/raw/master/BP_PublishComplexRestServices/dist/Documentation/Microflow_Example03.png)
Close off the microflow by finalizing the paging. Based on the offset, pagesize, and total nr of records that are applicable within the constraints this sub-flow will create the paging entity and populate all the fields correctly. After calling this sub-flow, if you need paging you will have an instance of the 'paging' and 'PageToken' entity. You don't need to do anything with this anymore, besides making sure that your response mapping and message definition allow this data to be returned.

Logging is enabled in this microflow too, immediately before each end-event the action 'LogResponse' is called. This will asynchronously log the information about this response. For most applications this information will suffice, but if you want to log more you could choose to customize: 'LogResponseFromJava'. Keep in mind that the more you evaluate and log the more capacity it requires of your server.


### Error Codes (Types)
To allow the developers to gain better insight in why your service is returning an error, it's often best to be explicit about all functional errors that you are generating.  
The enumeration 'StatusCode' allows you to have flexibility and consistency through all services. There are a few status codes defined as an example. It is recommended to extend this enumeration with all functional errors and codes for your service, an example of this could be: 401 - "Customer’s subscription has expired" or 400 - "Customer doesn't have a configured payment method".  
The enumeration caption will be used in the status response. Additionally this enumeration will also determine the http status code that is returned. When you add or change the enumeration values you'll notice that the microflow: 'GetStatusCode_ByErrorCode' needs to be updated. You can technically choose any status code here, but try to conform with the HTTP Status codes: https://en.wikipedia.org/wiki/List_of_HTTP_status_codes (It's important to not make up your own numbers, pick a status code that matches best with your error)

Add as many enumeration values as you need but try and keep it consistent. 

It's also good to document the different error codes that you have. In the example 'DataModule' the service documentation contains a table with all error codes. It's good practice to disclose this information somewhere in your service too, this can be on the service or for the individual operations.

Below is the example syntax:   

# Error Codes:

Error Description | Status Code | Cause
---------- | :-----------:| --------
Not Found | 200 | Based on the parameters no records could be located
Unauthorized | 401 | Customer’s subscription has expired
Invalid Configuration | 400 | Customer doesn't have a configured payment method
Invalid Authorization | 401 | The credentials that were used don't have access to this operation
Invalid Parameter | 400 | One or more of the required parameters isn't provided or correct
Server Exception | 500 | An unexpected error has occurred, contact the system administrator for more details


