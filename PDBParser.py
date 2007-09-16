# Parse PDB files into graphs.  Used to match PDB graphs with PubChem XML
# graphs to discover which nodes to highlight.

import fileinput
import Graph_Node
import Graph

# Read in the file, figure out the compound name
def parse_file(file):
  serial_map = {}
  compound_name = file[0:-4]
  compound_name = compound_name[5:]
  compound_name = compound_name.replace(" ","_")
  g = Graph.Graph()
  for line in fileinput.input([file]):
    parse_line(line, g, serial_map, compound_name)
  return g

# Figure out if this line describes an atom, a bond or something else
def parse_line(line, g, serial_map, compound_name):
  record = line[0:6]
  if record == "ATOM  ":
    process_atom(line, g, serial_map, compound_name)
  elif record == "CONECT":
      process_connect(line, g, serial_map)
  else:
    pass

#  Parse an atom serial number
def serial_to_int(s):
  return int(s.strip(" "))

#  Create a node for an atom
def process_atom(line, g, serial_map, compound_name):
  #find the serial number
  serial_string = line[6:11]
  serial = serial_to_int(serial_string)
  # find what the file considers the atom name
  name_string = line[12:16]
  name = name_string.strip(" ")
  # find out what element this is for the label
  label = name.strip('0123456789')
  label = label.lower()
  # make the node
  gn = Graph_Node.Graph_Node(label)
  # stick the atom name in, in PyMol selection format
  gn.atom_name = "/" + compound_name + "////" + name
  # record what atom thi is
  serial_map[serial] = gn
  # add it to the graph
  g.add_node(gn)

# make conenctions
def process_connect(line, g, serial_map):
  l = len(line)
  initial = serial_map[serial_to_int(line[6:11])]
  hi = 16
  while hi < l:
    try:
      other = serial_map[serial_to_int(line[hi - 5 : hi])]
    except ValueError:
      return
    g.add_edge(initial, other)
    hi += 5
