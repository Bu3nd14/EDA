from collections import defaultdict
from skidl import Pin, Part, Alias, SchLib, SKIDL, TEMPLATE

from skidl.pin import pin_types

SKIDL_lib_version = '0.0.1'

preamp_audio = SchLib(tool=SKIDL).add_parts(*[
        Part(**{ 'name':'G6K-2', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'G6K-2'}), 'ref_prefix':'K', 'fplist':[''], 'footprint':'Relay_SMD:Relay_DPDT_Omron_G6K-2F-Y', 'keywords':'Miniature Relay Dual Pole DPDT Omron', 'description':'Miniature 2-pole relay, Single-side Stable', 'datasheet':'http://omronfs.omron.com/en_US/ecb/products/pdf/en-g6k.pdf', 'pins':[
            Pin(num='1',func=pin_types.PASSIVE,unit=1),
            Pin(num='2',func=pin_types.PASSIVE,unit=1),
            Pin(num='3',func=pin_types.PASSIVE,unit=1),
            Pin(num='4',func=pin_types.PASSIVE,unit=1),
            Pin(num='5',func=pin_types.PASSIVE,unit=1),
            Pin(num='6',func=pin_types.PASSIVE,unit=1),
            Pin(num='7',func=pin_types.PASSIVE,unit=1),
            Pin(num='8',func=pin_types.PASSIVE,unit=1)], 'unit_defs':[] }),
        Part(**{ 'name':'D', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'D'}), 'ref_prefix':'D', 'fplist':[''], 'footprint':'Diode_THT:D_DO-35_SOD27_P7.62mm_Horizontal', 'keywords':'diode', 'description':'Diode', 'datasheet':'', 'pins':[
            Pin(num='1',name='K',func=pin_types.PASSIVE,unit=1),
            Pin(num='2',name='A',func=pin_types.PASSIVE,unit=1)], 'unit_defs':[] }),
        Part(**{ 'name':'G6KU-2', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'G6KU-2'}), 'ref_prefix':'K', 'fplist':[''], 'footprint':'Relay_SMD:Relay_DPDT_Omron_G6K-2F-Y', 'keywords':'Miniature Relay Dual Pole DPDT Omron', 'description':'Miniature 2-pole relay, Single-winding Latching', 'datasheet':'http://omronfs.omron.com/en_US/ecb/products/pdf/en-g6k.pdf', 'pins':[
            Pin(num='1',func=pin_types.PASSIVE,unit=1),
            Pin(num='2',func=pin_types.PASSIVE,unit=1),
            Pin(num='3',func=pin_types.PASSIVE,unit=1),
            Pin(num='4',func=pin_types.PASSIVE,unit=1),
            Pin(num='5',func=pin_types.PASSIVE,unit=1),
            Pin(num='6',func=pin_types.PASSIVE,unit=1),
            Pin(num='7',func=pin_types.PASSIVE,unit=1),
            Pin(num='8',func=pin_types.PASSIVE,unit=1)], 'unit_defs':[] }),
        Part(**{ 'name':'D_TVS', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'D_TVS'}), 'ref_prefix':'D', 'fplist':[''], 'footprint':'Diode_SMD:D_SMA', 'keywords':'diode TVS thyrector', 'description':'Bidirectional transient-voltage-suppression diode', 'datasheet':'', 'pins':[
            Pin(num='1',name='A1',func=pin_types.PASSIVE,unit=1),
            Pin(num='2',name='A2',func=pin_types.PASSIVE,unit=1)], 'unit_defs':[] }),
        Part(**{ 'name':'SW_Rotary_4x3', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'SW_Rotary_4x3'}), 'ref_prefix':'SW', 'fplist':[''], 'footprint':'Connector_PinHeader_2.54mm:PinHeader_2x08_P2.54mm_Vertical', 'keywords':'rotary switch 4x3', 'description':'4 rotary switches with 3 positions', 'datasheet':'http://cdn-reichelt.de/documents/datenblatt/C200/DS-Serie%23LOR.pdf', 'pins':[
            Pin(num='1',name='1',func=pin_types.PASSIVE,unit=1),
            Pin(num='2',name='2',func=pin_types.PASSIVE,unit=1),
            Pin(num='3',name='3',func=pin_types.PASSIVE,unit=1),
            Pin(num='4',name='4',func=pin_types.PASSIVE,unit=1),
            Pin(num='5',name='5',func=pin_types.PASSIVE,unit=1),
            Pin(num='6',name='6',func=pin_types.PASSIVE,unit=1),
            Pin(num='7',name='7',func=pin_types.PASSIVE,unit=1),
            Pin(num='8',name='8',func=pin_types.PASSIVE,unit=1),
            Pin(num='9',name='9',func=pin_types.PASSIVE,unit=1),
            Pin(num='10',name='10',func=pin_types.PASSIVE,unit=1),
            Pin(num='11',name='11',func=pin_types.PASSIVE,unit=1),
            Pin(num='12',name='12',func=pin_types.PASSIVE,unit=1),
            Pin(num='13',name='13',func=pin_types.PASSIVE,unit=1),
            Pin(num='14',name='14',func=pin_types.PASSIVE,unit=1),
            Pin(num='15',name='15',func=pin_types.PASSIVE,unit=1),
            Pin(num='16',name='16',func=pin_types.PASSIVE,unit=1)], 'unit_defs':[] }),
        Part(**{ 'name':'R', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'R'}), 'ref_prefix':'R', 'fplist':[''], 'footprint':'Resistor_THT:R_Axial_DIN0207_L6.3mm_D2.5mm_P10.16mm_Horizontal', 'keywords':'R res resistor', 'description':'Resistor', 'datasheet':'', 'pins':[
            Pin(num='1',func=pin_types.PASSIVE,unit=1),
            Pin(num='2',func=pin_types.PASSIVE,unit=1)], 'unit_defs':[] }),
        Part(**{ 'name':'LED', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'LED'}), 'ref_prefix':'D', 'fplist':[''], 'footprint':'LED_THT:LED_D3.0mm', 'keywords':'LED diode', 'description':'Light emitting diode', 'datasheet':'', 'pins':[
            Pin(num='1',name='K',func=pin_types.PASSIVE,unit=1),
            Pin(num='2',name='A',func=pin_types.PASSIVE,unit=1)], 'unit_defs':[] }),
        Part(**{ 'name':'Conn_01x01', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'Conn_01x01'}), 'ref_prefix':'J', 'fplist':[''], 'footprint':'Connector_PinHeader_2.54mm:PinHeader_1x01_P2.54mm_Vertical', 'keywords':'connector', 'description':'Generic connector, single row, 01x01, script generated (kicad-library-utils/schlib/autogen/connector/)', 'datasheet':'', 'pins':[
            Pin(num='1',name='Pin_1',func=pin_types.PASSIVE,unit=1)], 'unit_defs':[] }),
        Part(**{ 'name':'C', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'C'}), 'ref_prefix':'C', 'fplist':[''], 'footprint':'Capacitor_THT:CP_Radial_D8.0mm_P3.50mm', 'keywords':'cap capacitor', 'description':'Unpolarized capacitor', 'datasheet':'', 'pins':[
            Pin(num='1',func=pin_types.PASSIVE,unit=1),
            Pin(num='2',func=pin_types.PASSIVE,unit=1)], 'unit_defs':[] }),
        Part(**{ 'name':'Q_NPN', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'Q_NPN'}), 'ref_prefix':'Q', 'fplist':[''], 'footprint':'Package_TO_SOT_THT:TO-92_Inline', 'keywords':'BJT', 'description':'NPN bipolar junction transistor', 'datasheet':'', 'pins':[
            Pin(num='B',name='B',func=pin_types.INPUT,unit=1),
            Pin(num='C',name='C',func=pin_types.PASSIVE,unit=1),
            Pin(num='E',name='E',func=pin_types.PASSIVE,unit=1)], 'unit_defs':[] }),
        Part(**{ 'name':'LSK489', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'LSK489'}), 'ref_prefix':'Q', 'fplist':['Package_SO:SOIC-8_3.9x4.9mm_P1.27mm'], 'footprint':'Package_SO:SOIC-8_3.9x4.9mm_P1.27mm', 'keywords':'', 'description':'Monolithic dual N-JFET, low noise, 4 pF Ciss (LSK489A/B). Two units on one die, one SOIC-8 package. Pinout from LSK489 datasheet Rev A40 page 1, SOIC-A Top View.', 'datasheet':'https://www.linearsystems.com/jfet-amplifiers-duals/lsk489-series', 'pins':[
            Pin(num='2',name='D1',func=pin_types.PASSIVE,unit=1),
            Pin(num='4',name='G1',func=pin_types.INPUT,unit=1),
            Pin(num='1',name='S1',func=pin_types.PASSIVE,unit=1),
            Pin(num='6',name='D2',func=pin_types.PASSIVE,unit=2),
            Pin(num='8',name='G2',func=pin_types.INPUT,unit=2),
            Pin(num='5',name='S2',func=pin_types.PASSIVE,unit=2),
            Pin(num='3',name='SS',func=pin_types.PASSIVE,unit=3),
            Pin(num='7',name='SS',func=pin_types.PASSIVE,unit=3)], 'unit_defs':[{'label': 'uA', 'num': 1, 'pin_nums': ['2', '1', '4']},{'label': 'uB', 'num': 2, 'pin_nums': ['5', '8', '6']},{'label': 'uC', 'num': 3, 'pin_nums': ['7', '3']}] }),
        Part(**{ 'name':'LS352', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'LS352'}), 'ref_prefix':'Q', 'fplist':['Package_SO:SOIC-8_3.9x4.9mm_P1.27mm'], 'footprint':'Package_SO:SOIC-8_3.9x4.9mm_P1.27mm', 'keywords':'', 'description':'Monolithic dual PNP, tight VBE matching (LS350 series). Two units on one die, one package.', 'datasheet':'https://www.linearsystems.com/bipolartransistors/ls350-series', 'pins':[
            Pin(num='1',name='C1',func=pin_types.PASSIVE,unit=1),
            Pin(num='2',name='B1',func=pin_types.INPUT,unit=1),
            Pin(num='3',name='E1',func=pin_types.PASSIVE,unit=1),
            Pin(num='6',name='E2',func=pin_types.PASSIVE,unit=2),
            Pin(num='7',name='B2',func=pin_types.INPUT,unit=2),
            Pin(num='8',name='C2',func=pin_types.PASSIVE,unit=2),
            Pin(num='4',name='NC1',func=pin_types.NOCONNECT,unit=3),
            Pin(num='5',name='NC2',func=pin_types.NOCONNECT,unit=3)], 'unit_defs':[{'label': 'uA', 'num': 1, 'pin_nums': ['1', '3', '2']},{'label': 'uB', 'num': 2, 'pin_nums': ['8', '7', '6']},{'label': 'uC', 'num': 3, 'pin_nums': ['5', '4']}] }),
        Part(**{ 'name':'Q_PNP', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'Q_PNP'}), 'ref_prefix':'Q', 'fplist':[''], 'footprint':'Package_TO_SOT_THT:TO-92_Inline', 'keywords':'BJT', 'description':'PNP bipolar junction transistor', 'datasheet':'', 'pins':[
            Pin(num='B',name='B',func=pin_types.INPUT,unit=1),
            Pin(num='C',name='C',func=pin_types.PASSIVE,unit=1),
            Pin(num='E',name='E',func=pin_types.PASSIVE,unit=1)], 'unit_defs':[] }),
        Part(**{ 'name':'Conn_01x02', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'Conn_01x02'}), 'ref_prefix':'J', 'fplist':[''], 'footprint':'Connector_PinHeader_2.54mm:PinHeader_1x02_P2.54mm_Vertical', 'keywords':'connector', 'description':'Generic connector, single row, 01x02, script generated (kicad-library-utils/schlib/autogen/connector/)', 'datasheet':'', 'pins':[
            Pin(num='1',name='Pin_1',func=pin_types.PASSIVE,unit=1),
            Pin(num='2',name='Pin_2',func=pin_types.PASSIVE,unit=1)], 'unit_defs':[] }),
        Part(**{ 'name':'Conn_01x03', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'Conn_01x03'}), 'ref_prefix':'J', 'fplist':[''], 'footprint':'Connector_PinHeader_2.54mm:PinHeader_1x03_P2.54mm_Vertical', 'keywords':'connector', 'description':'Generic connector, single row, 01x03, script generated (kicad-library-utils/schlib/autogen/connector/)', 'datasheet':'', 'pins':[
            Pin(num='1',name='Pin_1',func=pin_types.PASSIVE,unit=1),
            Pin(num='2',name='Pin_2',func=pin_types.PASSIVE,unit=1),
            Pin(num='3',name='Pin_3',func=pin_types.PASSIVE,unit=1)], 'unit_defs':[] }),
        Part(**{ 'name':'Conn_01x04', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'Conn_01x04'}), 'ref_prefix':'J', 'fplist':[''], 'footprint':'Connector_PinHeader_2.54mm:PinHeader_1x04_P2.54mm_Vertical', 'keywords':'connector', 'description':'Generic connector, single row, 01x04, script generated (kicad-library-utils/schlib/autogen/connector/)', 'datasheet':'', 'pins':[
            Pin(num='1',name='Pin_1',func=pin_types.PASSIVE,unit=1),
            Pin(num='2',name='Pin_2',func=pin_types.PASSIVE,unit=1),
            Pin(num='3',name='Pin_3',func=pin_types.PASSIVE,unit=1),
            Pin(num='4',name='Pin_4',func=pin_types.PASSIVE,unit=1)], 'unit_defs':[] })])