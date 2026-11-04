from collections import defaultdict
from skidl import Pin, Part, Alias, SchLib, SKIDL, TEMPLATE

from skidl.pin import pin_types

SKIDL_lib_version = '0.0.1'

psu_s1 = SchLib(tool=SKIDL).add_parts(*[
        Part(**{ 'name':'Conn_01x02', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'Conn_01x02'}), 'ref_prefix':'J', 'fplist':[''], 'footprint':'TerminalBlock_Phoenix:TerminalBlock_Phoenix_MKDS-1,5-2-5.08_1x02_P5.08mm_Horizontal', 'keywords':'connector', 'description':'Generic connector, single row, 01x02, script generated (kicad-library-utils/schlib/autogen/connector/)', 'datasheet':'', 'pins':[
            Pin(num='1',name='Pin_1',func=pin_types.PASSIVE,unit=1),
            Pin(num='2',name='Pin_2',func=pin_types.PASSIVE,unit=1)], 'unit_defs':[] }),
        Part(**{ 'name':'Fuse', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'Fuse'}), 'ref_prefix':'F', 'fplist':[''], 'footprint':'Fuse:Fuseholder_Cylinder-5x20mm_Schurter_0031_8201_Horizontal_Open', 'keywords':'fuse', 'description':'Fuse', 'datasheet':'', 'pins':[
            Pin(num='1',func=pin_types.PASSIVE,unit=1),
            Pin(num='2',func=pin_types.PASSIVE,unit=1)], 'unit_defs':[] }),
        Part(**{ 'name':'G2RL-2A', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'G2RL-2A'}), 'ref_prefix':'K', 'fplist':['', 'Relay_THT:Relay_DPST_Omron_G2RL-2A'], 'footprint':'Relay_THT:Relay_DPST_Omron_G2RL-2A', 'keywords':'Dual Pole Relay Omron DPST NO', 'description':'General Purpose Low Profile Relay DPST Through Hole, Omron G2RL series, Normally Open,  8A 250VAC', 'datasheet':'https://omronfs.omron.com/en_US/ecb/products/pdf/en-g2rl.pdf', 'pins':[
            Pin(num='13',func=pin_types.PASSIVE,unit=1),
            Pin(num='14',func=pin_types.PASSIVE,unit=1),
            Pin(num='23',func=pin_types.PASSIVE,unit=1),
            Pin(num='24',func=pin_types.PASSIVE,unit=1),
            Pin(num='A1',func=pin_types.PASSIVE,unit=1),
            Pin(num='A2',func=pin_types.PASSIVE,unit=1)], 'unit_defs':[] }),
        Part(**{ 'name':'D', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'D'}), 'ref_prefix':'D', 'fplist':[''], 'footprint':'Diode_THT:D_DO-35_SOD27_P7.62mm_Horizontal', 'keywords':'diode', 'description':'Diode', 'datasheet':'', 'pins':[
            Pin(num='1',name='K',func=pin_types.PASSIVE,unit=1),
            Pin(num='2',name='A',func=pin_types.PASSIVE,unit=1)], 'unit_defs':[] }),
        Part(**{ 'name':'R', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'R'}), 'ref_prefix':'R', 'fplist':[''], 'footprint':'Resistor_THT:R_Axial_DIN0414_L11.9mm_D4.5mm_P15.24mm_Horizontal', 'keywords':'R res resistor', 'description':'Resistor', 'datasheet':'', 'pins':[
            Pin(num='1',func=pin_types.PASSIVE,unit=1),
            Pin(num='2',func=pin_types.PASSIVE,unit=1)], 'unit_defs':[] }),
        Part(**{ 'name':'2N7002', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'2N7002'}), 'ref_prefix':'Q', 'fplist':['', 'Package_TO_SOT_SMD:SOT-23'], 'footprint':'Package_TO_SOT_SMD:SOT-23', 'keywords':'N-Channel Switching MOSFET', 'description':'0.115A Id, 60V Vds, N-Channel MOSFET, SOT-23', 'datasheet':'https://www.onsemi.com/pub/Collateral/NDS7002A-D.PDF', 'pins':[
            Pin(num='1',name='G',func=pin_types.INPUT,unit=1),
            Pin(num='2',name='S',func=pin_types.PASSIVE,unit=1),
            Pin(num='3',name='D',func=pin_types.PASSIVE,unit=1)], 'unit_defs':[] }),
        Part(**{ 'name':'Conn_01x03', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'Conn_01x03'}), 'ref_prefix':'J', 'fplist':[''], 'footprint':'TerminalBlock_Phoenix:TerminalBlock_Phoenix_MKDS-1,5-3-5.08_1x03_P5.08mm_Horizontal', 'keywords':'connector', 'description':'Generic connector, single row, 01x03, script generated (kicad-library-utils/schlib/autogen/connector/)', 'datasheet':'', 'pins':[
            Pin(num='1',name='Pin_1',func=pin_types.PASSIVE,unit=1),
            Pin(num='2',name='Pin_2',func=pin_types.PASSIVE,unit=1),
            Pin(num='3',name='Pin_3',func=pin_types.PASSIVE,unit=1)], 'unit_defs':[] }),
        Part(**{ 'name':'D_Bridge_+AA-', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'D_Bridge_+AA-'}), 'ref_prefix':'D', 'fplist':[''], 'footprint':'Diode_THT:Diode_Bridge_Vishay_KBL', 'keywords':'rectifier ACDC', 'description':'Diode bridge, +ve/AC/AC/-ve', 'datasheet':'', 'pins':[
            Pin(num='1',name='+',func=pin_types.PASSIVE,unit=1),
            Pin(num='2',func=pin_types.PASSIVE,unit=1),
            Pin(num='3',func=pin_types.PASSIVE,unit=1),
            Pin(num='4',name='-',func=pin_types.PASSIVE,unit=1)], 'unit_defs':[] }),
        Part(**{ 'name':'C_Polarized', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'C_Polarized'}), 'ref_prefix':'C', 'fplist':[''], 'footprint':'Capacitor_THT:CP_Radial_D16.0mm_P7.50mm', 'keywords':'cap capacitor', 'description':'Polarized capacitor', 'datasheet':'', 'pins':[
            Pin(num='1',func=pin_types.PASSIVE,unit=1),
            Pin(num='2',func=pin_types.PASSIVE,unit=1)], 'unit_defs':[] }),
        Part(**{ 'name':'TPS7A4701xRGW', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'TPS7A4701xRGW'}), 'ref_prefix':'U', 'fplist':['Package_DFN_QFN:Texas_RGW0020A_VQFN-20-1EP_5x5mm_P0.65mm_EP3.15x3.15mm_ThermalVias'], 'footprint':'Package_DFN_QFN:Texas_RGW0020A_VQFN-20-1EP_5x5mm_P0.65mm_EP3.15x3.15mm_ThermalVias', 'keywords':'linear regulator ldo voltage noise', 'description':'1A, Low-Noise Low-Dropout Voltage Regulator, 3-35V Input, Adjustable 1.4-34V Output, VQFN-20', 'datasheet':'https://www.ti.com/lit/ds/symlink/tps7a47.pdf', 'pins':[
            Pin(num='1',name='OUT',func=pin_types.PWROUT,unit=1),
            Pin(num='3',name='SENSE/FB',func=pin_types.INPUT,unit=1),
            Pin(num='4',name='6.4V',func=pin_types.INPUT,unit=1),
            Pin(num='5',name='6.4V',func=pin_types.INPUT,unit=1),
            Pin(num='6',name='3.2V',func=pin_types.INPUT,unit=1),
            Pin(num='7',name='GND',func=pin_types.PWRIN,unit=1),
            Pin(num='8',name='1.6V',func=pin_types.INPUT,unit=1),
            Pin(num='9',name='0.8V',func=pin_types.INPUT,unit=1),
            Pin(num='10',name='0.4V',func=pin_types.INPUT,unit=1),
            Pin(num='11',name='0.2V',func=pin_types.INPUT,unit=1),
            Pin(num='12',name='0.1V',func=pin_types.INPUT,unit=1),
            Pin(num='13',name='EN',func=pin_types.INPUT,unit=1),
            Pin(num='14',name='NR',func=pin_types.PASSIVE,unit=1),
            Pin(num='15',name='IN',func=pin_types.PWRIN,unit=1),
            Pin(num='16',name='IN',func=pin_types.PASSIVE,unit=1),
            Pin(num='20',name='OUT',func=pin_types.PWROUT,unit=1),
            Pin(num='21',name='EP',func=pin_types.PASSIVE,unit=1)], 'unit_defs':[] }),
        Part(**{ 'name':'C', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'C'}), 'ref_prefix':'C', 'fplist':[''], 'footprint':'Capacitor_SMD:C_0805_2012Metric', 'keywords':'cap capacitor', 'description':'Unpolarized capacitor', 'datasheet':'', 'pins':[
            Pin(num='1',func=pin_types.PASSIVE,unit=1),
            Pin(num='2',func=pin_types.PASSIVE,unit=1)], 'unit_defs':[] }),
        Part(**{ 'name':'D_Schottky', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'D_Schottky'}), 'ref_prefix':'D', 'fplist':[''], 'footprint':'Diode_THT:D_DO-201AD_P15.24mm_Horizontal', 'keywords':'diode Schottky', 'description':'Schottky diode', 'datasheet':'', 'pins':[
            Pin(num='1',name='K',func=pin_types.PASSIVE,unit=1),
            Pin(num='2',name='A',func=pin_types.PASSIVE,unit=1)], 'unit_defs':[] }),
        Part(**{ 'name':'TPS7A3301RGW', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'TPS7A3301RGW'}), 'ref_prefix':'U', 'fplist':['Package_DFN_QFN:Texas_RGW0020A_VQFN-20-1EP_5x5mm_P0.65mm_EP3.15x3.15mm_ThermalVias'], 'footprint':'Package_DFN_QFN:Texas_RGW0020A_VQFN-20-1EP_5x5mm_P0.65mm_EP3.15x3.15mm_ThermalVias', 'keywords':'linear regulator ldo voltage negative', 'description':'1A, Low-Noise Lod-Dropout Negative Voltage Regulator, -3..-36V Input, Adjustable -1.18...-33V Output, VQFN-20', 'datasheet':'https://www.ti.com/lit/ds/symlink/tps7a33.pdf', 'pins':[
            Pin(num='1',name='OUT',func=pin_types.PWROUT,unit=1),
            Pin(num='3',name='FB',func=pin_types.INPUT,unit=1),
            Pin(num='7',name='GND',func=pin_types.PWRIN,unit=1),
            Pin(num='13',name='EN',func=pin_types.INPUT,unit=1),
            Pin(num='14',name='NR/SS',func=pin_types.PASSIVE,unit=1),
            Pin(num='15',name='IN',func=pin_types.PWRIN,unit=1),
            Pin(num='16',name='IN',func=pin_types.PASSIVE,unit=1),
            Pin(num='20',name='OUT',func=pin_types.PASSIVE,unit=1),
            Pin(num='21',name='EP',func=pin_types.PWRIN,unit=1)], 'unit_defs':[] }),
        Part(**{ 'name':'MCP1703Ax-500xxDB', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'MCP1703Ax-500xxDB'}), 'ref_prefix':'U', 'fplist':['Package_TO_SOT_SMD:SOT-223-3_TabPin2', 'Package_TO_SOT_SMD:SOT-223-3_TabPin2'], 'footprint':'Package_TO_SOT_SMD:SOT-223-3_TabPin2', 'keywords':'REGULATOR LDO', 'description':'Low Quiescent Current LDO Regulator, 5.0V, 250mA, Vin<=16V, SOT-223', 'datasheet':'http://ww1.microchip.com/downloads/en/DeviceDoc/20005122B.pdf', 'pins':[
            Pin(num='1',name='VI',func=pin_types.PWRIN,unit=1),
            Pin(num='2',name='GND',func=pin_types.PWRIN,unit=1),
            Pin(num='3',name='VO',func=pin_types.PWROUT,unit=1)], 'unit_defs':[] }),
        Part(**{ 'name':'NetTie_2', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'NetTie_2'}), 'ref_prefix':'NT', 'fplist':[''], 'footprint':'NetTie:NetTie-2_SMD_Pad0.5mm', 'keywords':'net tie short', 'description':'Net tie, 2 pins', 'datasheet':'', 'pins':[
            Pin(num='1',name='1',func=pin_types.PASSIVE,unit=1),
            Pin(num='2',name='2',func=pin_types.PASSIVE,unit=1)], 'unit_defs':[] }),
        Part(**{ 'name':'LM4040DBZ-2.5', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'LM4040DBZ-2.5'}), 'ref_prefix':'U', 'fplist':['Package_TO_SOT_SMD:SOT-23', 'Package_TO_SOT_SMD:SOT-23'], 'footprint':'Package_TO_SOT_SMD:SOT-23', 'keywords':'diode device voltage reference shunt', 'description':'2.500V Precision Micropower Shunt Voltage Reference, SOT-23', 'datasheet':'http://www.ti.com/lit/ds/symlink/lm4040-n.pdf', 'pins':[
            Pin(num='1',name='K',func=pin_types.PASSIVE,unit=1),
            Pin(num='2',name='A',func=pin_types.PASSIVE,unit=1),
            Pin(num='3',name='NC',func=pin_types.NOCONNECT,unit=1)], 'unit_defs':[] }),
        Part(**{ 'name':'LM2903', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'LM2903'}), 'ref_prefix':'U', 'fplist':[''], 'footprint':'Package_SO:SOIC-8_3.9x4.9mm_P1.27mm', 'keywords':'cmp open collector', 'description':'Low-Power, Low-Offset Voltage, Dual Comparators, DIP-8/SOIC-8/SOP-8/TSSOP-8/VSSOP-8', 'datasheet':'http://www.ti.com/lit/ds/symlink/lm393.pdf', 'pins':[
            Pin(num='1',func=pin_types.OPENCOLL,unit=1),
            Pin(num='2',name='-',func=pin_types.INPUT,unit=1),
            Pin(num='3',name='+',func=pin_types.INPUT,unit=1),
            Pin(num='5',name='+',func=pin_types.INPUT,unit=2),
            Pin(num='6',name='-',func=pin_types.INPUT,unit=2),
            Pin(num='7',func=pin_types.OPENCOLL,unit=2),
            Pin(num='4',name='V-',func=pin_types.PWRIN,unit=3),
            Pin(num='8',name='V+',func=pin_types.PWRIN,unit=3)], 'unit_defs':[{'label': 'uA', 'num': 1, 'pin_nums': ['2', '3', '1']},{'label': 'uB', 'num': 2, 'pin_nums': ['6', '5', '7']},{'label': 'uC', 'num': 3, 'pin_nums': ['8', '4']}] }),
        Part(**{ 'name':'BC847', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'BC847'}), 'ref_prefix':'Q', 'fplist':['', 'Package_TO_SOT_SMD:SOT-23'], 'footprint':'Package_TO_SOT_SMD:SOT-23', 'keywords':'NPN Small Signal Transistor', 'description':'0.1A Ic, 45V Vce, NPN Transistor, SOT-23', 'datasheet':'http://www.infineon.com/dgdl/Infineon-BC847SERIES_BC848SERIES_BC849SERIES_BC850SERIES-DS-v01_01-en.pdf?fileId=db3a304314dca389011541d4630a1657', 'pins':[
            Pin(num='1',name='B',func=pin_types.INPUT,unit=1),
            Pin(num='2',name='E',func=pin_types.PASSIVE,unit=1),
            Pin(num='3',name='C',func=pin_types.PASSIVE,unit=1)], 'unit_defs':[] }),
        Part(**{ 'name':'D_Zener', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'D_Zener'}), 'ref_prefix':'D', 'fplist':[''], 'footprint':'Diode_THT:D_DO-35_SOD27_P7.62mm_Horizontal', 'keywords':'diode', 'description':'Zener diode', 'datasheet':'', 'pins':[
            Pin(num='1',name='K',func=pin_types.PASSIVE,unit=1),
            Pin(num='2',name='A',func=pin_types.PASSIVE,unit=1)], 'unit_defs':[] }),
        Part(**{ 'name':'AO3401A', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'AO3401A'}), 'ref_prefix':'Q', 'fplist':['Package_TO_SOT_SMD:SOT-23', 'Package_TO_SOT_SMD:SOT-23'], 'footprint':'Package_TO_SOT_SMD:SOT-23', 'keywords':'P-Channel MOSFET', 'description':'-4.0A Id, -30V Vds, P-Channel MOSFET, SOT-23', 'datasheet':'http://www.aosmd.com/pdfs/datasheet/AO3401A.pdf', 'pins':[
            Pin(num='1',name='G',func=pin_types.INPUT,unit=1),
            Pin(num='2',name='S',func=pin_types.PASSIVE,unit=1),
            Pin(num='3',name='D',func=pin_types.PASSIVE,unit=1)], 'unit_defs':[] }),
        Part(**{ 'name':'LM339', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'LM339'}), 'ref_prefix':'U', 'fplist':[''], 'footprint':'Package_SO:TSSOP-14_4.4x5mm_P0.65mm', 'keywords':'cmp open collector', 'description':'Quad Differential Comparators, SOIC-14/TSSOP-14', 'datasheet':'https://www.st.com/resource/en/datasheet/lm139.pdf', 'pins':[
            Pin(num='2',func=pin_types.OPENCOLL,unit=1),
            Pin(num='4',name='-',func=pin_types.INPUT,unit=1),
            Pin(num='5',name='+',func=pin_types.INPUT,unit=1),
            Pin(num='1',func=pin_types.OPENCOLL,unit=2),
            Pin(num='6',name='-',func=pin_types.INPUT,unit=2),
            Pin(num='7',name='+',func=pin_types.INPUT,unit=2),
            Pin(num='10',name='-',func=pin_types.INPUT,unit=3),
            Pin(num='11',name='+',func=pin_types.INPUT,unit=3),
            Pin(num='13',func=pin_types.OPENCOLL,unit=3),
            Pin(num='8',name='-',func=pin_types.INPUT,unit=4),
            Pin(num='9',name='+',func=pin_types.INPUT,unit=4),
            Pin(num='14',func=pin_types.OPENCOLL,unit=4),
            Pin(num='3',name='V+',func=pin_types.PWRIN,unit=5),
            Pin(num='12',name='V-',func=pin_types.PWRIN,unit=5)], 'unit_defs':[{'label': 'uA', 'num': 1, 'pin_nums': ['2', '4', '5']},{'label': 'uB', 'num': 2, 'pin_nums': ['6', '1', '7']},{'label': 'uC', 'num': 3, 'pin_nums': ['13', '11', '10']},{'label': 'uD', 'num': 4, 'pin_nums': ['14', '9', '8']},{'label': 'uE', 'num': 5, 'pin_nums': ['3', '12']}] }),
        Part(**{ 'name':'Conn_01x07', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'Conn_01x07'}), 'ref_prefix':'J', 'fplist':[''], 'footprint':'Connector_PinHeader_2.54mm:PinHeader_1x07_P2.54mm_Vertical', 'keywords':'connector', 'description':'Generic connector, single row, 01x07, script generated (kicad-library-utils/schlib/autogen/connector/)', 'datasheet':'', 'pins':[
            Pin(num='1',name='Pin_1',func=pin_types.PASSIVE,unit=1),
            Pin(num='2',name='Pin_2',func=pin_types.PASSIVE,unit=1),
            Pin(num='3',name='Pin_3',func=pin_types.PASSIVE,unit=1),
            Pin(num='4',name='Pin_4',func=pin_types.PASSIVE,unit=1),
            Pin(num='5',name='Pin_5',func=pin_types.PASSIVE,unit=1),
            Pin(num='6',name='Pin_6',func=pin_types.PASSIVE,unit=1),
            Pin(num='7',name='Pin_7',func=pin_types.PASSIVE,unit=1)], 'unit_defs':[] }),
        Part(**{ 'name':'Conn_01x01', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'Conn_01x01'}), 'ref_prefix':'J', 'fplist':[''], 'footprint':'Connector_PinHeader_2.54mm:PinHeader_1x01_P2.54mm_Vertical', 'keywords':'connector', 'description':'Generic connector, single row, 01x01, script generated (kicad-library-utils/schlib/autogen/connector/)', 'datasheet':'', 'pins':[
            Pin(num='1',name='Pin_1',func=pin_types.PASSIVE,unit=1)], 'unit_defs':[] }),
        Part(**{ 'name':'TestPoint', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'TestPoint'}), 'ref_prefix':'TP', 'fplist':[''], 'footprint':'TestPoint:TestPoint_Keystone_5000-5004_Miniature', 'keywords':'test point tp', 'description':'test point', 'datasheet':'', 'pins':[
            Pin(num='1',name='1',func=pin_types.PASSIVE,unit=1)], 'unit_defs':[] })])