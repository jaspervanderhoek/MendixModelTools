# Publishing Rest (or SOAP) Services, what to keep in mind
Microservices and integrations are everywhere, each system needs to be connected to each other. Which means you need to create more and more APIs. But APIs can create dependencies, and when you have a system that is depending on your API you can't just change it anymore. If you've been developing software long enough you have run into the problem that you really should change a service but can't anymore because other systems are using it. Or you have to rebuild most of your logic because you forgot to add a places to put validation rules, or security, or paging through large data sets.  
Most of these problems can be prevented by using the right structure. This best-practice and [template module](https://github.com/jaspervanderhoek/MendixModelTools/raw/master/BP_PublishComplexRestServices/dist/RestWrapperExample_v0.1.0.mpk) are created so that you don't have to reinvent what we've already thought off.  

This page will talk you through the concepts that you need to keep in mind when publishing services. For each topic you'll find that the template module already contains a solution or place to accomodate the challenges.  


## Validation & Consistency  
When exposing services you can have simple services that have no or just primitive parameters, but as soon as you introduce intelligence or complex structures to the input of your service you need to be able to validate and provide a response.  
Yes a 500 server exception will let the caller know he didn't provide the right information, but it's not very helpful. Just like with your application UX you also should focus on creating a good DX (Developer Experience) when working with your service.  

Think about how you can communicate validation messages and make sure you don't need to rewrite your entire mapping and message definition to accomodate this.  

Luckily we're working with the Mendix Platform, which already takes care of a lot of the basic validation. When your service gets called the platform will check that you are receiving JSON. Also if all field and parameters are of the expected types. For example if you publish an integer parameter and you pass a string Mendix will return an error message explaining which value is incorrect.  
![Type Error](https://github.com/jaspervanderhoek/MendixModelTools/raw/master/BP_PublishComplexRestServices/dist/Documentation/SwaggerError_TypeCheck.png)

But we can't only rely on the platform for data validation. If you publish an integer, do you accept negative numbers? What if parameters aren't provided, how do you want to let the caller know about this?  

You can accomodate this through a simple Response & error entity structure. The image below shows the domain model that exactly matches the standard error response from the platform. This is important because we as Mendix developers know about what the platform does and what we built in a microflow, but we don't need the consuming system to know about it.   
So making the exact same Json response will allow the consumer to only expect 1 type of error response:  
![Domain_Model](https://github.com/jaspervanderhoek/MendixModelTools/raw/master/BP_PublishComplexRestServices/dist/Documentation/DomainModel_ResponseValidation.png)

To use this entity structure you only need to create the error and response entity, populate them with the response of your choice, transform to Json and you're done.  
Well even easier, if you use the [template module](https://github.com/jaspervanderhoek/MendixModelTools/raw/master/BP_PublishComplexRestServices/dist/RestWrapperExample_v0.1.0.mpk) you can just call the microflow "CreateSimpleErrorResponse" and it will take care of that for you:  
![Microflow_CreateSimpleErrorResponse](https://github.com/jaspervanderhoek/MendixModelTools/raw/master/BP_PublishComplexRestServices/dist/Documentation/Microflow_CreateSimpleErrorResponse.png)


## Traceability  


## Development Speed & Consistency  



## Security  
TODO  

## Versioning  
TODO  


# The Template  
This best-practices is demonstrated through two modules. The "RestWrapper" and "DataModule" modules are both provided as an mpk file for your use.  
The "RestWrapper" is a starter module to help you quickly setup your published rest service. This module should not be considered an 'Appstore Module' meaning that this is NOT a readonly module and you are encouraged to rename and customize it to integrate with your own functionality.  

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

1. First validate the input parameters (optional). You can add a subflow to do the validation or add all logic at the top level.  
   If validation fails there are two ways to end the flow, the difference between these two is described further down this page:  
     1. the Subflow 'CreateSimpleErrorResponse' and return empty  
     1. the Subflow 'RecordErrorMessage' and return the $Response variable  
     
1. Optional Paging. If your rest service has the option to publish large data sets this can cause issues both in your app and for the consumer. Adding paging (a limit and offset) will make consumption much easier.  
     1. Paging works by leveraging the 'Offset' and 'PageSize' field in the Response object. You can choose to let the user specify the PageSize or you can set yourself in the microflow. The example allows the PageSize as input, but not larger than 200.  
     1. The subflow 'EvaluatePageTokenInformation' checks the 'Token' input parameter and establishes the offset and PageSize in case this is the request for a second page or later.   
        * A String input parameter for the Token is mandatory to use paging.   
        * The PageToken is a 74 character string that the users passes through a parameter, using this string we can do a lookup in the PageToken entity.  
          This entity tracks the limit and offset so that we can reduce the complexity for the enduser.  
        * At the start of the flow variable: 'PageQueryType' was created to hold the enumeration.  
          This enum is to get internal separation of what tokens were requested for. The reason why this is a variable that is passed is to make copy/pasting easier, that way you can copy all logic without making a copy/paste mistake anywhere in the logic.   
          You should customize and extend this enumeration to accomodate all your different page types.  
     1. The subflow returns a boolean, if the value is false the subflow will have created an error response. The end-event should return empty, the HttpResponse has already been built in the subflow.

     1. Note: If you are using paging make sure that your message definition and response mapping publish the 'paging' entity and all fields of 'paging'. Don't publish the 'Offset' and 'PageSize' attribute in 'Response' these two attributes are for internal usage only. 


If you don't need paging you can remove these 2 activities, the 'Create Variable' activity at the start of the microflow, and the 'CreatePagingResponse' subflow at the end.


![Microflow_ExamplePublishedService](https://github.com/jaspervanderhoek/MendixModelTools/raw/master/BP_PublishComplexRestServices/dist/Documentation/Microflow_Example02.png)

![Microflow_ExamplePublishedService](https://github.com/jaspervanderhoek/MendixModelTools/raw/master/BP_PublishComplexRestServices/dist/Documentation/Microflow_Example03.png)
