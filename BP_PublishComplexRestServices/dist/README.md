# Publishing Rest (or SOAP) Services, what to keep in mind
Microservices and integrations are everywhere, each system needs to be connected to each other. Which means you need to create more and more APIs. But APIs can create dependencies, and when you have a system that is depending on your API you can't just change it anymore. If you've been developing software long enough you have run into the problem that you really should change a service but can't anymore because other systems are using it. Or you have to rebuild most of your logic because you forgot to add a places to put validation rules, or security, or paging through large data sets. 
Most of these problems can be prevented by using the right structure. This best-practice and [template module](https://github.com/jaspervanderhoek/MendixModelTools/raw/master/BP_PublishComplexRestServices/dist/RestWrapperExample_v0.1.0.mpk) are created so that you don't have to reinvent what we've already thought off.

This page will talk you through the concepts that you need to keep in mind when publishing services. For each topic you'll find that the template module already contains a solution or place to accomodate the challenges. 


# Validation & Consistency
When exposing services you can have simple services that have no or just primitive parameters, but as soon as you introduce intelligence or complex structures to the input of your service you need to be able to validate and provide a response. 
Yes a 500 server exception will let the caller know he didn't provide the right information, but it's not very helpful. Just like with your application UX you also should focus on creating a good DX (Developer Experience) when working with your service.

Think about how you can communicate validation messages and make sure you don't need to rewrite your entire mapping and message definition to accomodate this. 

Luckily we're working with the Mendix Platform, which already takes care of a lot of the basic validation. When your service gets called the platform will check that you are receiving JSON. Also if all field and parameters are of the expected types. For example if you publish an integer parameter and you pass a string Mendix will return an error message explaining which value is incorrect. 
![Type Error](https://github.com/jaspervanderhoek/MendixModelTools/tree/master/BP_PublishComplexRestServices/dist/Documentation/SwaggerError_TypeCheck.png)

But we can't only rely on the platform for data validation. If you publish an integer, do you accept negative numbers? What if parameters aren't provided, how do you want to let the caller know about this?

You can accomodate this through a simple Response & error entity structure. The image below shows the domain model that exactly matches the standard error response from the platform. This is important because we as Mendix developers know about what the platform does and what we built in a microflow, but we don't need the consuming system to know about it. 
So making the exact same Json response will allow the consumer to only expect 1 type of error response:
![Domain with error message](https://github.com/jaspervanderhoek/MendixModelTools/tree/master/BP_PublishComplexRestServices/dist/Documentation/DomainModel_ResponseValidation.png)

To use this entity structure you only need to create the error and response entity, populate them with the response of your choice, transform to Json and you're done. 
Well even easier, if you use the template module you can just call the microflow "CreateSimpleErrorResponse" and it will take care of that for you:
![Microflow_CreateSimpleErrorResponse](https://github.com/jaspervanderhoek/MendixModelTools/tree/master/BP_PublishComplexRestServices/dist/Documentation/Microflow_CreateSimpleErrorResponse.png)


* Security
* Validation
* Consistent response
* Versioning
* Development speed
* Traceability 
