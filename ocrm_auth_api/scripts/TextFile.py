# python3
try:
    import os,io
    import datetime
    import csv
    import shutil
    import sys
    import array as arr
    import codecs
    import datetime
    import arcpy
    
    from commonlib.ocrm_LoggerTool import LoggerTool

except Exception as e:
    print("Exception occurred while importing module: "+str(e))


dirpath=os.path.dirname(os.path.abspath(__file__))

workspace =os.getcwd()
workSp=arcpy.env.workspace
arcpy.env.overwriteOutput = True
##
TodaysDate=datetime.datetime.strftime(datetime.date.today(), '%m/%d/%y')

samplejob={'id': 'd6aabeb5178d4d4d975232aeccd29be9', 'projectname': 'New project2', 'tms': 'R0001J3456TTD', 'action': 'new_project', 'email': 'nyarkosn@dhec.sc.com', 'status': 'Pending', 'message': 'Pending', 'insertstatusdate': '2022-09-11 17:08:13', 'updatestatusdate': None, 'attachmentname': 'Queens_Way_Sidewalk_1_274034.txt', 'originalattachment': 'Queens Way Sidewalk (1).txt', 'filetype': 'txt'}

class TextFileProc:
    
    # ***This class is responsible for downloading email attachments and updating the 
    # geodatabase. It will send a response email to sender letting sender know if 
    # the boundary is accepted or rejected*** 
    def __init__(self,appConfig,logger,job):
        try:
            self.config=appConfig
            self.logger=logger
            self.job=job
        except Exception as e:
            print(str(e))



    def start(self):
        try:
            response=self.checkLength()
            
        except Exception as e:
            raise e
  



    def initFile(self, txtcontent):
        ##        ***This method picks and open the file ***
        newLists=[]
        try:
            for point in txtcontent:
                newLists.append(len(point))
            return set(newLists)
        except Exception as e:
            print(str(e))
            raise Exception("Error occurred while checking length of each line in file:"+str(e))
            
            
    def trueValue(self,SET):
    ##        ***This code checks if the file is multipart or singlepart ***
        try:
            for value in SET:
                if(len(SET))==1:
                    return value
                else:
                    return
        except Exception as e:
            print(str(e))
            raise Exception("Error occurred while checking if project is multipart or singlepart:"+str(e))
    
               
    def transformCoord(self,values):
        try:
            newList =[]
            for point in values:
                if len(point)==2:      
                    if (point[0]>point[1]):
                        x=point[0]
                        y=point[1] 
                        newList.append([x,y])
                    elif (point[0]<point[1]):
                        y=point[0]
                        x=point[1] 
                        newList.append([x,y])
                elif len(point)==3:        
                    if (point[1]>point[2]):
                        i=point[0]
                        x=point[1]
                        y=point[2]  
                        newList.append([int(i),x,y])
                    elif (point[1]<point[2]): 
                        i=point[0]
                        y=point[1]
                        x=point[2]
                        newList.append([int(i),x,y])
            return newList    
        except Exception as e:
            print(str(e))
            raise Exception("Error occurred while striping coordinates :"+str(e))
        finally:
            self.logger.printInfoMessage("Function name: transformCoord--Convert Coordinate to Integer Values")
      
            
    def filter_values_csv(self,downloadedFilePath):
        try:
            filtered=[]
            with open(downloadedFilePath, "r") as csvfile:
                spamreader = csv.reader(csvfile)
                rows=[]
                for eachline in spamreader:  
                    for col in eachline:
                        rows.append(col.split(","))

                for line in rows:
                    if len(line)>1:
                        if int(len(line))==2:
                            filtered.append([self.checkfloat(line[0]),self.checkfloat(line[1])])
                        elif int(len(line))==3:
                            if len(line[0])>3:
                                break
                            filtered.append([int(line[0]),self.checkfloat(line[1]),self.checkfloat(line[2])])
                
                return  filtered    
        except Exception as e:
            print(str(e))
            raise Exception("Error occurred while reading csv file :"+str(e))
        finally:
            self.logger.printInfoMessage("Function name: transformCoord--CSV file read successfully")

 
    
    
    def filterTextValues(self,downloadedFilePath):
        try:
            values=[]
            txtF= codecs.open(downloadedFilePath,mode='rb',encoding='utf-8-sig').read().split('\r\n')
            for line in txtF:
                point=line.split(',')
                values.append(point)

            filtered=[]
            for line in values:
                if int(len(line))!=0 and int(len(line))!=1:
                    if int(len(line))==2:
                        filtered.append([self.checkfloat(line[0]),self.checkfloat(line[1])])
                    elif int(len(line))==3:
                        if len(line[0])>3:
                            break
                        filtered.append([int(line[0]),self.checkfloat(line[1]),self.checkfloat(line[2])])
            return filtered
        except Exception as e:
            print(str(e))
            raise Exception("File could not be read :"+str(e))
        finally:
            self.logger.printInfoMessage("Function name:filterTextValues --TXT file read successfully")   
            
      
 
    def CreateSDEConnection(self,sdeConnPath):
        try:
            Instance=self.config["Instance"]
            SDEDatabase=self.config["SDEDatabase"]
            username=self.config["username"]
            password=self.config["password"] 
            SDEConnPath=os.path.join(sdeConnPath,'ocrm.sde')
            if not os.path.exists(SDEConnPath):
                arcpy.CreateDatabaseConnection_management(sdeConnPath,
                                                        "ocrm.sde",
                                                        "SQL_SERVER",
                                                        Instance,
                                                        "DATABASE_AUTH",
                                                        username,
                                                        password,
                                                        "SAVE_USERNAME",
                                                        SDEDatabase,
                                                        "#",
                                                        "TRANSACTIONAL",
                                                        "sde.DEFAULT")
            return True
        except Exception as e:
            print(str(e))
            raise Exception("Error creating sde connection :"+str(e))
        finally:
            self.logger.printInfoMessage("Function name:CreateSDEConnection --SDE connection verified successfully")   


    def FindNumberOfParts(self,constent):
        ##        ***If the file is multipart, this code will check how many polygons exist in file***
        numOfParts=[]#Number of polygon parts
        try:
            for point in constent:
                numOfParts.append(point[0])
            numOfParts=set(numOfParts)
            partcount=""
            if len(numOfParts)==2:
                partcount="singlepart"
            elif len(numOfParts)>2:
                partcount="multipart"  
            self.partLength=len(numOfParts)
            return list(numOfParts)
        except Exception as e:
            print(str(e))
            raise Exception("Error processing part count. Text or CSV file not properly formated :"+str(e))
        finally:
            self.logger.printInfoMessage(f"Function name: FindNumberOfParts--Processing {partcount} file...")  
 
 
    def checkType(self,part):
        try:
            if int(part):
                return True
        except Exception as e:
            return False                   
      
      
    def checkLength(self):
            ##        ***This method creates a geometry of polygon/s and add it to the geodatabase ***

                try:
                
                    print(self.job)
                    modified_file_name=self.job["attachmentname"]
                    original_file_name=self.job["originalattachment"]
                    fileType=self.job["filetype"]
                    actionType=self.job["action"]
                    projectname=self.job["projectname"]
                    tms=self.job["tms"]
                    # isApproved=self.job["isApproved"]
                   
                    # newName=self.job["newprojectname"]
                    
                    
                    
                    
                    
                    downloadPath=self.config["downloadPath"]
                    coastalbound=self.config["pathToCoastalZoneBoubary"]
                    subPathToCurrentBoundary=self.config["pathToCurrentBoundary"]
                    subPathToPreviousBoundary=self.config["pathToPreviousBoundary"]
                    sdeConnPath=self.config["sdeConnPath"]
                
                    downloadedFilePath=os.path.join(downloadPath,modified_file_name)
                    
                    
                    if actionType=="rename_existing_project":
                        pass
                    else:
                        
                        values=None
                        if fileType=="txt":
                            values= self.filterTextValues(downloadedFilePath)  
                        elif fileType=="csv":
                            values= self.filter_values_csv(downloadedFilePath) 
                    
                    
                    
                        textContent=self.transformCoord(values)
                    
                        print(textContent)
                
                        
                        # if os.path.exists(WorkHere):
                        #     shutil.rmtree(WorkHere)
                        # os.makedirs(WorkHere)
    
                                
                        
                        
                    
                        if self.CreateSDEConnection(sdeConnPath):
                            sdeconn=os.path.join(sdeConnPath,"ocrm.sde")
                            pathToCoastalZoneBoubary=os.path.join(sdeconn,coastalbound)
                            
                            currentbound = arcpy.CopyFeatures_management(pathToCoastalZoneBoubary,arcpy.Geometry())[0]
                            sR=currentbound.spatialReference
                            pathToCurrentBoundary=os.path.join(sdeconn,subPathToCurrentBoundary)
                            # pathToPreviousBoundary=self.config["pathToPreviousBoundary"]
                            
                            
                            Len=self.initFile(textContent)
                            array=[]
                        
                            if self.trueValue(Len)==2:#if the file has two columns, then singlepart
                                # ***SINGLEPART ***
                                for point in textContent:
                                    array.append(arcpy.Point(point[0],point[1]))
                                new_array=arcpy.Array(array)
                                polygon=arcpy.Polygon(new_array,sR)
                                
                                if polygon.__getattribute__('area')==0.0:
                                    print("Wrong coordinate format. Please check ")
                                    errorMessage="Incorrect boundary. Please verify if boundary has a valid area."
                                    raise Exception(errorMessage)
                    
                                POLY_AREA=polygon.__getattribute__('area')*0.0000229568
                                print(POLY_AREA)
                                if currentbound.contains(polygon):
                                    if actionType=="new_project":
                                        edit = arcpy.da.Editor(sdeconn)  
                                        edit.startEditing()  
                                        edit.startOperation()  
                                        Icursor = arcpy.da.InsertCursor(pathToCurrentBoundary, ["SHAPE@","DB_PROJECT","DB_DATE","TMS","POLY_AREA"])
                                        Icursor.insertRow([polygon,projectname,TodaysDate,tms,POLY_AREA])
                                        del Icursor
                                        edit.stopOperation()
                                        edit.stopEditing(True)
                                    elif  actionType=='update_existing_project':  
                                        edit = arcpy.da.Editor(sdeconn)  
                                        edit.startEditing()  
                                        edit.startOperation()  
                                        Icursor = arcpy.da.UpdateCursor(pathToCurrentBoundary, ["SHAPE@","DB_PROJECT","DB_DATE","TMS","POLY_AREA"])
                                        for row in Icursor:
                                            print(row[1])
                                            print(projectname)
                                            print(dir(row[1]))
                                            if((row[1].__contains__(projectname.strip()))):
                                        
                                                Icursor.updateRow([polygon,projectname,TodaysDate,tms,POLY_AREA])
                                        del Icursor
                                        edit.stopOperation()
                                        edit.stopEditing(True)
                
                                    else:
                                        pass
                                    #     self.Email.sendEmailRejected(self.bulkEmail,self.EmailSubject, self.emailAddress,self.ProjectName)
                                    #     print("{} is outside the Coastal zone and has been rejected-{}".format(FieldName,TodaysDate))
                                    #     arcpy.AddMessage("{} is outside the Coastal zone and has been rejected-{}".format(FieldName,TodaysDate))
                                    #     return False
                        
                            elif self.trueValue(Len)==3:#if the file has three columns, then multipart 
                                    # ***MULTIPART ***
                            
                                parts=self.FindNumberOfParts(textContent)
                                
                                parts=sorted(parts)
                                newArr=[]
                                polygonArr={}
                                print(parts)
                                for i in range(0,self.partLength):
                                    polygonArr[i]=[]                 
                                t=0
                                for part in parts:
                                    if self.checkType(part):
                                        partCount=[]
                                        for point in textContent:
                                            if part==point[0]:
                                                partCount.append(part)
                                                polygonArr[t].append(arcpy.Point(point[1],point[2]))                                              
                                        if len(partCount)<3:
                                            print("One or more of your multipart features has less than 3 points, Invalid content in text file. Check {}".format(point))
                                            errorMessage="One or more of your multipart features has less than 3 points, Invalid content in text file. Check {}".format(point)
                                            raise Exception(errorMessage)
                                        t=t+1
                                for pt in polygonArr:
                                    newArr.append(polygonArr[pt])
                                polygon=arcpy.Polygon(arcpy.Array(newArr),sR)
                            
                                if polygon.__getattribute__('area')==0.0:
                                    print("Wrong coordinate format. Please check ")
                                    errorMessage="Incorrect boundary. Please verify if boundary has a valid area."
                                    raise Exception(errorMessage)
                                
                                POLY_AREA=polygon.__getattribute__('area')*0.0000229568
                                print(POLY_AREA)
                                if currentbound.contains(polygon):
                                    if actionType=="new_project":
                                        edit = arcpy.da.Editor(sdeconn)  
                                        edit.startEditing()  
                                        edit.startOperation()  
                                        Icursor = arcpy.da.InsertCursor(pathToCurrentBoundary, ["SHAPE@","DB_PROJECT","DB_DATE","TMS","POLY_AREA"])
                                        Icursor.insertRow([polygon,projectname,TodaysDate,tms,POLY_AREA])
                                        del Icursor
                                        edit.stopOperation()
                                        edit.stopEditing(True)
                                    elif  actionType=='update_existing_project':  
                                        edit = arcpy.da.Editor(sdeconn)  
                                        edit.startEditing()  
                                        edit.startOperation()  
                                        Icursor = arcpy.da.UpdateCursor(pathToCurrentBoundary, ["SHAPE@","DB_PROJECT","DB_DATE","TMS","POLY_AREA"])
                                        for row in Icursor:
                                            if((row[0].lower().strip().__contains__(projectname.lower().strip()))):
                                                row[0]=newName
                                            Icursor.updateRow([polygon,projectname,TodaysDate,tms,POLY_AREA])
                                        del Icursor
                                        edit.stopOperation()
                                        edit.stopEditing(True)
                                #         deleted=self.__isFileExistDeleteRow(FieldName)
                                #     Icursor.insertRow([polygon,FieldName,TodaysDate,self.TMS,POLY_AREA])
                                #     print("{} has been added successfully-{}".format(FieldName,TodaysDate))
                                #     arcpy.AddMessage("{} has been added successfully-{}".format(FieldName,TodaysDate))
                                #     return True
                                # else:
                                #     self.Email.sendEmailRejected(self.bulkEmail,self.EmailSubject, self.emailAddress,self.ProjectName)
                                #     print("{} is outside the Coastal zone and has been rejected-{}".format(FieldName,TodaysDate))
                                #     arcpy.AddMessage("{} is outside the Coastal zone and has been rejected-{}".format(FieldName,TodaysDate))
                                #     print("------------------------------------------------------")
                                #     return False
                            elif self.trueValue(Len)==None:
                                print("Your file is not properly formatted, please check your delimiter")
                            #     errorMessage="Your file is not properly formatted, please check your delimiter"
                            #     self.Email.sendEmailInvalid(self.bulkEmail,self.EmailSubject, self.emailAddress,self.ProjectName,errorMessage)
                            #     return False

                            # del Icursor
                except Exception as e:
                    print(str(e))
                    self.logger.printErrorMessage("Exception occurred while processing file :"+str(e))   
                    return 1,str(e)

                finally:
                 self.logger.printInfoMessage("Processing completed successfully :")   
           


 
    #  self.logger.printErrorMessage("Error occurred while reading csv file :"+str(e))




        
        
        
        
        
        
        
        
        
        
        
        
        
      
      
      
      
      
      
      
      
      
      
      
      
      
      
      
      
      
      
      
      
      
      
      
      
        

          








  





