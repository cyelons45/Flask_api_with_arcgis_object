import io
import os
import sys
import  json
import uuid
from datetime import datetime,timedelta
from flask import Flask, request, jsonify
from flask_cors import CORS
from arcgis.gis import GIS
from arcgis.features import FeatureLayer
import json
import os
import bcrypt
import jwt
from commonlib.ocrm_LoggerTool import LoggerTool
from commonlib.ocrm_time_tool import getesttime
from commonlib.ocrm_email_notification import EmailNotification

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__),"..\\","")))
dirpath=os.path.dirname(os.path.abspath(__file__))

app = Flask(__name__)
cors=CORS(app,resources={r"/api/*":{"origins":"*"}})


environment="PROD"

def getConfigSettings(config_path,ENV):
    """
    Description : This function is to load config file to dict
    Args:
        config_path : config file name path
    Returns:
        config dict if succeed otherwise raise exception
    """
    environmentList = ["LOCAL", "DEV", "TST", "PROD"]
    startTime = getesttime()
    try:
        print(ENV)
        if not ENV.upper() in environmentList:
            raise Exception("Failed to set environment variable.")

        with io.open(config_path, encoding="utf-8-sig") as outfile:
            json_object = json.loads(outfile.read())
            if(json_object != None):
                configEnv = json_object["environment"][ENV]
                return configEnv
            else:
                raise Exception(
                    "Deployment environment listed in app.cfg is either not capitalized or is incorrect")
    except Exception as e:
        print("Failed in getConfigSettings function .. " + str(e))
        raise Exception(
            "Failed in getConfigSettings function .. " + str(e))

    
def responsemessage(code,status,message):
    """This function will jsonify the response object and return to caller.

    Args:
        code (string): Error or success code
        status (string): Job status either Failed or success
        message (string): Error or success message

    Raises:
        e: Exception

    Returns:
        object: string object
    """
    try:
        return jsonify({
            "code":code,
            "status":status,
            "message":message
        })
    except Exception as e:
        print(str(e)) 


@app.errorhandler(404)
def page_not_found(e):
    "This is required when a wrong pathe is called to exit"
    print(e)
    return "<h1>404</h1><p>Requested API URL does not exist</p>",404



def get_username(email):
    """Function to extract username from email
    Args:
        email (string): email
    Returns: username
    """
    try:
        username=email.split("@")[0]
        if "." in username:
            username=username.split(".")[0]
        return username
    except Exception as e:
        print("Exception occurred while extracting username from email: "+ str(e)) 
        
        
 
def decode_password(password,password_hash):
    """Function to compare passwords
    Args:
        password (string): password
        password_hash (string): hashed password
    Returns:
        Boolean: True/False
    """
    try:
       encodedpassword=password.encode('utf-8')
       encoded_hash_password=password_hash.encode('utf-8')
       user_status = bcrypt.checkpw(encodedpassword, encoded_hash_password)
       return user_status
    except Exception as e:
        print("Exception occurred while decoding password: "+ str(e)) 
        
def encode_password(password):
    """Function to encode password
    Args:
        password (strin): password string
    returns:
        string: hashed password
    """
    try:
        hashed_input_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
        return hashed_input_password.decode('utf-8')
    except Exception as e:
        print("Exception occurred while encoding password: "+ str(e)) 
 

def compare_datetime(datetime_str1,datetime_str2):
    """Function to find time difference
    Args:
        datetime_str1 (string): datetime string
        datetime_str2 (string): datetime string
    Returns:
        Double: Time difference in minuites
    """
    try:
        datetime_obj1 = datetime.strptime(datetime_str1, '%Y-%m-%d %H:%M:%S')
        datetime_obj2 = datetime.strptime(datetime_str2, '%Y-%m-%d %H:%M:%S')
        time_difference_seconds = (datetime_obj1 - datetime_obj2).total_seconds()
        time_difference_minutes = time_difference_seconds / 60
        return time_difference_minutes
    except Exception as e:
        print("Exception occurred while getting time difference: "+ str(e)) 
 
 
