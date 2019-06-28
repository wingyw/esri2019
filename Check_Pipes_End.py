# Purpose: Identify the pipes overshoot/undershoot or the pipe ends do not have proper device.
# Steps: Leverage the ArcGIS GP tool, use the GP result as the input for Reviewer batch job, and write the
# data validation result to the Reviewer table.

import arcpy
from arcpy import env
from Utility_DataReviewer import run_reviewer_batch_job, create_reviewer_workspace

env.overwriteOutput = True

# Set workspace environment
strDirectory = arcpy.GetParameterAsText(0) + "/"
# Prompt user for batch job directory
strRBJFile = arcpy.GetParameterAsText(1) + "/"
env.workspace = strDirectory + "EBMUDCopy_GeoNetwork.gdb"
env.qualifiedFieldNames = False  # The output field name will not include the table name.

# Set data reviewer variables
str_session = "PipesDoNotConnect"
str_reviewer_name = "Reviewer_PipesDoNotConnect"
str_reviewer_db = strDirectory + "/" + str_reviewer_name + ".gdb"
str_reviewer_rbj = strRBJFile + "CheckPipeConnect.rbj"
str_prod_workspace = strDirectory + "/" + "EBMUDCopy_GeoNetwork.gdb"

# Find dangle
wPressurizedMain = strDirectory + "EBMUDCopy_GeoNetwork.gdb" + "/" + "Water_Distribution_Network/wPressurizedMain"
wPressurizedMain_Dangle = strDirectory + "EBMUDCopy_GeoNetwork.gdb" + "/" + "wPressurizedMain_Dangle"
arcpy.FeatureVerticesToPoints_management(wPressurizedMain, wPressurizedMain_Dangle, "DANGLE")

# Call function to create Reviewer workspace
create_reviewer_workspace(strDirectory, str_reviewer_name, str_session)

# Execute data reviewer batch job file
run_reviewer_batch_job(str_reviewer_db, "Session 1 : " + str_session, str_reviewer_rbj, str_prod_workspace)

