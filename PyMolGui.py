# Custom pyMol gui for pyposey molecule matcher.

import threading
import Tkinter
import Molecules as M
import PDBParser
import Graph_Matcher as GM
import webbrowser

# how atoms should be colored -- currently corresponds to posey pieces
atom_colors = [("O","green"),("C","blue"),("H","yellow"),("Na","red")]

# globals for accessing needed components
pymol = None
listbox = None
scrollbar = None

app = None

def find (l,f): #XXX replace with hashtable
  for x in l:
    if f(x):
      return x
  return None

# make the atoms we've built into spheres, the others into sticks
def highlight_atoms(pymol, pc_map, pdb_graph, posey_map):
  # create a set of pdb graph nodes that are in the structure we've built
  node_set = set()
  for unique in posey_map.values():
    node_set.add(pc_map[unique])
  # check each node in the pdb graph, make it either a stick or a ball
  for (unique,node) in pdb_graph.node_dict.iteritems():
    name = node.atom_name
    if unique in node_set:
      pymol.cmd.show("spheres", name)
    else:
      pymol.cmd.hide("spheres", name)

# turn file names into PyMol atom names
def armor(s):
  return s.replace(" ","_")

# we store the name of the currently selected atom to tell if it is changed and
# we need to load the new file
current_name = None

# gets run when a user presses the "display molecule" button, or after updating
# the currently selected molecule when the user has added a posey piece
def list_sel_command():
  global listbox
  global current_name
  try:
    # try to get the currently selected molecule
    name = listbox.get(listbox.curselection())
  except Tkinter.TclError:
    # nothing is selected.  Blank the screen and return.
    pymol.cmd.reinitialize ()
    current_name = None
    return
  try:
    if name != current_name:
      # we are displaying a new molecule
      current_name = name
      # blank screen and unload old molecule
      pymol.cmd.reinitialize ()
      #load molecule
      pymol.cmd.load("pdbs/%s.pdb" % name)
      #color mollecule
      for (atom,color) in atom_colors:
        pymol.cmd.color(color, "/%s////%s*" % (armor(name),atom))
      # center view on the molecule
      pymol.cmd.center(armor(name))
      #display it in the right way
      pymol.cmd.set("sphere_scale", value=0.25)
      pymol.cmd.set("stick_radius", value=0.1)
      pymol.cmd.show("sticks")
  except pymol.CmdException:
    print "Unable to load file pdbs/%s.pdb" % name
  try:
    pdb_graph = PDBParser.parse_file("pdbs/%s.pdb" % name)
    #now try to highlight the molecule
    # find the PubChem xml molecule corresponding to this PDB file
    (ignore, pc_graph, posey_map) = (find(app.isomorphism_list, lambda x : x[0] == name))
    pdb_graph_matcher = GM.Graph_Matcher(pdb_graph, pc_graph)
    pc_map = pdb_graph_matcher.get_isomorphism()
    if pc_map is None:
      raise Exception
    # if we succeeded in finding a correspondance, highlight atoms
    highlight_atoms(pymol, pc_map, pdb_graph, posey_map)
  except Exception :
    print "Unable to highlight atoms."

# on changing the posey model, select correct molecule and display it
def update_display ():
  # find the current molecule in the listbox, or, if it doesn't exist,
  # select the first molecule
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
  # display selected molecule
  list_sel_command()

# hook to allow matcher to set the listbox list
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

# open wikipedia page on molecule
def info_command():
  i = listbox.curselection()
  try:
    item = listbox.get(i)
  except Tkinter.TclError:
    return
  webbrowser.open("http://en.wikipedia.org/wiki/%s" % armor(item))

#command for clear button -- clears the molecule view and deselects
def clear_command():
  pymol.cmd.reinitialize ()
  listbox.select_clear (0, Tkinter.END)

# set up the gui
def make_list_window():
  molecule_list_window = Tkinter.Tk()
  molecule_list_window.title("Possible Molecules")

  top_frame=Tkinter.Frame(molecule_list_window)
  top_frame.pack(fill=Tkinter.Y, side=Tkinter.TOP)
  bot_frame=Tkinter.Frame(molecule_list_window)
  bot_frame.pack(fill=Tkinter.Y, side=Tkinter.BOTTOM)

  global scrollbar
  scrollbar = Tkinter.Scrollbar(top_frame,orient=Tkinter.VERTICAL)
  scrollbar.pack(fill=Tkinter.Y, side=Tkinter.RIGHT)

  global listbox
  listbox = Tkinter.Listbox(top_frame)
  listbox.config(selectmode=Tkinter.SINGLE)
  listbox.pack(fill=Tkinter.X, side=Tkinter.TOP)

  listbox.config(yscrollcommand=scrollbar.set)
  scrollbar.config(command=listbox.yview)

  button = Tkinter.Button(bot_frame)
  button.config(text="Display Molecule")
  button.config(command=list_sel_command)
  button.pack(fill=Tkinter.X, side=Tkinter.TOP)

  clear_button = Tkinter.Button(bot_frame)
  clear_button.config(text="Clear")
  clear_button.config(command=clear_command)
  clear_button.pack(fill=Tkinter.X, side=Tkinter.RIGHT)

  info_button = Tkinter.Button(bot_frame)
  info_button.config(text="Molecule Info")
  info_button.config(command=info_command)
  info_button.pack(fill=Tkinter.X, side=Tkinter.RIGHT)

  global app
  app = M.start(set_gui_list, update_display)
  molecule_list_window.mainloop()

# spawn a thread to be the gui
def __init__(pm,i):
  global pymol
  pymol = pm

  t = threading.Thread(target=make_list_window,args=())
  t.setDaemon(1)
  t.start()

