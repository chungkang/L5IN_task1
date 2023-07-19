
# source file
directory_path = 'geojson_output\\'
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
                ,"Keine"
                ,"ROHBAU - Darstellungen - Brandwand"
                ,"ROHBAU - Darstellungen - Decken"
                ,"ROHBAU - Darstellungen - Wände"
                ,"ROHBAU - Darstellungen - Wände - Mauerwerk"
                ,"wall"
]

door_layer = "AUSBAU - Objekte - Türen"