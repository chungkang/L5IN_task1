
# source file
dxf_name = "dxf\\HCU_D_106_Grundriss_4OG.dxf"

# set custom CRS
dxf_CRS = "+proj=tmerc +lat_0=0 +lon_0=9 +k=1 +x_0=3500000 +y_0=0 +ellps=GRS80 +towgs84=0,0,0,0,0,0,0 +units=m +no_defs"
target_CRS = "EPSG:32632"

min_point = 0.02 # minimum length as a point
wall_width = 0.41 # wall width

# interested layer list
layer_list = [
                "AUSBAU - Bezeichnung - Parkplatz"
                ,"AUSBAU - Darstellungen - Akustik"
                ,"AUSBAU - Darstellungen - Dämmung"
                ,"AUSBAU - Darstellungen - Dämmung-brennbar_B1"
                ,"AUSBAU - Darstellungen - Doppelbodenschottungen"
                ,"AUSBAU - Darstellungen - Fassade"
                ,"AUSBAU - Darstellungen - Fassade-Bemaßung"
                ,"AUSBAU - Darstellungen - Geländer"
                ,"AUSBAU - Darstellungen - Stahlbau"
                ,"AUSBAU - Darstellungen - Trennwände"
                ,"AUSBAU - Darstellungen - Trockenbau"
                ,"AUSBAU - Darstellungen - Trockenbau-2"
                ,"AUSBAU - Darstellungen - Wände"
                ,"AUSBAU - Darstellungen - Wände - Mauerwerk"
                ,"AUSBAU - Objekte - Aufzüge"
                ,"AUSBAU - Objekte - Türen"
                ,"AUßENANLAGEN - Darstellungen - Geländer"
                # ,"DARSTELLUNGEN - Bauteil - feuerbeständig"
                # ,"DARSTELLUNGEN - Brandwand"
                ,"Keine"
                ,"ROHBAU - Darstellungen - Brandwand"
                ,"ROHBAU - Darstellungen - Decken"
                # ,"ROHBAU - Darstellungen - Stützen"
                # ,"ROHBAU - Darstellungen - Unterzug - Deckenversprung - Öffnung"
                ,"ROHBAU - Darstellungen - Wände"
                ,"ROHBAU - Darstellungen - Wände - Mauerwerk"
                ,"wall"
]

door_layer_name = "AUSBAU - Objekte - Türen"

directory_path = 'geojson_output\\'
# directory_path_result = 'geojson_result\\28102022\\4detection_lines\\'
directory_path_result = 'geojson_output\\'