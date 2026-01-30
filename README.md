An example of Oracle OCI functions usage.

This function calls out to a website, scrap some data out of a webpage, and send it to OCI Hub Connector which in turns sends it to OCI Nofication for delivery via SMS.
You may send direct to OCI Notifications but in this can only email as a channel works, not SMS, hence the usage of OCI Hub Connector.

Couple of tips:
* There is a pip command to extract the requirements.txt from your python code.
* The OCI Function (Fn project based) needs a handler(ctx, data: io.BytesIO = None) as header 
* The OCI Function (Fn project based) needs a return response.Response(ctx,...)
* You use the instance principal logging method for your function to obtain its "signer" value (make sure your function falls into a dyn group and has correct policies)
* return response.Response(ctx, response_data=..., headers={"Content-Type": "application/json"})
* Activate Monitoring from the OCI Application to get the logs (function invocation logs) out of the function execution
* Policies can be challenging to figure out, give broad permissions to your policy statements e.g. to manage all-resources in tenancy and work your way up towards least privilege
* Just read the OCI SDK Python documentation on the classes, methods you are going to use, it will save you time :>
* There is a need to execute fn invoke to build your application, it is not ideal and it takes time to go through the process everytime. I am pretty sure there is a way to speed up the process, if you know let me know.
