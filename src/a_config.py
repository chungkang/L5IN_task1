
# source file
# dxf_name = "modified_v1\\rev_HCU_D_102_Grundriss_1OG_moved.dxf"
# dxf_name = "modified_v1\\rev_HCU_D_104_Grundriss_2OG_moved.dxf"
# dxf_name = "modified_v1\\rev_HCU_D_105_Grundriss_3OG_moved.dxf"
# dxf_name = "modified_v1\\rev_HCU_D_106_Grundriss_4OG_moved_V2.dxf"

# dxf_name = "HCU_D_102_Grundriss_1OG_moved.dxf"
# dxf_name = "HCU_D_104_Grundriss_2OG_moved.dxf"
# dxf_name = "HCU_D_105_Grundriss_3OG_moved.dxf"
dxf_name = "HCU_D_106_Grundriss_4OG.dxf"

dxf_CRS = "+proj=tmerc +lat_0=0 +lon_0=9 +k=1 +x_0=3500000 +y_0=0 +ellps=GRS80 +towgs84=0,0,0,0,0,0,0 +units=m +no_defs"

min_point = 0.015 # minimum length as a point
wall_width = 0.41 # wall widthg

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
                ,"AUßENANLAGEN - Darstellungen - Treppen"
                # ,"DARSTELLUNGEN - Bauteil - feuerbeständig"
                ,"DARSTELLUNGEN - Brandwand"
                ,"Keine"
                ,"ROHBAU - Darstellungen - Brandwand"
                ,"ROHBAU - Darstellungen - Stützen"
                ,"ROHBAU - Darstellungen - Treppen"
                ,"ROHBAU - Darstellungen - Unterzug - Deckenversprung - Öffnung"
                ,"ROHBAU - Darstellungen - Wände"
                ,"ROHBAU - Darstellungen - Wände - Mauerwerk"
                ,"wall"
]

door_layer_name = "AUSBAU - Objekte - Türen"
stair_layer_name = "ROHBAU - Darstellungen - Treppen"

directory_path = 'geojson_output\\'
# directory_path_result = 'geojson_result\\28102022\\4detection_lines\\'
directory_path_result = 'geojson_output\\'