@app.route("/api/ocrm/forgot_password",methods=['POST'])
def forgot_password():
    try:
        startTime = getesttime()
        if request.method == 'POST':
            email=request.form.get("email",None)
            if len(email)<3 or '@' not in email:
                return responsemessage('e001',"Failed","Invalid input"),401            
            if email:         
                appConfig=getConfigSettings('app.cfg',environment)
                username=appConfig['username']
                password=appConfig['password']
                table=appConfig['table']
                logPath=appConfig['logFilePath']
                arcgisOnline=appConfig['arcgisOnline'] 
                sender_email=appConfig['senderEmail'] 
                if not os.path.exists(logPath):
                    os.makedirs(logPath)
                logger=LoggerTool(logPath,"DASHBOARD API")
                gis= GIS(arcgisOnline, username, password)
                query = f"email = '{email}'"
                layer=FeatureLayer(table, gis)
                result = layer.query(where=query)
                if len(result.features)==0:
                    return responsemessage('e001',"Failed","User Not Found"),403
                faeture=result.features[0]
                action_type=result.features[0].get_value("actiontype")
                if action_type =="inactive":
                    return responsemessage('e001',"Failed","User Not Authorized by DHEC"),403
                if action_type =="active":
                    validation_code=str(abs(uuid.uuid4().int) % 100000).zfill(5)
                    isotime=(str(startTime))[:19]
                    faeture.set_value(field_name = "est_time", value =isotime)
                    faeture.set_value(field_name = "code", value =validation_code)
                    layer.edit_features(updates=[faeture])
                    email_notif=EmailNotification(logger)
                    request_username=get_username(email)
                    email_notif.send_mail(email, sender_email,validation_code,request_username)         
                    return responsemessage('s001',"completed","Password Reset code sent to user email"),200
    except Exception as e:
        return responsemessage('e001',"Failed","Exception occcurred :"+str(e)),400       
    
     
@app.route("/api/ocrm/resetpassword",methods=['POST'])
def reset():
    try:
        startTime = getesttime()
        if request.method == 'POST':
            email=request.form.get("email",None)
            userpassword=request.form.get("newpassword",None)
            password_confirm=request.form.get("passwordconfirm",None)
            activation_code=request.form.get("resetcode",None)
            if userpassword!=password_confirm:
                return responsemessage('e001',"Failed","Unmatched password and password confirm"),401 
            if len(email)<3 or '@' not in email or len(userpassword)<3 or len(activation_code)<5:
                return responsemessage('e001',"Failed","Invalid input"),401            
            if email and userpassword:
                appConfig=getConfigSettings('app.cfg',environment)
                username=appConfig['username']
                password=appConfig['password']
                table=appConfig['table']
                arcgisOnline=appConfig['arcgisOnline'] 
                resetcode_life=appConfig['resetcodeLife'] 
                
                gis= GIS(arcgisOnline, username, password)
                query = f"email = '{email}'"
                layer=FeatureLayer(table, gis)
                result = layer.query(where=query)
                if len(result.features)==0:
                    return responsemessage('e001',"Failed","User Not Found"),403
                faeture=result.features[0]
                code=result.features[0].get_value("code")
                reset_time=result.features[0].get_value("est_time")
                if code!=activation_code:
                    return responsemessage('e001',"Failed","Invalid Reset Code"),403
                
                isotime=(str(startTime))[:19]
                time_difference=compare_datetime(isotime,reset_time)               
                
                if code!=activation_code:
                    return responsemessage('e001',"Failed","Invalid Reset Code"),403
 
                if time_difference > resetcode_life:
                    return responsemessage('e001',"Failed","Expired Reset Code"),403
                
                passwrd=encode_password(userpassword)
                                                                              
                faeture.set_value(field_name = "password", value =passwrd)
                layer.edit_features(updates=[faeture])

                return jsonify({"code":"s000","message":"completed","status":"success"}),200  

            else:
                return responsemessage('e001',"Failed","Invalid email, password or resetcode"),400       
    except Exception as e:
        return responsemessage('e001',"Failed","Exception occcurred :"+str(e)),400       
        

