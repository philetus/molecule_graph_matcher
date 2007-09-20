# Custom pyMol gui for pyposey molecule matcher.

import threading
import Tkinter
import Molecules as M
import PDBParser
import Graph_Matcher as GM
import webbrowser

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
  node_set = set()
  for unique in posey_map.values():
    node_set.add(pc_map[unique])
  for (unique,node) in pdb_graph.node_dict.iteritems():
    name = node.atom_name
    if unique in node_set:
      print "Displaying %s." % name
      pymol.cmd.show("spheres", name)
    else:
      pymol.cmd.hide("spheres", name)


def armor(s):
  return s.replace(" ","_")


current_name = None


def list_sel_command():
  global listbox
  global current_name
  try:
    name = listbox.get(listbox.curselection())
  except Tkinter.TclError:
    pymol.cmd.reinitialize ()
    current_name = None
    return
  try:
    print "Current name is %s." % current_name
    if name != current_name:
      current_name = name
      pymol.cmd.reinitialize ()
      pymol.cmd.load("pdbs/%s.pdb" % name)
      pymol.cmd.center(armor(name))
      pymol.cmd.set("sphere_scale", value=0.25)
      pymol.cmd.set("stick_radius", value=0.1)
      pymol.cmd.show("sticks")
  except pymol.CmdException:
    print "Unable to load file pdbs/%s.pdb" % name
  pdb_graph = PDBParser.parse_file("pdbs/%s.pdb" % name)
  (ignore, pc_graph, posey_map) = (find(app.isomorphism_list, lambda x : x[0] == name))
  try:
    pdb_graph_matcher = GM.Graph_Matcher(pdb_graph, pc_graph)
    pc_map = pdb_graph_matcher.get_isomorphism()
    if pc_map is None:
      raise Exception
    highlight_atoms(pymol, pc_map, pdb_graph, posey_map)
  except Exception :
    print "Unable to highlight atoms."


def update_display ():
  global current_name
  l = listbox.get(0,Tkinter.END)
  n = len(l)
  if n > 0:
    ix = 0
    for i in range(0,n):
      if l[i] == current_name:
        ix = i
        break
    listbox.select_set(ix)
  print "in u_d, calling list_sel"
  list_sel_command()


def set_gui_list(l):
  i = listbox.curselection()
  item = None
  try:
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

def info_command():
  i = listbox.curselection()
  try:
    item = listbox.get(i)
  except Tkinter.TclError:
    return
  webbrowser.open("http://en.wikipedia.org/wiki/%s" % armor(item))


def make_list_window():
  molecule_list_window = Tkinter.Tk()
  molecule_list_window.title("Possible Molecules")

  global scrollbar
  scrollbar = Tkinter.Scrollbar(orient=Tkinter.VERTICAL)
  scrollbar.pack(fill=Tkinter.Y, side=Tkinter.RIGHT)

  global listbox
  listbox = Tkinter.Listbox(molecule_list_window)
  listbox.config(selectmode=Tkinter.SINGLE)
  listbox.pack(fill=Tkinter.X, side=Tkinter.TOP)

  listbox.config(yscrollcommand=scrollbar.set)
  scrollbar.config(command=listbox.yview)

  button = Tkinter.Button(molecule_list_window)
  button.config(text="Display Molecule")
  button.config(command=list_sel_command)
  button.pack(fill=Tkinter.X, side=Tkinter.TOP)

  info_button = Tkinter.Button(molecule_list_window)
  info_button.config(text="Molecule Info")
  info_button.config(command=info_command)
  info_button.pack(fill=Tkinter.X, side=Tkinter.TOP)

  global app
  app = M.start(set_gui_list, update_display)
  molecule_list_window.mainloop()


def __init__(pm,i):
  global pymol
  pymol = pm

  t = threading.Thread(target=make_list_window,args=())
  t.setDaemon(1)
  t.start()

