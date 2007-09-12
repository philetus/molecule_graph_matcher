# Custom pyMol gui for pyposey molecule matcher.

import threading
import Tkinter
import Molecules as M
import PDBParser
import Graph_Matcher as GM

pymol = None
listbox = None
scrollbar = None

app = None


def find (l,f): #XXX replace with hashtable
  for x in l:
    if f(x):
      return x
  return None


def highlight_atoms(pymol, pc_map, pdb_graph, posey_map):
  for unique in posey_map.values():
    print pc_map
    name = pdb_graph.node_dict[pc_map[unique]].atom_name
    print "Displaying %s." % name
    pymol.cmd.show("spheres", name)


def armor(s):
  return s.replace(" ","_")


def list_sel_command(event=None):
  print "foo"
  try:
    name = listbox.get(listbox.curselection())
  except Tkinter.TclError:
    return
  print name
  try:
    pymol.cmd.reinitialize ()
    pymol.cmd.load("pdbs/%s.pdb" % name)
    pymol.cmd.center(armor(name))
    pymol.cmd.set("sphere_scale", value=0.25)
    pymol.cmd.set("stick_radius", value=0.1)
    pymol.cmd.show("sticks")
    #pymol.cmd.show("spheres")
  except pymol.CmdException:
    print "Unable to load file pdbs/%s.pdb" % name
  pdb_graph = PDBParser.parse_file("pdbs/%s.pdb" % name)
  #(ignore, pc_graph) = (find(app.isomorphism_list, lambda x : x[0] == name))
  #posey_map = None
  (ignore, pc_graph, posey_map) = (find(app.isomorphism_list, lambda x : x[0] == name))
  print (ignore, pc_graph, posey_map)
#  try:
  print 1
  print "pc:"
  print pc_graph
  print "pdb:"
  print pdb_graph
  pdb_graph_matcher = GM.Graph_Matcher(pdb_graph, pc_graph)
  print 2
  pc_map = pdb_graph_matcher.get_isomorphism()
  print 3
#  if pc_map is None:
#    raise Exception
  highlight_atoms(pymol, pc_map, pdb_graph, posey_map)
#  except Exception :
#    print "Unable to highlight atoms."

def set_gui_list(l):
  i = listbox.curselection()
  item = None
  try:
    global item
    item = listbox.get(i)
  except Tkinter.TclError:
    pass
  listbox.delete(0,Tkinter.END)
  map(lambda x : listbox.insert(Tkinter.END, x[0]), l)
  try:
    j = l.index(item)
    listbox.select_set(j)
  except ValueError:
    pass


def make_list_window():
  molecule_list_window = Tkinter.Tk()
  molecule_list_window.title("Possible Molecules")

  button = Tkinter.Button(molecule_list_window)
  button.config(text="Display Molecule")
  button.config(command=list_sel_command)
  button.pack(fill=Tkinter.X, side=Tkinter.TOP)

  global scrollbar
  scrollbar = Tkinter.Scrollbar(orient=Tkinter.VERTICAL)
  scrollbar.pack(fill=Tkinter.Y, side=Tkinter.RIGHT)

  global listbox
  listbox = Tkinter.Listbox(molecule_list_window)
  listbox.config(selectmode=Tkinter.SINGLE)
  listbox.pack(fill=Tkinter.BOTH, side=Tkinter.RIGHT)

  listbox.config(yscrollcommand=scrollbar.set)
  scrollbar.config(command=listbox.yview)

  global app
  app = M.start(set_gui_list, list_sel_command)
  molecule_list_window.mainloop()


def __init__(pm,i):
  global pymol
  pymol = pm

  t = threading.Thread(target=make_list_window,args=())
  t.setDaemon(1)
  t.start()

