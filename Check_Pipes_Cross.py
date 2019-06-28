# Purpose: Identify the intersection points of two pipes meet the following criteria: same pressure zone and
# without a "jump".
# Steps: Use the first Reviewer Batch job to identify the pipes cross with same pressure zone, use GP tools to
# clip pipeline with 5 feet buffer from intersection points, use the second batch job to identify the jumps
# (nonlinear lines and digitalized lines), use GP tools to select the intersection points not on any jumps,
# and write the data validation result to the Reviewer table.

import arcpy
from arcpy import env
from Utility_DataReviewer import run_reviewer_batch_job, create_reviewer_workspace, write_to_reviewer_table, \
    create_reviewer_session

env.overwriteOutput = True

# Set workspace environment
# Prompt user for the production workspace directory
strDirectory = arcpy.GetParameterAsText(0) + "/"
# Prompt user for batch job directory
strRBJFile = arcpy.GetParameterAsText(1) + "/"
env.workspace = strDirectory + "EBMUDCopy_GeoNetwork.gdb"
env.qualifiedFieldNames = False  # The output field name will not include the table name.

# Set data reviewer variables
str_session1 = "PipesCrossSamePZ"
str_session2 = "FindJump"
str_session3 = "IntersectPointsNoJump"
str_reviewer_name = "Reviewer_CrossedPipes"
str_reviewer_db = strDirectory + "/" + str_reviewer_name + ".gdb"
str_reviewer_rbj1 = strRBJFile + "PipeCrossSamePZ.rbj"
str_reviewer_rbj2 = strRBJFile + "FindJump.rbj"
str_prod_workspace = strDirectory + "/" + "EBMUDCopy_GeoNetwork.gdb"
#
# Call function to create Reviewer workspace
create_reviewer_workspace(strDirectory, str_reviewer_name, str_session1)

# Pipes cross same PZ, run batch job and write to Reviewer session 1
run_reviewer_batch_job(str_reviewer_db, "Session 1 : " + str_session1, str_reviewer_rbj1, str_prod_workspace)
#
# Pipe crossing intersect points
# Make Feature Layer
# wPressurizedMain = env.workspace + "/Water_Distribution_Network/wPressurizedMain"
wPressurizedMain = strDirectory + "EBMUDCopy_GeoNetwork.gdb" + "/" + "Water_Distribution_Network/wPressurizedMain"
arcpy.MakeFeatureLayer_management(wPressurizedMain, 'wPressurizedMain_Layer')
# Process: Make Table View
REVTABLEMAIN = str_reviewer_db + "/" + "REVTABLEMAIN"
REVTABLEMAIN_S1 = "REVTABLEMAIN_S1"

arcpy.MakeTableView_management(REVTABLEMAIN, REVTABLEMAIN_S1, "SESSIONID = 1")
#
# Process: Add Join
arcpy.AddJoin_management('wPressurizedMain_Layer', "OBJECTID", REVTABLEMAIN_S1, "OBJECTID", "KEEP_COMMON")

# Process: Intersect
Intersect_Points = strDirectory + "EBMUDCopy_GeoNetwork.gdb" + "/" + "CrossedPipes_Intersect_Point"
arcpy.Intersect_analysis("wPressurizedMain_Layer #", Intersect_Points, "ALL", "", "POINT")

# Select points not at pipe end, buffer to 5 feet, clip pipes
# Set feature class variables
CrossedPipes_Intersect_Point = strDirectory + "EBMUDCopy_GeoNetwork.gdb" + "/" + "CrossedPipes_Intersect_Point"
Points_5ft_Buffer = strDirectory + "EBMUDCopy_GeoNetwork.gdb" + "/" + "CrossedPipes_Intersect_Point_5ftBuffer"
Pipes_Clipped_5ft_Buffer = strDirectory + "EBMUDCopy_GeoNetwork.gdb" + "/" + "Pipes_Clipped_5ft_Buffer"
Intersect_Points_Within_Pipe = strDirectory + "EBMUDCopy_GeoNetwork.gdb" + "/" + "Intersect_Points_Within_Pipe"
AllJumps = strDirectory + "EBMUDCopy_GeoNetwork.gdb" + "/" + "AllJumps"
IntersectPointsNoJump = strDirectory + "EBMUDCopy_GeoNetwork.gdb" + "/" + "IntersectPointsNoJump"

arcpy.MakeFeatureLayer_management(CrossedPipes_Intersect_Point, 'CrossedPipes_Intersect_Point_Layer')
arcpy.SelectLayerByLocation_management('CrossedPipes_Intersect_Point_Layer', "COMPLETELY_WITHIN", wPressurizedMain)
arcpy.CopyFeatures_management('CrossedPipes_Intersect_Point_Layer', Intersect_Points_Within_Pipe)

arcpy.Buffer_analysis(Intersect_Points_Within_Pipe, Points_5ft_Buffer, "5 Feet", "FULL", "ROUND", "NONE", "",
                      "PLANAR")

arcpy.Clip_analysis(wPressurizedMain, Points_5ft_Buffer, Pipes_Clipped_5ft_Buffer, "")

# Find jumps run reviewer batch job
create_reviewer_session(str_reviewer_db, "FindJump")
# arcpy.CreateReviewerSession_Reviewer(str_reviewer_db, "FindJump")
run_reviewer_batch_job(str_reviewer_db, "Session 2 : " + str_session2, str_reviewer_rbj2, str_prod_workspace)

# Pipes cross no jump
# Create Reviewer session 2 table view
REVTABLEMAIN = str_reviewer_db + "/" + "REVTABLEMAIN"
REVTABLEMAIN_S2 = "REVTABLEMAIN_S2"

arcpy.MakeTableView_management(REVTABLEMAIN, REVTABLEMAIN_S2, "SESSIONID = 2")

# Join table view to Pipes_Clipped_5ft_Buffer
arcpy.MakeFeatureLayer_management(Pipes_Clipped_5ft_Buffer, 'Pipes_Clipped_5ft_Buffer_Layer')
arcpy.AddJoin_management('Pipes_Clipped_5ft_Buffer_Layer', "OBJECTID", REVTABLEMAIN_S2, "OBJECTID", "KEEP_COMMON")

# Copy feature to AllJumps feature class
arcpy.CopyFeatures_management('Pipes_Clipped_5ft_Buffer_Layer', AllJumps)

# Select Intersect_Points_Within_Pipe intersect AllJumps Invert
arcpy.MakeFeatureLayer_management(Intersect_Points_Within_Pipe, 'Intersect_Points_Within_Pipe_Layer')
arcpy.SelectLayerByLocation_management('Intersect_Points_Within_Pipe_Layer', "INTERSECT", AllJumps,
                                       '0.1 feet', invert_spatial_relationship="INVERT")
arcpy.CopyFeatures_management('Intersect_Points_Within_Pipe_Layer', IntersectPointsNoJump)

# Delete identical points
arcpy.DeleteIdentical_management(IntersectPointsNoJump, "SHAPE")

# Write to reviewer session 3
create_reviewer_session(str_reviewer_db, str_session3)

write_to_reviewer_table(str_reviewer_db, "Session 3 : " + str_session3, IntersectPointsNoJump, "OBJECTID",
                        "IntersectPointsNoJump")
