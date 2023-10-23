import os,sys,io,json
import time
from pathlib import Path
import smtplib
import sqlite3

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__),"..\\","")))

from commonlib.ocrm_email_notification import EmailNotification
from commonlib.ocrm_LoggerTool import LoggerTool
from commonlib.ocrm_SqliteTool import CreateSqliteDBConnection
from commonlib.ocrm_time_tool import getesttime

from scripts.TextFile import TextFileProc


dirpath=os.path.dirname(os.path.abspath(__file__))




attachment=["C:\\Users\\nyarkosn\\Documents\\WORK AREA\TO BE DELETED\\FEATURED 2021 PROJECTS.docx"]


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

def main(args):
    try:
        print(args)
        if len(args)!=4:
        #    send email to samuel
           return 1
        jobId=args[1]
        logpath=args[2]
        Environment=args[3]
        
        appConfig=getConfigSettings('app.cfg',Environment)
        dbname=appConfig['databaseName']
        dbFullPath=appConfig['databaseFullPath']
        logger=LoggerTool("C:\OCRMJOBS\Logs","DIGITAL BOUNDARY",appendtolog=logpath)
        logger.printInfoMessage("")
        logger.printInfoMessage("------------Batch Job Processing Started---------------")
        logger.printInfoMessage("")
        
        body=f"Your digital boundary has been received, meets minimum requirements for digitization and has been added to the OCRM GIS.{jobId},{logpath}}}"
        email=EmailNotification(logger)
        
        
        # Get job from database.
        db=CreateSqliteDBConnection().connectdb(logger,dbFullPath)
        Query=f"SELECT id,projectname,tms,action,email,status,message,insertstatusdate,updatestatusdate,attachmentname,originalattachment,filetype FROM {dbname} WHERE id=?"
        response=db.select_one_from_db(Query,jobId,dbFullPath,logger)
        if len(response)!=0:
            job=response[0]
            print("Job Id: " +jobId)
          
            
            if job["filetype"] in ["txt","csv"]:
                print("This is a csv or  txt file")
                processedfile=TextFileProc(appConfig,logger,job)
                response=processedfile.start()
                
                return 0
            
            elif job["filetype"] =="dwg":
                print("This is an autocad file")
            elif job["filetype"] =="zip":
                print("This is a shapefile")           
            else:
                print("Invalid file")       
        
            email.send_mail("DEV","DIGITAL BOUNDARY PROCESSING",body,"nyarkosn@dhec.sc.gov",attachment,"ocrmdigbound@dhec.sc.gov")
            logger.printInfoMessage("Completed successfully")
            logger.printInfoMessage("This is from second log file")     
        
        else:
            body="Provided Id does not exist in database"
            email.send_mail("DEV","DIGITAL BOUNDARY PROCESSING",body,"nyarkosn@dhec.sc.gov",attachment,"ocrmdigbound@dhec.sc.gov")
            logger.printInfoMessage(body)

      
        print("COMPLETED")
        
        return 0
        
    except Exception as e:
        print("Exception occurred")
        raise e
    





if __name__=='__main__':
    intreturncode=main(sys.argv)
    print("Exit code - "+str(intreturncode))
    sys.exit(intreturncode)