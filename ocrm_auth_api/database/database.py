import sqlite3
import sys,os

dbPath="C:/OCRMJOBS/sqlitedb/ocrmdigitalboundary.sqlite"
dbDirPath="C:/OCRMJOBS/sqlitedb"
def CreateDatabaseTable(args):
    """This function will create a sqlite table
    Args:
        args (list): Script name
    Returns:
        Integer: 1/0
    """
    try:
        if not os.path.exists(dbDirPath):
                    os.makedirs(dbDirPath)      
        db=sqlite3.connect(dbPath)
        db.execute("CREATE TABLE IF NOT EXISTS ocrmdigitalboundary (id TEXT PRIMARY KEY, projectname text,tms text,action text,email text,status text,message text,insertstatusdate text,updatestatusdate text,attachmentname text, originalattachment text,filetype text,newprojectname text,isAprovalRequired integer,isApproved integer)")
        db.close()
        return 0
    except Exception as e:
        print("Exception occurred in CreateDatabaseTable function :"+ str(e))
        return 1


if __name__=="__main__":
    intreturncode=CreateDatabaseTable(sys.argv)
    print("Exit code - "+str(intreturncode))
    sys.exit(intreturncode)
    