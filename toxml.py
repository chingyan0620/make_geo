from datetime import datetime 
from lxml import etree
from osgeo import gdal, ogr, osr
from tools import Tool
import re ,json

class build_xml_data():
    def __init__(self,data_list) -> None:
        
        self.data = data_list
        self.S124_upperCorner = ""
        self.S124_lowerCorner = ""
        self.geom_list = []
        self.geojson = []
        self.res_dict = {"subject":[],"content_time":[],"radius":0,"geo_list":[],"unit":"","numYear":""}
        
        self.build_obj = self.iter_list()
        # print(self.res_dict)
        self.get_geom()
        self.s124 = self.build_xml()
        

    def iter_list(self):
        time_in = True
        geo_in = True
        tmp_str = "" 
        tmp_geo = [0,0]
        tmp_pos = []
        for idx ,i in enumerate(self.data):

            if i[1] == "B-msg.end":
                break
            if i[1] == "B-msg.time":
                self.res_dict["publictime"] = i[0]
            if i[1] == "I-msg.time":
                try:
                    self.res_dict["year"] = datetime.strptime(i[0],"%Y")
                except:
                    pass
                try:
                    self.res_dict["month"] = datetime.strptime(i[0],"%b")
                except:
                    pass
            if i[1] == "B-msg.num_year":
                self.res_dict["numYear"] = i[0]
            if i[1] == "B-content.subject" or i[1] == "I-content.subject":
                self.res_dict["subject"].append(i[0])
            if i[1] == "B-content.time":
                # self.res_dict["content_time"].append(i[0])
                tmp_str = ""
                tmp_str = i[0]
                if(self.data[idx+1][1] != "I-content.time" or self.data[idx+1][1] == "B-content.time"):
                    self.res_dict["content_time"].append(tmp_str)
                    tmp_str = ""
            if i[1] == "I-content.time":
                tmp_str = tmp_str + " " + i[0]
                if(self.data[idx+1][1] != "I-content.time"):
                    self.res_dict["content_time"].append(tmp_str)
                    tmp_str = ""

            if i[1] == "B-geo.lat":
                tmp_geo[1] = i[0]
            if i[1] == "B-geo.lon":
                tmp_geo[0] = i[0]
            if i[1] == "B-geo.rad":
                self.res_dict["radius"] = i[0]

            if tmp_geo[0] != 0 and tmp_geo[1] != 0:
                tmp_pos.append(" ".join(tmp_geo))
                tmp_geo = [0,0]
            if(self.data[idx +1][1] != "B-geo.lat" and self.data[idx +1][1] != "B-geo.lon"):
                if len(tmp_pos) != 0:
                    self.res_dict["geo_list"].append(tmp_pos)
                    tmp_pos = []
                
            if i[1] == "B-geo.unit":
                self.res_dict["unit"] = i[0]
            if i[1] == "B-geo.rad":
                self.res_dict["radius"] = i[0]

        return self.res_dict
    
    def get_geom(self):
        geo_list = self.res_dict["geo_list"]
        
        coor_warp = 0
        geo_type = "point"        #可能會碰到一個以上，之後處理   
        pos_listN = []
        pos_listE = []
        wkt = ""
        for pos in geo_list:
            os_listN = []
            pos_listE = []
            for words in pos:
                single_word = words.split(" ")

                for word in single_word:
                    word = word.replace(".","1234321")
                    word = word.strip()
                    res_tmp = re.findall('(\d+|[A-Za-z])', word)
                    
                    tmpp = ""
                    NN = ""
                    res = []
                    for iii in res_tmp:
                        try:
                            aa = float(iii)
                            res.append(iii)
                        except Exception as e:
                            tmpp = iii
                            
                    if "N" in word or "S" in word :
                        res.append(tmpp)
                        if len(res) == 2:
                            val = res[0].replace("1234321",'.')
                            NN = val
                        if len(res) == 3:
                            NN = Tool.dm2dd(res)
                        if len(res) == 4:
                            NN = Tool.dms2dd(res)
                        pos_listN.append(NN)
                    if "E" in word or "W" in word :
                        res.append(tmpp)
                        if len(res) == 2:
                            val = res[0].replace("1234321",'.')
                            EE = val
                        if len(res) == 3:
                            EE = Tool.dm2dd(res)
                        if len(res) == 4:
                            EE = Tool.dms2dd(res)
                        pos_listE.append(EE)

                    if ("N" not in word and "E" not in word):
                        if len(res) == 1:
                            val = res[0].replace("1234321",'.')
                            NN = val
                        elif len(res) == 2:
                            tmp = res
                            tmp.append('N')
                            NN = Tool.dm2dd(tmp)
                        
                        elif len(res) == 3:
                            tmp = res
                            tmp.append('N')
                            NN = Tool.dms2dd(tmp)
                        if append_count % 2 == 0:
                            if coor_warp == "1":
                                pos_listN.append(NN)
                            if coor_warp == "0":
                                pos_listE.append(NN)
                        if append_count % 2 == 1:
                            if coor_warp == "1":
                                pos_listE.append(NN)
                            if coor_warp == "0":
                                pos_listN.append(NN)
                        append_count += 1
            if len(pos_listE) == 1:
                geo_type = "point"
            elif len(pos_listE) == 2:
                geo_type ="linstring"
            elif len(pos_listE) >2:
                geo_type ="polygon"
            if self.res_dict["radius"] != 0:
                geo_type ="circle"
        

            if geo_type == "point":
                # print(pos_dict)
                self.res_dict["geo_type"] = "point"
                point = ogr.Geometry(ogr.wkbPoint)
                point.AddPoint(float(pos_listE[0]) , float(pos_listN[0]))
                wkt = point
                geojson = point.ExportToJson()
                self.geom_list.append(point.ExportToWkt())

                result = {"type": "FeatureCollection","name": "test.geojson"}
                result.update({"features": [{"type": "Feature", "properties": {'name': 'EPSG:4326'}, "geometry":json.loads(geojson)}]})
                self.geojson.append(result)

            if geo_type == "linstring":
                self.res_dict["geo_type"] = "linstring"

                line = ogr.Geometry(ogr.wkbLineString)
                for i in range(len(pos_listE)):
                    line.AddPoint(float(pos_listE[i]) , float(pos_listE[i]))
                wkt = line
                line = poly.GetEnvelope()
                self.S124_upperCorner = str(env[0])+" "+str(env[2])
                self.S124_lowerCorner = str(env[1])+" "+str(env[3])
                geojson = line.ExportToJson()
                self.geom_list.append(line.ExportToWkt())
                # self.geojson.append(geojson)
                # result = {"type": "FeatureCollection","name": "test.geojson"}
                # result.update({"features": [{"type": "Feature", "properties": {'name': 'EPSG:4326'}, "geometry":json.loads(geojson)}]})
                result = {"type": "FeatureCollection","name": "test.geojson"}
                result.update({"features": [{"type": "Feature", "properties": {'name': 'EPSG:4326'}, "geometry":json.loads(geojson)}]})
                self.geojson.append(result)

            if geo_type =="polygon":
                self.res_dict["geo_type"] = "polygon"
                ring = ogr.Geometry(ogr.wkbLinearRing)
                for i in range(len(pos_listE)):
                    # ring.AddPoint(float(pos_dict["pos_N"][i]) , float(pos_dict["pos_E"][i]))
                    ring.AddPoint(float(pos_listE[i]) , float(pos_listN[i]))
                ring.AddPoint(float(pos_listE[0]) , float(pos_listN[0]))
                poly = ogr.Geometry(ogr.wkbPolygon)
                poly.AddGeometry(ring)
                env = poly.GetEnvelope()
                self.S124_upperCorner = str(env[0])+" "+str(env[2])
                self.S124_lowerCorner = str(env[1])+" "+str(env[3])
                geojson = poly.ExportToJson()
                self.geom_list.append(poly.ExportToWkt())

                # self.geojson.append(geojson)
                result = {"type": "FeatureCollection","name": "test.geojson"}
                result.update({"features": [{"type": "Feature", "properties": {'name': 'EPSG:4326'}, "geometry":json.loads(geojson)}]})
                self.geojson.append(result)
            if geo_type == "circle":
                self.res_dict["geo_type"] = "circle"
                point = ogr.Geometry(ogr.wkbPoint)
                point.AddPoint(float(pos_listN[0]) , float(pos_listE[0]))
                mid_lon = 0.0
                for l in pos_listE:
                    mid_lon += float(l)
                mid_lon = round(float(mid_lon)/len(pos_listE))

                circle = Tool.do_buffer(point ,mid_lon  , float(self.res_dict["radius"]) , self.res_dict["unit"])
                circle2 = Tool.change_geo_type(circle)
                env = circle2.GetEnvelope()
                self.S124_upperCorner = str(env[0])+" "+str(env[2])
                self.S124_lowerCorner = str(env[1])+" "+str(env[3])
                geojson = circle2.ExportToJson()
                self.geom_list.append(circle2.ExportToWkt())

                # geojson = circle2.ExportToJson()
                # self.geojson.append(geojson)
                result = {"type": "FeatureCollection","name": "test.geojson"}
                result.update({"features": [{"type": "Feature", "properties": {'name': 'EPSG:4326'}, "geometry":json.loads(geojson)}]})
                self.geojson.append(result)

            
        


        # for idx ,i in enumerate(pos_listE):
        #     wkt = wkt + pos_listE[idx] +" "+pos_listN[idx]
        #     if idx <len(pos_listE):
        #         wkt = wkt + ","
        #     else:
        #         wkt = wkt +")"
        #         if geo_type == "POLYGON ":
        #             wkt = wkt +")"
        # if self.res_dict["radius"] != 0:
        #     Tool.do_buffer()
        # print(self.geojson)
        # print(self.S124_upperCorner)
        # print(self.S124_lowerCorner)


    def build_xml(self):
        xmlns = "http://www.iho.int/s100gml/5.0"
        xsi = 'http://www.w3.org/2001/XMLSchema-instance'
        schemaLocation = 'http://www.iho.int/S124/1.0 S-124_GML_Schemas_1.0.0.xsd'
        S124 = 'http://www.iho.int/S124/1.0'
        S100 = "http://www.iho.int/s100gml/1.0"
        gml = 'http://www.opengis.net/gml/3.2'
        # S100 = 'http://www.iho.int/s100gml/1.0'
        # xlink = 'http://www.w3.org/1999/xlink'
        if self.res_dict["numYear"] != "":
            year = self.res_dict["numYear"].split("/")[1]
            idd = self.res_dict["numYear"].split("/")[0][-4:]
        else:
            now = datetime.now()
            year = now.strftime("%Y")
            idd = "0000"
        id_o = 'TW.NAVTEX.{}.{}'.format(idd,year)
            # self.S124_year[-2:], self.S124_warningNum)
        # ns = {'xsi': xsi, 'gml': gml, 'S100': S100,'S124': S124, 'xlink': xlink}
        ns = {"xmlns":"http://www.iho.int/s100gml/5.0",'xsi': xsi, 'gml': gml, 'S124': S124,"S100":S100}
        id_ = 'NW.{}'.format(id_o)
        root = etree.Element('{' + S124 + '}Dataset',nsmap=ns,
        # root = etree.Element('{' + S124 + '}Dataset', 
                             attrib={'{' + xsi + '}schemaLocation': schemaLocation, '{'+gml+'}id': id_[3:]} ,)
        
        # build envelope geometry
        id_counter = 0
        srsname = "http://www.opengis.net/def/crs/EPSG/0/4326"
        boundedBy = etree.SubElement(root, '{' + gml + '}boundedBy')
        Envelope = etree.SubElement(boundedBy, '{' + gml + '}Envelope')
        Envelope.set('srsName', srsname)
        lowerCorner = etree.SubElement(Envelope, '{' + gml + '}lowerCorner')
        upperCorner = etree.SubElement(Envelope, '{' + gml + '}upperCorner')
        
        lowerCorner.text = self.S124_lowerCorner
        upperCorner.text = self.S124_upperCorner

        ##### build DatasetIdentificationInformation
        DatasetIdentificationInformation = etree.SubElement(root, 'DatasetIdentificationInformation')
        DatasetIdentificationInformation.set("xmlns",xmlns)
        encodingSpecification = etree.SubElement(DatasetIdentificationInformation , "encodingSpecification")
        encodingSpecification.text = "S-100 Part 10b"
        encodingSpecificationEdition = etree.SubElement(DatasetIdentificationInformation, 'encodingSpecificationEdition')
        encodingSpecificationEdition.text = "1.0"
        productIdentifier = etree.SubElement(DatasetIdentificationInformation, 'productIdentifier')
        productIdentifier.text = " "
        productEdition = etree.SubElement(DatasetIdentificationInformation, 'productEdition')
        productEdition.text = "0"
        applicationProfile = etree.SubElement(DatasetIdentificationInformation, 'applicationProfile')
        applicationProfile.text = ""
        datasetFileIdentifier = etree.SubElement(DatasetIdentificationInformation, 'datasetFileIdentifier')
        datasetFileIdentifier.text = "TAIWAN NAVTEX" # temp content
        datasetTitle = etree.SubElement(DatasetIdentificationInformation, 'datasetTitle')
        datasetTitle.text = " "
        datasetReferenceDate = etree.SubElement(DatasetIdentificationInformation, 'datasetReferenceDate')
        datasetReferenceDate.text = self.res_dict["year"].strftime("%Y-") + self.res_dict["month"].strftime("%m-%d")
        datasetLanguage = etree.SubElement(DatasetIdentificationInformation, 'datasetLanguage')
        datasetLanguage.text = "eng"
        datasetAbstract = etree.SubElement(DatasetIdentificationInformation, 'datasetAbstract')
        datasetAbstract.text = ""
        datasetTopicCategory = etree.SubElement(DatasetIdentificationInformation, 'datasetTopicCategory')
        datasetTopicCategory.text = "imageryBaseMapsEarthCover" # topic category 
        datasetPurpose = etree.SubElement(DatasetIdentificationInformation, 'datasetPurpose')
        datasetPurpose.text = "base"
        updateNumber = etree.SubElement(DatasetIdentificationInformation, 'updateNumber')
        updateNumber.text = "0"

        ##### build member 
        members = etree.SubElement(root, '{' + S124 + '}members')
        NAVWARNPreamble = etree.SubElement(members, '{' + S124 + '}NAVWARNPreamble')
        # NAVWARNPreamble.set('{' + gml + '}id', id_o+str(id_counter).zfill(4))  # gml id 
        NAVWARNPreamble.set('{' + gml + '}id', id_o+"."+str(id_counter))  # gml id 
        id_counter = id_counter + 1
        affectedChartPublications = etree.SubElement(NAVWARNPreamble, '{' + S124 + '}affectedChartPublications')
        chartAffected = etree.SubElement(affectedChartPublications, '{' + S124 + '}chartAffected')
        chartNumber = etree.SubElement(chartAffected, '{' + S124 + '}chartNumber')
        chartPlanNumber = etree.SubElement(chartAffected, '{' + S124 + '}chartPlanNumber')
        chartPlanNumber.text = "" # need to know rule
        editionDate = etree.SubElement(chartAffected, '{' + S124 + '}editionDate')
        editionDate.text = self.res_dict["year"].strftime("%Y-") + self.res_dict["month"].strftime("%m-%d")  #need change
        lastNoticeDate = etree.SubElement(chartAffected, '{' + S124 + '}lastNoticeDate')
        lastNoticeDate.text = self.res_dict["year"].strftime("%Y-") + self.res_dict["month"].strftime("%m-%d")  #need change
        chartPublicationIdentifier = etree.SubElement(affectedChartPublications, '{' + S124 + '}chartPublicationIdentifier')
        internationalChartAffected = etree.SubElement(affectedChartPublications, '{' + S124 + '}internationalChartAffected')# need to know rule
        language = etree.SubElement(affectedChartPublications, '{' + S124 + '}language')
        language.text = "eng"
        generalArea = etree.SubElement(NAVWARNPreamble, '{' + S124 + '}generalArea')
        locationName = etree.SubElement(generalArea, '{' + S124 + '}locationName')
        text = etree.SubElement(locationName, '{' + S124 + '}text')
        text.text = "some text"
        messageSeriesIdentifier = etree.SubElement(NAVWARNPreamble, '{' + S124 + '}messageSeriesIdentifier')
        agencyResponsibleForProduction = etree.SubElement(messageSeriesIdentifier, '{' + S124 + '}agencyResponsibleForProduction')
        countryName = etree.SubElement(messageSeriesIdentifier, '{' + S124 + '}countryName')
        countryName.text = "TWN" # ISO 3166-1 2 or 3 code  
        nameOfSeries = etree.SubElement(messageSeriesIdentifier, '{' + S124 + '}nameOfSeries')
        nameOfSeries.text = "NAVAREA XI"
        warningNumber = etree.SubElement(messageSeriesIdentifier, '{' + S124 + '}warningNumber')
        warningNumber.text = "0"
        warningType = etree.SubElement(messageSeriesIdentifier, '{' + S124 + '}warningType')
        warningType.text = "Local No Warning" # need to know rule
        warningType.set('code', '6')
        year = etree.SubElement(messageSeriesIdentifier, '{' + S124 + '}year')
        year.text = self.res_dict["year"].strftime("%Y")
        intService = etree.SubElement(NAVWARNPreamble, '{' + S124 + '}intService')
        intService.text = "true"
        navwarnTypeGeneral = etree.SubElement(NAVWARNPreamble, '{' + S124 + '}navwarnTypeGeneral')
        navwarnTypeGeneral.text = "Special Operations" # need to change
        navwarnTypeGeneral.set('code', '9')
        publicationTime = etree.SubElement(NAVWARNPreamble, '{' + S124 + '}publicationTime')
        parse_time = datetime.strptime(self.res_dict["publictime"],"%d%H%MUTC")
        publicationTime.text = self.res_dict["year"].strftime("%Y-") + self.res_dict["month"].strftime("%m-%d")+"T" + parse_time.strftime("%H:%M:%SZ")

        ## references
        References = etree.SubElement(members, '{' + S124 + '}References')
        References.set('{' + gml + '}id',  id_o+"."+str(id_counter))
        id_counter = id_counter + 1
        messageSeriesIdentifier = etree.SubElement(References, '{' + S124 + '}messageSeriesIdentifier')
        agencyResponsibleForProduction = etree.SubElement(messageSeriesIdentifier, '{' + S124 + '}agencyResponsibleForProduction')
        nameOfSeries = etree.SubElement(messageSeriesIdentifier, '{' + S124 + '}nameOfSeries')
        warningNumber = etree.SubElement(messageSeriesIdentifier, '{' + S124 + '}warningNumber')
        warningNumber.text = "0"
        warningType = etree.SubElement(messageSeriesIdentifier, '{' + S124 + '}warningType')
        warningType.text = "Coastal Navigational Warning" # need to know rule
        warningType.set('code', '2')
        year = etree.SubElement(messageSeriesIdentifier, '{' + S124 + '}year')
        year.text = self.res_dict["year"].strftime("%Y")
        noMessageOnHand = etree.SubElement(References, '{' + S124 + '}noMessageOnHand')
        noMessageOnHand.text = "false"
        referenceCategory = etree.SubElement(References, '{' + S124 + '}referenceCategory')
        referenceCategory.text = "In-Force" # need to change
        referenceCategory.set("code" , "2") # need to change

        ## NAVWARNPart
        NAVWARNPart = etree.SubElement(members, '{' + S124 + '}NAVWARNPart')
        NAVWARNPart.set('{' + gml + '}id',  id_o+"."+str(id_counter))
        id_counter = id_counter + 1
        featureName = etree.SubElement(NAVWARNPart, '{' + S124 + '}featureName')
        name = etree.SubElement(featureName, '{' + S124 + '}name')
        name.text = "" # add
        featureReference = etree.SubElement(NAVWARNPart, '{' + S124 + '}featureReference')
        dateTimeRange = etree.SubElement(featureReference, '{' + S124 + '}dateTimeRange')
        dateTimeEnd = etree.SubElement(dateTimeRange, '{' + S124 + '}dateTimeEnd')
        dateTimeEnd.text = "2023-12-30T09:30:47Z" #add
        dateTimeStart = etree.SubElement(dateTimeRange, '{' + S124 + '}dateTimeStart')
        dateTimeStart.text = "2023-12-31T09:30:47Z" #add
        # <n1:fixedDateRange>
        #     <n1:dateEnd>
        #         <gDay>---30</gDay>
        #     </n1:dateEnd>
        #     <n1:dateStart>
        #         <gDay>---31</gDay>
        #     </n1:dateStart>
        # </n1:fixedDateRange>
        warningInformation = etree.SubElement(NAVWARNPart, '{' + S124 + '}warningInformation')
        information = etree.SubElement(warningInformation, '{' + S124 + '}information')
        headline = etree.SubElement(information, '{' + S124 + '}headline') # add
        language = etree.SubElement(information, '{' + S124 + '}language')
        language.text = "eng"
        text = etree.SubElement(information, '{' + S124 + '}text') # add

        header = etree.SubElement(NAVWARNPart, '{' + S124 + '}header')
        # geometry = etree.SubElement(NAVWARNPart, '{' + S124 + '}geometry')

        # add geometry 
        #  only with point ,curve ,surface
        if self.res_dict["geo_type"] == "point":
            geometry = etree.SubElement(NAVWARNPart, '{' + S124 + '}geometry')
            pointProperty = etree.SubElement(geometry ,pointProperty)
            pointProperty.set("xmlns",xmlns)

            pointele = etree.SubElement(pointProperty , pointele)
            pointele.set('{' + gml + '}id' ,  id_o+"."+str(id_counter)) #add
            id_counter = id_counter + 1
            pos = etree.SubElement(pointele , pos)
            # add pos text

        # add linstring
            

        # add polygon
        if self.res_dict["geo_type"] == "polygon" or self.res_dict["geo_type"] == "circle":
            # surfaceProperty = etree.SubElement(geometry ,"surfaceProperty")
            # Surface = etree.SubElement(surfaceProperty ,"Surface")
            # Surface.set('{' + gml + '}id' , id_o+"."+str(id_counter)) #add
            # id_counter = id_counter + 1
            for geo in self.geojson:
                geometry = etree.SubElement(NAVWARNPart, '{' + S124 + '}geometry')
                surfaceProperty = etree.SubElement(geometry ,"surfaceProperty")
                surfaceProperty.set("xmlns",xmlns)
                
                Surface = etree.SubElement(surfaceProperty ,"Surface")
                Surface.set('{' + gml + '}id' , id_o+"."+str(id_counter)) #add
                id_counter = id_counter + 1
                patches = etree.SubElement(Surface ,'{' + gml + '}patches')
                PolygonPatch = etree.SubElement(patches ,'{' + gml + '}PolygonPatch')
                exterior = etree.SubElement(PolygonPatch ,'{' + gml + '}exterior')
                LinearRing = etree.SubElement(exterior ,'{' + gml + '}LinearRing')
                pos_list = geo["features"][0]["geometry"]["coordinates"][0]
                for geo_pos in pos_list:
                    # global po;s
                    pos = etree.SubElement(LinearRing ,'{' + gml + '}pos')
                    pos.text = str(geo_pos[0]) + " " + str(geo_pos[1])


        # add textplacement
        TextPlacement = etree.SubElement(members, '{' + S124 + '}TextPlacement')
        TextPlacement.set('{' + xmlns + '}S100',S100)
        TextPlacement.set('{' + gml + '}id' , id_o+"."+str(id_counter)) #add
        id_counter = id_counter + 1
        text = etree.SubElement(TextPlacement, '{' + S124 + '}text')
        text.text = "text"
        textJustification = etree.SubElement(TextPlacement, '{' + S124 + '}textJustification')
        textJustification.set('code' , "1") #add
        textJustification.text = "Centred"
        identifies = etree.SubElement(TextPlacement, '{' + S124 + '}identifies')
        geometry = etree.SubElement(TextPlacement, '{' + S124 + '}geometry')
        pointProperty = etree.SubElement(geometry ,'pointProperty')
        geometry.set("xmlns",xmlns)




        tree = etree.ElementTree(root)
        # tree.write("test3.xml", pretty_print=True,
        #            xml_declaration=True,   encoding="utf-8")
        # print(self.res_dict)
        return etree.tostring(tree,pretty_print=True)




if __name__ == "__main__":
    # ff = open("./nick_code/data/finish_tagging/finish_tag_navtex.txt" , "r")
    ff = open("./test_predict.txt" , "r")
    ff_list = ff.readlines()
    input_list = []
    for i  in ff_list:
        i = i.strip()
        if i == "":
            continue
        aa = i.split("\t")
        input_list.append(aa)


    # print(input_list)
    # data_obj = build_xml_data(input_list)
    # print(data_obj.geojson)