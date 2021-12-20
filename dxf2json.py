import ezdxf
dxf = "./HCU_D_104_Grundriss_2OG_moved.dxf"

# loading dxf file
doc = ezdxf.readfile(dxf)

# get modelspace
msp = doc.modelspace()

# get lines of layer
lines = msp.query('LINE[layer=="AUSBAU - Darstellungen - Daemmung"]')

