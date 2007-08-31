# Custom pyMol gui for pyposey molecule matcher.

import threading
import Tkinter
import Molecules

pymol = None
listbox = None
scrollbar = None

def list_sel_command():
  name = listbox.get(listbox.curselection())
  print name
  try:
    pymol.cmd.load("pdbs/%s.pdb" % name)
  except pymol.CmdException:
    print "Unable to load file pdbs/%s.pdb" % name
    pymol.cmd.load("pdbs/nitroglycerin.pdb")
  pymol.cmd.set("sphere_scale", value=0.25)
  pymol.cmd.set("stick_radius", value=0.1)
  pymol.cmd.show("sticks")
  pymol.cmd.show("spheres")

def set_gui_list(l):
  listbox.delete(0,Tkinter.END)
  map(lambda x : listbox.insert(Tkinter.END, x[0]), l)

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

  Molecules.start(set_gui_list)
  molecule_list_window.mainloop()


def __init__(pm,i):
  global pymol
  pymol = pm

  t = threading.Thread(target=make_list_window,args=())
  t.setDaemon(1)
  t.start()

