
from ntpath import join
import re
from numpy import empty
import json
from datetime import datetime,timedelta
from osgeo import ogr,osr
import math,ast





class Tool():
    def TWD97_trans(trans_line ,coor,warp):
        from osgeo import _osr
        trans_line = trans_line.strip()
        tmp = trans_line.split()
        x = float(tmp[0])
        y = float(tmp[1])
        if warp == "1":
            x1 = x
            x = y 
            y = x1
        if coor == "twd97_121":
            twd87_str = 'PROJCS["TWD97 / TM2 zone 121",GEOGCS["TWD97",DATUM["Taiwan_Datum_1997",SPHEROID["GRS 1980",6378137,298.257222101,AUTHORITY["EPSG","7019"]],TOWGS84[0,0,0,0,0,0,0],AUTHORITY["EPSG","1026"]],PRIMEM["Greenwich",0,AUTHORITY["EPSG","8901"]],UNIT["degree",0.0174532925199433,AUTHORITY["EPSG","9122"]],AUTHORITY["EPSG","3824"]],PROJECTION["Transverse_Mercator"],PARAMETER["latitude_of_origin",0],PARAMETER["central_meridian",121],PARAMETER["scale_factor",0.9999],PARAMETER["false_easting",250000],PARAMETER["false_northing",0],UNIT["metre",1,AUTHORITY["EPSG","9001"]],AXIS["X",EAST],AXIS["Y",NORTH],AUTHORITY["EPSG","3826"]]'
        if coor == "twd97_119":
            twd87_str = 'PROJCS["TWD97 / TM2 zone 119",GEOGCS["TWD97",DATUM["Taiwan_Datum_1997",SPHEROID["GRS 1980",6378137,298.257222101,AUTHORITY["EPSG","7019"]],TOWGS84[0,0,0,0,0,0,0],AUTHORITY["EPSG","1026"]],PRIMEM["Greenwich",0,AUTHORITY["EPSG","8901"]],UNIT["degree",0.0174532925199433,AUTHORITY["EPSG","9122"]],AUTHORITY["EPSG","3824"]],PROJECTION["Transverse_Mercator"],PARAMETER["latitude_of_origin",0],PARAMETER["central_meridian",119],PARAMETER["scale_factor",0.9999],PARAMETER["false_easting",250000],PARAMETER["false_northing",0],UNIT["metre",1,AUTHORITY["EPSG","9001"]],AXIS["X",EAST],AXIS["Y",NORTH],AUTHORITY["EPSG","3825"]]'
        spatialref_source=osr.SpatialReference()
        spatialref_source.ImportFromWkt(twd87_str)
        spatialref_target=osr.SpatialReference()
        spatialref_target.ImportFromEPSG(4326)

        trans=osr.CoordinateTransformation(spatialref_source,spatialref_target)
        coordinate_after_trans=trans.TransformPoint(x,y)

        return coordinate_after_trans[0] ,coordinate_after_trans[1]


    def strQ2B(ustring):
        # """把字串全形轉半形"""
        ss = []
        for s in ustring:
            rstring = ""
            for uchar in s:
                inside_code = ord(uchar)
                if inside_code == 12288:  # 全形空格直接轉換
                    inside_code = 32
                elif (inside_code >= 65281 and inside_code <= 65374):  # 全形字元（除空格）根據關係轉化
                    inside_code -= 65248
                rstring += chr(inside_code)
            ss.append(rstring)
        return ''.join(ss)
    def d2dd(value_list):
        value = value_list[0]
        value = float(value.replace("1234321","."))
        xs,zs=math.modf(value)
        print(xs)
        print(zs)

        
        deg = value // 1
        m = str(round(xs * 60,4))
        print(type(zs))
        print(zs)
        result = ''
        return result

    def d2dm(string):
        
        value = float(string)
        xs,zs=math.modf(value)
        # print(xs)
        # print(zs)

        
        deg = value // 1
        m = str(round(xs * 60,4))
        # print(type(zs))
        # print(zs)
        zs = str(int(zs))
        result = zs+"°"+m+"'"
        return result

    def dms2dd(value_list):
        # print(value_list)
        for i in range(len(value_list)):
            if "1234321" in value_list[i]:
                value_list[i] = value_list[i].replace("1234321",".")
        # print(value_list)
        dd = float(value_list[0]) + float(value_list[1])/60 + float(value_list[2])/(60*60)
        if value_list[3] == "S" or value_list[3] == "W":
            dd = -1 * dd
        return str(dd) 
    def dm2dd(value_list):
        # print(value_list)
        for i in range(len(value_list)):
            # print(i)
            if "1234321" in value_list[i]:
                value_list[i] = value_list[i].replace("1234321",".")
        # print(value_list)
        dd = float(value_list[0]) + float(value_list[1])/60
        if value_list[2] == "S" or value_list[2] == "W":
            dd = -1 * dd
        return str(dd)
        
    def dmstodd(text):
        textlist = text.split('-')
        # print(textlist)
        try:
            decNum = float(textlist[0]) + float(textlist[1])/60.0 + float(textlist[2])/3600.0
        except:
            decNum = "NaN"
        return(decNum)
    
    def dmstodd2(text):
        textlist = text.split('-')
        try:
            decNum = float(textlist[0]) + float(textlist[1])/60.0
        except:
            decNum = "NaN"
        return(decNum)

    def do_buffer(geom, mid_line, rad , unit):
        if unit =="M":
            rad = rad * 1
        if unit =="KM":
            rad = rad * 1000
        if unit =="NM":
            rad = rad * 1852
        proj = "+proj=tmerc +lat_0=0 +lon_0=121 +k=0.9999 +x_0=250000 +y_0=0 +ellps=GRS80 +towgs84=0,0,0,0,0,0,0 +units=m +no_defs "
        wgs84 ='PROJCS["WGS84_Simple_Mercator",GEOGCS["GCS_WGS_1984",DATUM["D_WGS_1984",SPHEROID["WGS_1984",6378137,298.257223563]],PRIMEM["Greenwich",0],UNIT["Degree",0.017453292519943295]],PROJECTION["Mercator"],PARAMETER["standard_parallel_1",0],PARAMETER["central_meridian",0],PARAMETER["false_easting",0],PARAMETER["false_northing",0],UNIT["Meter",1]]'
        wktstr = 'PROJCS["TWD97 / TM2 zone 121",GEOGCS["TWD97",DATUM["Taiwan_Datum_1997",SPHEROID["GRS 1980",6378137,298.257222101,AUTHORITY["EPSG","7019"]],TOWGS84[0,0,0,0,0,0,0],AUTHORITY["EPSG","1026"]],PRIMEM["Greenwich",0,AUTHORITY["EPSG","8901"]],UNIT["degree",0.0174532925199433,AUTHORITY["EPSG","9122"]],AUTHORITY["EPSG","3824"]],PROJECTION["Transverse_Mercator"],PARAMETER["latitude_of_origin",0],PARAMETER["central_meridian",{}],PARAMETER["scale_factor",0.9999],PARAMETER["false_easting",250000],PARAMETER["false_northing",0],UNIT["metre",1,AUTHORITY["EPSG","9001"]],AXIS["X",EAST],AXIS["Y",NORTH],AUTHORITY["EPSG","3826"]]'.format(mid_line)
        wktstr = 'PROJCS["TWD97 / TM2 zone 121",GEOGCS["TWD97",DATUM["Taiwan_Datum_1997",SPHEROID["GRS 1980",6378137,298.257222101,AUTHORITY["EPSG","7019"]],TOWGS84[0,0,0,0,0,0,0],AUTHORITY["EPSG","1026"]],PRIMEM["Greenwich",0,AUTHORITY["EPSG","8901"]],UNIT["degree",0.0174532925199433,AUTHORITY["EPSG","9122"]],AUTHORITY["EPSG","3824"]],PROJECTION["Transverse_Mercator"],PARAMETER["latitude_of_origin",0],PARAMETER["central_meridian",121],PARAMETER["scale_factor",0.9999],PARAMETER["false_easting",250000],PARAMETER["false_northing",0],UNIT["metre",1,AUTHORITY["EPSG","9001"]],AXIS["X",EAST],AXIS["Y",NORTH],AUTHORITY["EPSG","3826"]]'
        wgs84_ref = osr.SpatialReference()
        wgs84_ref.ImportFromEPSG(4326)
        # wgs84_ref.ImportFromWkt(wgs84)
        custom_ref = osr.SpatialReference()
        # custom_ref.ImportFromProj4(proj)
        custom_ref.ImportFromWkt(wktstr)
        # custom_ref.ImportFromEPSG(3824)
        wgs84trans = osr.CoordinateTransformation(wgs84_ref, custom_ref)
        trans2wgs84 = osr.CoordinateTransformation(custom_ref, wgs84_ref)

        geom.Transform(wgs84trans)
        geom = geom.Buffer(rad, quadsecs=4)
        geom.Transform(trans2wgs84)
        print(geom)
        return geom

    def count2id(counter):
        word_list = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
        word = ""
        if counter <= 25:
            word = word_list[counter]
        if counter > 25:
            i = counter // 26 -1
            j = counter % 26
            # print("===============")
            # print(i)
            # print(j)
            word = word_list[i] + word_list[j]
        return word

    def rastor_cal(lon,lat, distance,arc_start):
        print("arc_start:")
        print(arc_start)
        R = 6371000
        d = distance
        fin1 = float(lat) *math.pi/180
        lamda1 = float(lon) *math.pi/180
        # arc_start = float(arc_start) %360
        brng = arc_start *math.pi/180
        # print(brng)
        fin2 = math.asin( math.sin(fin1)*math.cos(d/R) + math.cos(fin1)*math.sin(d/R)*math.cos(brng) )
        lamda2 = lamda1 + math.atan2(math.sin(brng)*math.sin(d/R)*math.cos(fin1),math.cos(d/R)-math.sin(fin1)*math.sin(fin2))
        return [lamda2 * 180 / math.pi,fin2* 180 / math.pi]



    
    def parse2json(one_list):
        if  isinstance(one_list, dict):
            one_list = one_list
            
        else:
            one_list = json.loads(one_list)
        # print(one_list)
        # print(type(one_list))
        geostr = one_list["content"]
        geotype = one_list["type"]
        # result, pos_dict = Tool.one_parser(geostr,geotype)
        wkt = ""
        print(one_list)
        print(geostr)
        try:
            pos_dict = process.parse_geostr(geostr)
        except Exception as e:
            print(e)
            pos_dict = {}

        if geotype == "polygon":
            ring = ogr.Geometry(ogr.wkbLinearRing)
            for i in range(len(pos_dict["pos_N"])):
                # ring.AddPoint(float(pos_dict["pos_N"][i]) , float(pos_dict["pos_E"][i]))
                ring.AddPoint(float(pos_dict["pos_E"][i]) , float(pos_dict["pos_N"][i]))
            poly = ogr.Geometry(ogr.wkbPolygon)
            poly.AddGeometry(ring)
            # print(poly)
            wkt = poly
            geojson = poly.ExportToJson()
            result = {"type": "FeatureCollection","name": "test.geojson"}
            result.update({"features": [{"type": "Feature", "properties": {'name': 'EPSG:4326'}, "geometry":json.loads(geojson)}]})
        
        if geotype == "multipoint":
            multipoint = ogr.Geometry(ogr.wkbMultiPoint)
            # ring = ogr.Geometry(ogr.wkbLinearRing)
            for i in range(len(pos_dict["pos_N"])):
                # ring.AddPoint(float(pos_dict["pos_N"][i]) , float(pos_dict["pos_E"][i]))
                point1 = ogr.Geometry(ogr.wkbPoint)
                point1.AddPoint(float(pos_dict["pos_E"][i]) , float(pos_dict["pos_N"][i]))
                multipoint.AddGeometry(point1)
                # ring.AddPoint(float(pos_dict["pos_E"][i]) , float(pos_dict["pos_N"][i]))
            # poly = ogr.Geometry(ogr.wkbPolygon)
            # poly.AddGeometry(ring)
            # print(poly)
            wkt = multipoint
            geojson = multipoint.ExportToJson()
            result = {"type": "FeatureCollection","name": "test.geojson"}
            result.update({"features": [{"type": "Feature", "properties": {'name': 'EPSG:4326'}, "geometry":json.loads(geojson)}]})
            
        if geotype == "linstring":
            line = ogr.Geometry(ogr.wkbLineString)
            for i in range(len(pos_dict["pos_N"])):
                line.AddPoint(float(pos_dict["pos_E"][i]) , float(pos_dict["pos_N"][i]))
            # linee = ogr.Geometry(ogr.wkbPolygon)
            # linee.AddGeometry(line)
            wkt = line
            geojson = line.ExportToJson()
            result = {"type": "FeatureCollection","name": "test.geojson"}
            result.update({"features": [{"type": "Feature", "properties": {'name': 'EPSG:4326'}, "geometry":json.loads(geojson)}]})


        if geotype == "circle":
            print("---------------")
            print("---------------=====================================")
            print(geostr)
            # geo_dict = json.loads(geostr)
            # geo_dict = eval(geostr)
            if  isinstance(geostr, dict):
                center = geostr["center"]
                length = geostr["rad"]
                unit = geostr["unit"]
            
            else:
                
                geostr = geostr[1:-1]
                tmp_geo = geostr.split(",")
                # geo_dict = ast.literal_eval(geostr)
                center = tmp_geo[0]
                length = tmp_geo[1]
                unit = tmp_geo[2]
            print("in tmp geo")
            print(center)
            print(length)
            print(unit)
            # print(geo_dict)
            pos_dict = process.parse_geostr(center)
            point = ogr.Geometry(ogr.wkbPoint)
            # point.AddPoint(float(pos_dict["pos_E"][0]) , float(pos_dict["pos_N"][0]))
            point.AddPoint(float(pos_dict["pos_N"][0]) , float(pos_dict["pos_E"][0]))
            mid_lon = 0.0
            for l in pos_dict["pos_E"]:
                mid_lon += float(l)
            mid_lon = round(float(mid_lon)/len(pos_dict["pos_E"]))

            circle = Tool.do_buffer(point ,mid_lon  , float(length) , unit)
            circle2 = Tool.change_geo_type(circle)
            wkt = circle
            geojson = circle.ExportToJson()
            geojson = circle2.ExportToJson()
            print(geojson)

            result = {"type": "FeatureCollection","name": "test.geojson"}
            result.update({"features": [{"type": "Feature", "properties": {'name': 'EPSG:4326'}, "geometry":json.loads(geojson)}]})

        if geotype == "point":
            # print(pos_dict)
            point = ogr.Geometry(ogr.wkbPoint)
            point.AddPoint(float(pos_dict["pos_E"][0]) , float(pos_dict["pos_N"][0]))
            wkt = point
            geojson = point.ExportToJson()
            result = {"type": "FeatureCollection","name": "test.geojson"}
            result.update({"features": [{"type": "Feature", "properties": {'name': 'EPSG:4326'}, "geometry":json.loads(geojson)}]})

        if geotype == "sector":
            print("in geo str")
            print(geostr)
            print(type(geostr))

            # geo_dict = json.loads(geostr)
            # print(geo_dict)

            if  isinstance(geostr, dict):
                center = geostr["center"]
                rad = geostr["rad"]
                unit = geostr["unit"]
                start_arc = geostr["start_arc"]
                end_arc = geostr["end_arc"]
            
            else:
                
                # geostr = geostr[1:-1]
                # tmp_geo = geostr.split(",")
                # # geo_dict = ast.literal_eval(geostr)
                # center = tmp_geo[0]
                # length = tmp_geo[1]
                # unit = tmp_geo[2]
                geostr = geostr[1:-1]
                tmp_geo = geostr.split(",")
                center = tmp_geo[0]
                rad = tmp_geo[1]
                unit = tmp_geo[2]
                start_arc = tmp_geo[3]
                end_arc = tmp_geo[4]

            pos_dict = process.parse_geostr(center)
            # print(pos_dict)
            arc_start = float(start_arc)%360
            arc_end = float(end_arc)%360
            # unit = geo_dict["unit"]
            rad = float(rad)
            if unit =="M":
                rad = rad * 1
            if unit =="KM":
                rad = rad * 1000
            if unit =="NM":
                rad = rad * 1852
            interval = (arc_end - arc_start)/8
            pos_list = []
            for i in range(8 + 1):
                # print(interval) 
                arc = arc_start + interval *i
                return_pos = Tool.rastor_cal(pos_dict["pos_E"][0],pos_dict["pos_N"][0], rad,arc)
                pos_list.append(return_pos)
                # print(arc_start + interval *i)
            pos_list.append([pos_dict["pos_E"][0],pos_dict["pos_N"][0]])
            result = {"type": "FeatureCollection","name": "test.geojson"}
            result.update({"features": [{"type": "Feature", "properties": {}, "geometry":{"type": "Polygon","coordinates": [pos_list]}}]})


        # print(result)
        # print(pos_dict)
        # print("+++++++++  end parse2json  +++++++++++++")


        return result , pos_dict,wkt
        
    def get_affect(wkt):
        with open("./static/resource/encub.json","r") as f:
            json_str = f.readlines()[0]
        enc = ast.literal_eval(json_str)
        # print("get_affect ----------------------------->")
        # print(wkt)
        affect_list = []
        for key in enc:
            wkt1 = enc[key]
            poly1 = ogr.CreateGeometryFromWkt(wkt1)
            # poly2 = ogr.CreateGeometryFromWkt(wkt)
            intersection = str(poly1.Intersection(wkt))

            tmps = poly1.Intersects(wkt)
            # print(tmps)
            # print(type(poly1))
            # print(type(wkt))
            # print(intersection)
            # print(intersection)
            if "EMPTY" not in intersection and intersection is not None:
                affect_list.append(key)
            
            # print(val)
        # print(type(json_str))
        # print(json_str)
        print(affect_list)
        return affect_list

    def change_geo_type(circle):
        # print("=====================================================")
        # print(" change_geo_type ")
        circle = circle.ExportToWkt()
        # print(circle)
        tmp_cir = str(circle)[10:-2]
        tmp_cir = tmp_cir.split(",")
        ring = ogr.Geometry(ogr.wkbLinearRing)
        for i in tmp_cir:
            aa = i.split()
            tmp_NN = float(aa[0])
            tmp_EE = float(aa[1])
            ring.AddPoint(tmp_EE ,tmp_NN)
        poly = ogr.Geometry(ogr.wkbPolygon)
        poly.AddGeometry(ring)
        # print(poly)
        return poly
        
        # print(geom_poly)
        # print(type(geom_poly))


    