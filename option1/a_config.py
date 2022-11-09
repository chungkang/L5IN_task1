
# source file
# dxf_name = "rev_HCU_D_102_Grundriss_1OG_moved"
# dxf_name = "rev_HCU_D_104_Grundriss_2OG_moved"
# dxf_name = "rev_HCU_D_105_Grundriss_3OG_moved"
dxf_name = "rev_HCU_D_106_Grundriss_4OG_moved_V2"

min_length = 0.04 # minimum length of lines(ignore short lines)
min_point = 0.01 # minimum length as a point
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
                # ,"ROHBAU - Darstellungen - Treppen" 
                ,"ROHBAU - Darstellungen - Waende" 
                ,"ROHBAU - Darstellungen - Decken" 
                ,"ROHBAU - Darstellungen - Waende - Mauerwerk" 
                # ,"ROHBAU - Darstellungen - Ansichtslinien"
                ,"ROHBAU - Darstellungen - Unterzug - Deckenversprung - Oeffnung"
                ,"ROHBAU - Darstellungen - Stuetzen"
                ,"wall"
]

directory_path = 'option1_walls\\'
# directory_path_result = 'geojson_result\\28102022\\4detection_lines\\'
directory_path_result = 'option1_walls\\'