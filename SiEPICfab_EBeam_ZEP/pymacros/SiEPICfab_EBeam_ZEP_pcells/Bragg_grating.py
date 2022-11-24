# Waveguide Bragg grating
# imported from SiEPIC_EBeam_PDK.  Model does not exist. Layout only.

from . import *
import pya
from pya import *
import math
class Bragg_grating(pya.PCellDeclarationHelper):
  """
  Input: length, width
  """

  def __init__(self):

    # Important: initialize the super class
    super(Bragg_grating, self).__init__()
    from SiEPIC.utils import get_technology_by_name, load_Waveguides_by_Tech
    self.technology_name = 'SiEPICfab_EBeam_ZEP'
    TECHNOLOGY = get_technology_by_name(self.technology_name)
    self.TECHNOLOGY = TECHNOLOGY
            
    # Load all strip waveguides
    self.waveguide_types = load_Waveguides_by_Tech(self.technology_name)   
        
    # declare the parameters
    p = self.param("waveguide_type", self.TypeList, "Waveguide Type", default = 'Strip 1310 nm, w=350 nm (core-clad)' ) # self.waveguide_types[0]['name'])
    for wa in self.waveguide_types:
        p.add_choice(wa['name'],wa['name'])
    self.param("layer", self.TypeLayer, "Layer - Waveguide", default = TECHNOLOGY['Si_core'])

    # declare the parameters
    self.param("number_of_periods", self.TypeInt, "Number of grating periods", default = 300)     
    self.param("grating_period", self.TypeDouble, "Grating period (microns)", default = 0.317)     
    self.param("fill_factor", self.TypeDouble, "Grating fill factor", default = 0.5)     
    self.param("wg_width", self.TypeDouble, "Waveguide width", default = 0.5)     
    self.param("corrugation_width", self.TypeDouble, "Corrugration width (microns)", default = 0.05)     
    self.param("misalignment", self.TypeDouble, "Grating misalignment (microns)", default = 0.0)     
    self.param("sinusoidal", self.TypeBoolean, "Grating Type (Rectangular=False, Sinusoidal=True)", default = False)     
    self.param("pinrec", self.TypeLayer, "PinRec Layer", default = TECHNOLOGY['PinRec'])
    self.param("devrec", self.TypeLayer, "DevRec Layer", default = TECHNOLOGY['DevRec'])
#    self.param("textl", self.TypeLayer, "Text Layer", default = LayerInfo(10, 0))

  def display_text_impl(self):
    # Provide a descriptive text for the cell
    return "Bragg_grating_%s-%.3f-%.3f-%.3f" % \
    (self.number_of_periods, self.grating_period, self.corrugation_width, self.misalignment)
  
  def coerce_parameters_impl(self):
    pass

  def can_create_from_shape(self, layout, shape, layer):
    return False
    
  def produce_impl(self):
  
    # fetch the parameters
    dbu = self.layout.dbu
    ly = self.layout
    shapes = self.cell.shapes

    LayerSi = self.layer
    LayerSiN = ly.layer(LayerSi)
    LayerPinRecN = ly.layer(self.pinrec)
    LayerDevRecN = ly.layer(self.devrec)

    from SiEPIC.extend import to_itype

    
    # Draw the Bragg grating:
    box_width = to_itype(self.grating_period/2,dbu)
    grating_period = to_itype(self.grating_period,dbu)
    w = to_itype(self.wg_width,dbu)
    half_w = w/2
    half_corrugation_w = to_itype(self.corrugation_width/2,dbu)
    misalignment = to_itype(self.misalignment,dbu)
    
    if self.sinusoidal:
      npoints_sin = 40
      for i in range(0,self.number_of_periods):
        x = i * to_itype(self.grating_period,dbu)
        box1 = Box(x, 0, x + box_width, half_w+half_corrugation_w)
        pts1 = [Point(x,0)]
        pts3 = [Point(x + misalignment,0)]
        for i1 in range(0,npoints_sin+1):
          x1 = i1 * 2* math.pi / npoints_sin
          y1 = half_corrugation_w*math.sin(x1)
          x1 = x1/2/math.pi*grating_period
