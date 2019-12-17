import arcpy


class Toolbox(object):
    def __init__(self):
        """Define the toolbox (the name of the toolbox is the name of the
        .pyt file)."""
        self.label = "zMPScustomToolz_2019"
        self.alias = "zMPScustomToolz_2019"

        # List of tool classes associated with this toolbox
        self.tools = [fcsGlimpse, SimpleMultiBuf]


class fcsGlimpse(object):
    def __init__(self):
        """Define the tool (tool name is the name of the class)."""
        self.label = "FeatureClass Glimpse"
        self.description = "View general FeatureClass information such as FeatureClass Structure (polyline, Polygon, Point, etc), Field Name/Type, and technical Spatial Reference Information"
        self.canRunInBackground = False

    def getParameterInfo(self):
        """Define parameter definitions"""
        p0=arcpy.Parameter()
        p0.name='wksp'
        p0.displayName='Choose workspace where fcs is located:'
        p0.datatype=('Workspace', 'Feature Dataset')
        
        p1=arcpy.Parameter()
        p1.name='fcs'
        p1.displayName='Choose FeatureClass to generate report on:'
        params = [p0,p1]
        return params

    def isLicensed(self):
        """Set whether tool is licensed to execute."""
        return True

    def updateParameters(self, parameters):
        """Modify the values and properties of parameters before internal
        validation is performed.  This method is called whenever a parameter
        has been changed."""
        if parameters[0].altered:
            arcpy.env.workspace=parameters[0].value
            fcs=arcpy.ListFeatureClasses()
            if fcs:
                parameters[1].filter.list=fcs
            elif not fcs:
                parameters[1].filter.list=[]
        return

    def updateMessages(self, parameters):
        """Modify the messages created by internal validation for each tool
        parameter.  This method is called after internal validation."""
        return

    def execute(self, parameters, messages):
        """The source code of the tool."""
        p0=parameters[0].valueAsText.encode('unicode-escape').replace("\\","/")
        arcpy.env.workspace=p0
        desc=arcpy.Describe(parameters[1].valueAsText)
        report=[]
        report.append("FeatureClass '{0}' has {1} structure".format(desc.name,desc.shapeType))
        report.append("Extents as follows: Xmin={0}|max={1}, Ymin={2}|max{3}".format(round(desc.extent.XMin,1),round(desc.extent.XMax,1),round(desc.extent.YMin,1),round(desc.extent.YMax,1)))
        for i in ["Fields: "]:
            rFields=i
            report.append(rFields)
            for n,ii in enumerate(desc.fields):
                ct=n+1
                fld="|F{0} name is '{1}'/ Type is '{2}'".format(ct,ii.name,ii.type)
                rFields=rFields+fld
                report.append(fld)
        report.append("Spatial Reference Info: "+desc.spatialReference.exporttostring())
        for i in report:
            arcpy.AddMessage(i)
        arcpy.AddMessage("Scripted by Marc Santos | twitter: @CorvoProfano")
        return