@app.route("/api/ocrm/delete/<id>",methods=['DELETE'])
def delete(id):
    try:
        if request.method == 'DELETE':
            appConfig=getConfigSettings('app.cfg',environment)
            username=appConfig['username']
            password=appConfig['password']
            table=appConfig['table']
            secret_key=appConfig['secret_key']
            auth=request.headers.get("Authorization")
            arcgisOnline=appConfig['arcgisOnline'] 
            if auth=='' or len(auth)<12:
                return responsemessage('e001',"Failed","Missing Authorization Token"),400    
            token=request.headers.get("Authorization").split("Bearer ")[1]
            decoded_token=jwt.decode(token,secret_key,algorithms="HS256")
            email=decoded_token["email"]
            exp=decoded_token["exp"]
            expiration_datetime=datetime.utcfromtimestamp(exp)
            if expiration_datetime < datetime.utcnow():
                return responsemessage('e001',"Failed","User Not Logged In"),400    
            
            gis= GIS(arcgisOnline, username, password)
            query = f"email = '{email}'"
            layer=FeatureLayer(table, gis)
            result = layer.query(where=query)
            if len(result.features)==0:
                    return responsemessage('e001',"Failed","You are not authorized to perform this operation."),403
            role=result.features[0].get_value("role")
            if role!="admin":
                return responsemessage('e001',"Failed","You are not authorized to perform this operation."),403   
                    
            delete_result = layer.edit_features(deletes=str(id))
            print(delete_result)
            return jsonify({"code":"s000","message":"completed","status":"success"}),204      
    except Exception as e:
        return responsemessage('e001',"Failed","Exception occcurred :"+str(e)),400
    
    
@app.route("/api/ocrm/login",methods=['POST'])
def login():
    try:
        if request.method == 'POST':
            email=request.form.get("email",None)
            userpassword=request.form.get("password",None)
            if len(email)<3 or '@' not in email or len(userpassword)<3:
                return responsemessage('e001',"Failed","Invalid input"),401
            if email and userpassword:
                appConfig=getConfigSettings('app.cfg',environment)
                username=appConfig['username']
                password=appConfig['password']
                table=appConfig['table']
                secret_key=appConfig['secret_key']
                arcgisOnline=appConfig['arcgisOnline'] 
                gis= GIS(arcgisOnline, username, password)
                query = f"email = '{email}'"
                layer=FeatureLayer(table, gis)
                result = layer.query(where=query)
                if len(result.features)==0:
                    return responsemessage('e001',"Failed","User Not Found"),403
                hashed_password=result.features[0].get_value("password")
                phone=result.features[0].get_value("phone")
                action_type=result.features[0].get_value("actiontype")
                if action_type.lower()=="active":
                    status=decode_password(userpassword,hashed_password)
                    if not status:
                        return responsemessage('e001',"Failed","Invalid Username or Password"),403
                    payload = {
                        "email": email,
                        "phone": phone,
                        "exp": datetime.utcnow() + timedelta(hours=1)  
                    }
                    token = jwt.encode(payload, secret_key, algorithm="HS256")
                    return jsonify({"code":"s000","message":"completed","status":"success","token":token}),200  
                else:
                    return responsemessage('e001',"Failed","Contact DHEC OCRM staff to get authorized."),400    
            else:
                return responsemessage('e001',"Failed","Invalid email,phone or password"),400           
    except Exception as e:
        return responsemessage('e001',"Failed","Exception occcurred :"+str(e)),400



@app.route("/api/ocrm/register",methods=['POST'])
def register():
    try:
        if request.method == 'POST':
            email=request.form.get("email",None)
            userpassword=request.form.get("password",None)
            password_confirm=request.form.get("passwordconfirm",None)
            phone=request.form.get("phone",None)
            if userpassword!=password_confirm:
                return responsemessage('e001',"Failed","Unmatched password and password confirm"),401 
            if len(email)<3 or '@' not in email or len(userpassword)<3 or len(phone)<3:
                return responsemessage('e001',"Failed","Invalid input"),401
            if email and userpassword and phone:
                appConfig=getConfigSettings('app.cfg',environment)
                username=appConfig['username']
                password=appConfig['password']
                table=appConfig['table'] 
                arcgisOnline=appConfig['arcgisOnline'] 
                gis= GIS(arcgisOnline, username, password)
                layer=FeatureLayer(table, gis)
                query = f"email = '{email}'"
                result = layer.query(where=query)
                if len(result.features)>0:
                    return responsemessage('e001',"Failed","User already exist"),403
                passwrd=encode_password(userpassword)
                new_feature_attributes = {
                    "attributes":{
                    "email": email,
                    "password": passwrd,
                    "phone": phone 
                    }               
                }
                new_feature = layer.edit_features(adds=[new_feature_attributes])
                if new_feature["addResults"][0]["success"]:
                    return jsonify({"code":"s000","message":"completed","status":"success"}),201 
            else:
                return responsemessage('e001',"Failed","Invalid email,phone or password"),400           
    except Exception as e:
        return responsemessage('e001',"Failed","Exception occcurred :"+str(e)),400



if __name__=="__main__":
    app.run(debug=True)