#          print("x: %s, y: %s" % (x1,y1))
          pts1.append( Point(x + x1,half_w+y1 ) )
          pts3.append( Point(x + misalignment + x1,-half_w-y1 ) )
        pts1.append( Point(x + grating_period, 0) )
        pts3.append( Point(x + grating_period + misalignment, 0) )
        shapes(LayerSiN).insert(Polygon(pts1))
        shapes(LayerSiN).insert(Polygon(pts3))
      length = x + grating_period + misalignment
      if misalignment > 0:
        # extra piece at the end:
        box2 = Box(x + grating_period, 0, length, half_w)
        shapes(LayerSiN).insert(box2)
        # extra piece at the beginning:
        box3 = Box(0, 0, misalignment, -half_w)
        shapes(LayerSiN).insert(box3)

    else:
      for i in range(0,self.number_of_periods):
        x = i * to_itype(self.grating_period,dbu)
        box1 = Box(x, 0, x + box_width, half_w+half_corrugation_w)
        box2 = Box(x + box_width, 0, x + grating_period, half_w-half_corrugation_w)
        box3 = Box(x + misalignment, 0, x + box_width + misalignment, -half_w-half_corrugation_w)
        box4 = Box(x + box_width + misalignment, 0, x + grating_period + misalignment, -half_w+half_corrugation_w)
        shapes(LayerSiN).insert(box1)
        shapes(LayerSiN).insert(box2)
        shapes(LayerSiN).insert(box3)
        shapes(LayerSiN).insert(box4)
      length = x + grating_period + misalignment
      if misalignment > 0:
        # extra piece at the end:
        box2 = Box(x + grating_period, 0, length, half_w)
        shapes(LayerSiN).insert(box2)
        # extra piece at the beginning:
        box3 = Box(0, 0, misalignment, -half_w)
        shapes(LayerSiN).insert(box3)

    
    # Create the pins on the waveguides, as short paths:
    from SiEPIC._globals import PIN_LENGTH as pin_length

    t = Trans(Trans.R0, 0,0)
    pin = Path([Point(pin_length/2, 0), Point(-pin_length/2, 0)], w)
    pin_t = pin.transformed(t)
    shapes(LayerPinRecN).insert(pin_t)
    text = Text ("opt1", t)
    shape = shapes(LayerPinRecN).insert(text)
    shape.text_size = 0.4/dbu

    t = Trans(Trans.R0, length,0)
    pin = Path([Point(-pin_length/2, 0), Point(pin_length/2, 0)], w)
    pin_t = pin.transformed(t)
    shapes(LayerPinRecN).insert(pin_t)
    text = Text ("opt2", t)
    shape = shapes(LayerPinRecN).insert(text)
    shape.text_size = 0.4/dbu
    shape.text_halign = 2

    # Compact model information
    t = Trans(Trans.R0, 0, 0)
    text = Text ('Lumerical_INTERCONNECT_library=Custom', t)
    shape = shapes(LayerDevRecN).insert(text)
    shape.text_size = 0.1/dbu
    t = Trans(Trans.R0, length/10, 0)
    text = Text ('Component=Bragg_waveguide_grating', t)
    shape = shapes(LayerDevRecN).insert(text)
    shape.text_size = 0.1/dbu
    t = Trans(Trans.R0, length/9, 0)
    text = Text \
      ('Spice_param:number_of_periods=%s grating_period=%.3g corrugation_width=%.3g misalignment=%.3g sinusoidal=%s' %\
      (self.number_of_periods, self.grating_period*1e-6, self.corrugation_width*1e-6, self.misalignment*1e-6, int(self.sinusoidal)), t )
    shape = shapes(LayerDevRecN).insert(text)
    shape.text_size = 0.1/dbu


    # Load the technology and all waveguide types
    from SiEPIC.utils import load_Waveguides_by_Tech
    technology_name = self.technology_name
    waveguide_types = load_Waveguides_by_Tech(technology_name)

    # Load parameters for the chosen waveguide type
    params = [t for t in waveguide_types if t['name'] == self.waveguide_type]
    if type(params) == type([]) and len(params) > 0:
        params = params[0]
        if 'width' not in params and 'compound_waveguide' not in params:
            params['width'] = params['wg_width']
    else:
        print('error: waveguide type not found in PDK waveguides')
        raise Exception('error: waveguide type (%s) not found in PDK waveguides' %
                        waveguide_type)
    # compound waveguide types:
    if 'compound_waveguide' in params:
        raise Exception('Cannot use compound waveguide type for the Bragg grating cell')

    # find all the non-waveguide core layers (DevRec, Cladding)
    for wg in params['component']:
        if self.layer != self.TECHNOLOGY[wg['layer']]:
            t = Trans(Trans.R0, 0,0)
            path = Path([Point(0, 0), Point(length, 0)], to_itype(wg['width'],dbu))
            shapes(ly.layer(self.TECHNOLOGY[wg['layer']])).insert(path.simple_polygon())
#[wg['offset'] for wg in params['component']], 

    # Create the device recognition layer -- make it 1 * wg_width away from the waveguides.


    print('Done: Bragg_waveguide_grating')