import arcpy


def run_reviewer_batch_job(reviewer_db, session, checks_rbj, prod_data):

    # Check out a Data Reviewer extension license
    arcpy.CheckOutExtension("datareviewer")

    arcpy.env.overwriteOutput = "true"

    # Execute Reviewer Batch Job function
    res = arcpy.ExecuteReviewerBatchJob_Reviewer(reviewer_db, session, checks_rbj, prod_data)

    arcpy.CheckInExtension("datareviewer")


def create_reviewer_workspace(workspacepath, name, session):
    # Check out a Data Reviewer extension license
    arcpy.CheckOutExtension("datareviewer")

    # Set environment
    arcpy.env.workspace = workspacepath

    # Create new geodatabase
    workspace = arcpy.CreateFileGDB_management(workspacepath, name)

    # Execute EnableDataReviewer
    arcpy.EnableDataReviewer_Reviewer(workspace, "2227", "#", "DEFAULTS")
    print "created spatial reference"

    # Create a new Reviewer session
    arcpy.CreateReviewerSession_Reviewer(workspace, session, "#")

    arcpy.CheckInExtension("datareviewer")


def write_to_reviewer_table(reviewer_db, session, feature, field, orig_table_name):

    # Check out a Data Reviewer extension license
    arcpy.CheckOutExtension("datareviewer")

    arcpy.env.overwriteOutput = "true"

    arcpy.WriteToReviewerTable_Reviewer(reviewer_db, session, feature, field, orig_table_name)

    arcpy.CheckInExtension("datareviewer")


def create_reviewer_session(reviewer_db, session):
    # Check out a Data Reviewer extension license
    arcpy.CheckOutExtension("datareviewer")

    arcpy.env.overwriteOutput = "true"

    arcpy.CreateReviewerSession_Reviewer(reviewer_db, session)

    arcpy.CheckInExtension("datareviewer")