class SimpleMultiBuf(object):
    def __init__(self):
        """Define the tool (tool name is the name of the class)."""
        self.label = "Multiple Single Part Buffers"
        self.description = "Run multiple buffer analyses: results are Singlepart and Round Ended; Default outputs workspace is same as input though you have option to change."
        self.canRunInBackground = False

    def getParameterInfo(self):
        """Define parameter definitions"""
        p0=arcpy.Parameter()
        p0.name='wksp'
        p0.displayName='Choose workspace/geodatabase where input feature class or shapefile is located:'
        p0.datatype=('Workspace', 'Feature Dataset')
        
        p1=arcpy.Parameter()
        p1.name='fcs'
        p1.displayName='Choose FeatureClass to buffer:'
        
        p2=arcpy.Parameter()
        p2.name='outDif'
        p2.displayName='Save output featureclasses to different workspace/geodatabse/dataset?'
        p2.datatype='Boolean'
        p2.parameterType='Optional'
        p2.category="Specifiy output workspace? (default same as input)"
        
        p3=arcpy.Parameter()
        p3.name='outWksp'
        p3.displayName='Choose output workspace/geodatabase where buffer outputs will be generated:'
        p3.datatype=('Workspace', 'Feature Dataset')
        p3.enabled=False
        p3.parameterType='Optional'
        p3.category="Specifiy output workspace? (default same as input)"
        
        p4=arcpy.Parameter()
        p4.name='Units'
        p4.displayName='Choose the units of the buffer distance:'
        p4.filter.list=['Meters','Feet','Miles','Kilometers']
        
        p5=arcpy.Parameter()
        p5.name='distance'
        p5.displayName='Enter the distance(s) to be used in the buffers (max=5000):'
        p5.datatype='GPValueTable'
        p5.columns=[['Long','Length:']]
        p5.filters[0].type='Range'
        p5.filters[0].list=[0,5000]
        
        
        p6=arcpy.Parameter()
        p6.name='End'
        p6.displayName='Do you want buffer ends to be Flat or Round?'
        p6.filter.list=['FLAT','ROUND']
        
        p7=arcpy.Parameter()
        p7.name='PlanGeo'
        p7.displayName='Do you want your bufffers to be calculated via Planar or Geodesic analysis?'
        p7.filter.list=['PLANAR','GEODESIC']
        params = [p0,p1,p2,p3,p4,p5,p6,p7]
        return params

    def isLicensed(self):
        """Set whether tool is licensed to execute."""
        return True

    def updateParameters(self, parameters):
        """Modify the values and properties of parameters before internal
        validation is performed.  This method is called whenever a parameter
        has been changed."""
        arcpy.env.overwriteOutput=True
        arcpy.env.workspace=parameters[0].valueAsText
        if parameters[0].altered:
            fcs=arcpy.ListFeatureClasses()
            if fcs:
                parameters[1].filter.list=fcs
            elif not fcs:
                parameters[1].filter.list=['No featureclasses found in slected gdb/dataset']
        if parameters[2].altered:
            parameters[3].enabled=parameters[2].value
        return

    def updateMessages(self, parameters):
        """Modify the messages created by internal validation for each tool
        parameter.  This method is called after internal validation."""
        return

    def execute(self, parameters, messages):
        """The source code of the tool."""
        p0=parameters[0].valueAsText
        p1=str(parameters[1].valueAsText)
        p2=parameters[2].valueAsText
        p3=parameters[3].valueAsText
        p4=str(parameters[4].valueAsText)
        p6=parameters[6].valueAsText
        p7=parameters[7].valueAsText
        wksp=p0.encode('unicode-escape').replace("\\","/")
        arcpy.env.workspace=wksp
        wkspO=wksp
        if p2:
            if p3:
                wkspO=p3.encode('unicode-escape').replace("\\","/")
        bufs=[]
        for i in parameters[5].valueAsText.split(";"):
            bufs.append(i.strip(" "))
        desc=arcpy.Describe(wksp+"/"+p1)
        ct=0
        for i in bufs:
            inp=desc.catalogPath
            fcs_o=wkspO+"/"+desc.basename+"_Buf"+str(i)+p4
            argBuf="{0} {1}".format(str(i),p4)
            try:
                arcpy.Buffer_analysis(inp,fcs_o,argBuf,"FULL",p6,"ALL","",p7)
                arcpy.AddMessage("Success: '"+argBuf+"' saved to "+fcs_o)
                ct+=1
            except arcpy.ExecuteError:
                arcpy.AddMessage("Issues with '{0}'; continued with rest of buffers".format(argBuf))
                arcpy.AddMessages(arcpy.GetMessages(0))
        arcpy.AddMessage(str(ct)+" features successfully created. Scripted by Marc Santos | twitter: @CorvoProfano")
        return