#     def checkPDFFile(self):
# ##        ***Check for the existence of a PDF***
#         try:
#             oldname=PDFpath+self.pdfName
#             if  os.path.exists(oldname):
#                 return True
#             else:
#                 return False
#         except Exception as e:
#             print(str(e))




            
    # def __storeRenameRequestEmail(self,oldprojName,newprojName,msg):
    # ##        ***Method to store rename request while waiting for approval ***
    #     try:
    #         projectName=oldprojName.strip(" ").encode(encoding='ascii',errors='ignore')
    #         renameData=shelve.open(projectRenameDataStore) 
    #         renameData[projectName]={
    #             "senderEmail":self.emailAddress,
    #             "requesttedUpdateOn":str(self.timeStamp()),
    #             "oldProjectName":projectName,
    #             "requestSubject":msg.Subject.encode(encoding='ascii',errors='ignore'),
    #             "NewProjectName":newprojName
    #             }
    #         renameData.close()
    #         self.__sendRenameEmailToOCRM(msg,oldprojName,newprojName)
    #     except Exception as e:
    #         print(str(e))


            

    def __updateProjectName(self,oldName,newName):
        ##        ***Method to updates the project name***
        fields=["DB_PROJECT"]
                # Process: Start Edit  
        editingWs="Database Connections\\gissde_ocrm_os.sde"
        edit = arcpy.da.Editor(editingWs)  
        edit.startEditing()  
        edit.startOperation() 
        try:         
                with arcpy.da.UpdateCursor(Coastal_zone, fields) as cursor:
                    for row in cursor:
                        if((row[0].lower().strip().__contains__(oldName.lower().strip()))):
                            row[0]=newName
                        cursor.updateRow(row)
                    print("{} has been updated successfully-{}".format(newName,TodaysDate))
                    arcpy.AddMessage("{} has been updated successfully-{}".format(newName,TodaysDate))
        except Exception as e:
            print(str(e))

        else:
            pass
        finally:
            del cursor
            edit.stopOperation()
            edit.stopEditing(True)

            



    def createExtentGeometry(self):
        try:
            currentgeometries = arcpy.CopyFeatures_management(self.updatedlayername,arcpy.Geometry())
            return currentgeometries
        except Exception as e:
            print(str(e))



    # def setVariables(self,currentMail,ESubject, eAddress,ProjName,fc,TMS,fileType,coastalbound):       
    #     self.bulkEmail=currentMail
    #     self.EmailSubject=ESubject
    #     self.emailAddress=eAddress
    #     self.ProjectName=ProjName
    #     self.fc=fc
    #     self.TMS=TMS.strip()
    #     self.fileType=fileType
    #     self.coastalbound=coastalbound

    
 
 

    def __isFileExistDeleteRow(self,fullFieldName):
        fields=["DB_PROJECT"]
        FieldName=os.path.splitext(fullFieldName)[0]
        # Process: Start Edit  
        try:         
            delcursor= arcpy.da.UpdateCursor(self.fc, fields)
            for row in delcursor:
              if row[0]:
                if row[0].encode(encoding='ascii',errors='ignore').lower().strip()==(FieldName.lower().strip()):
                    print("{0} deleted successfully....".format(row[0]))
                    delcursor.deleteRow()
                    return True
            del delcursor
        except Exception as e:
            print(str(e))

 
 

  


                


            
           
    def checkfloat(self,value):
        ##        ***This code checks if the content in file is a float/number or text, in which case it will be rejected ***
        try:
            val2=value.strip()           
            return float(val2)
        except ValueError:
            print("Your file contains invalid content. Please check")
            self.Email.sendEmailWithInvalidContent(self.bulkEmail,self.EmailSubject, self.emailAddress,self.ProjectName)







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


def main():
    try:
        appConfig=getConfigSettings("app.cfg")
        Eml=TextFileProc()
        Eml.checkLength()
    except Exception as e:
        raise e
       
 
if __name__ == '__main__': 
        # ***Call Class***    
    intreturncode=main(sys.argv)
    print("Exit code - "+str(intreturncode))
    sys.exit(intreturncode)

    


