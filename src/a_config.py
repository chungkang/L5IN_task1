
# source file
# dxf_name = "rev_HCU_D_102_Grundriss_1OG_moved"
# dxf_name = "rev_HCU_D_104_Grundriss_2OG_moved"
dxf_name = "rev_HCU_D_105_Grundriss_3OG_moved"
# dxf_name = "rev_HCU_D_106_Grundriss_4OG_moved_V2"

dxf_CRS = "+proj=tmerc +lat_0=0 +lon_0=9 +k=1 +x_0=3500000 +y_0=0 +ellps=GRS80 +towgs84=0,0,0,0,0,0,0 +units=m +no_defs"

min_point = 0.015 # minimum length as a point
wall_width = 0.41 # wall widthg

# interested layer list
layer_list = [
                "AUSBAU - Bezeichnung - Parkplatz" 
                ,"AUSBAU - Darstellungen - Akustik" 
                ,"AUSBAU - Darstellungen - Daemmung" 
                ,"AUSBAU - Darstellungen - Daemmung-brennbar_B1" 
                ,"AUSBAU - Darstellungen - Doppelbodenschottungen" 
                ,"AUSBAU - Darstellungen - Fassade"
                ,"AUSBAU - Darstellungen - Fassade-Bemassung"
                ,"AUSBAU - Darstellungen - Fassade-Bemaßung"
                ,"AUSBAU - Darstellungen - Gelaender" 
                ,"AUSBAU - Darstellungen - Stahlbau" 
                ,"AUSBAU - Darstellungen - Trennwaende"
                ,"AUSBAU - Darstellungen - Trockenbau" 
                ,"AUSBAU - Darstellungen - Waende - Mauerwerk"
                ,"AUSBAU - Darstellungen - Trennwaende"
                ,"AUSBAU - Darstellungen - Waende - Mauerwerk"
                # ,"AUSBAU - Objekte - Aufzuege"
                ,"AUSBAU - Objekte - Tueren"
                ,"DARSTELLUNGEN - Aufsichtslinien"
                ,"DARSTELLUNGEN - Brandwand"
                ,"DARSTELLUNGEN - Bauteil - feuerbestaendig"
                # ,"ROHBAU - Darstellungen - Unterzug - Deckenversprung - Oeffnung"
                ,"keine" 
                ,"ROHBAU - Darstellungen - Brandwand" 
                ,"ROHBAU - Darstellungen - Treppen" 
                ,"ROHBAU - Darstellungen - Waende" 
                ,"ROHBAU - Darstellungen - Decken" 
                ,"ROHBAU - Darstellungen - Waende - Mauerwerk" 
                # ,"ROHBAU - Darstellungen - Ansichtslinien"
                # ,"ROHBAU - Darstellungen - Unterzug - Deckenversprung - Oeffnung"
                ,"ROHBAU - Darstellungen - Stuetzen"
                ,"wall"
]

directory_path = 'geojson_output\\'
# directory_path_result = 'geojson_result\\28102022\\4detection_lines\\'
directory_path_result = 'geojson_output\\'