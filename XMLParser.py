import xml.sax as XS
import xml.sax.handler as XH

from sys import argv

import Graph as G
import Graph_Node as GN

graph = None
name = None

class StructureHandler(XH.ContentHandler):

  atoms = {}
  bonds = {}

  inside_atom = 0
  inside_bond1 = 0
  inside_bond2 = 0
  inside_name = 0
  passed_name = 0

  atom_count = 0
  element_count = 0
  beginning_count = 0
  end_count = 0

  def startElement(self,name,attrs):
    if name == "PC-Atoms_aid_E":
      self.inside_atom = 1
    elif name == "PC-Element":
      self.element_count += 1
      self.atoms[self.element_count].label = attrs.getValue("value")
    elif name == "PC-Bonds_aid1_E":
      self.inside_bond1 = 1
    elif name == "PC-Bonds_aid2_E":
      self.inside_bond2 = 1
    elif name == "PC-InfoData_value_sval":
      self.inside_name = 1

  def endElement(self,name):
    if name == "PC-Atoms_aid_E":
      self.inside_atom = 0
    elif name == "PC-Bonds_aid1_E":
      self.inside_bond1 = 0
    elif name == "PC-Bonds_aid2_E":
      self.inside_bond2= 0
    elif name == "PC-InfoData_value_sval":
      self.inside_name = 0

  def characters(self,content):
    if self.inside_atom:
      self.atom_count += 1
      gn = GN.Graph_Node(content)
      self.atoms[self.atom_count] = gn
      graph.add_node(gn)
    elif self.inside_bond1:
      self.beginning_count += 1
      self.bonds[ self.beginning_count] = self.find_atom(content)
    elif self.inside_bond2:
      self.end_count += 1
      graph.add_edge(self.bonds[self.end_count], self.find_atom(content))
    elif self.inside_name and self.passed_name:
      global name
      name = content
      self.passed_name = 0
    elif content == "IUPAC Name":
      self.passed_name = 1

  def find_atom(self, content):
    return self.atoms[int(content)]

def parse_file(file):
  global graph
  graph = G.Graph()

  structure_handler = StructureHandler()
  XS.parse(file, structure_handler)

  return (name,graph)
