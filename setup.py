"""
Setup module of the BlankOnOff app

Author: Mangachh
Version: 1.5
"""



import subprocess
import os
import shutil

from finalSaver import Saver


# check the route of this files
# if files are NOT in the folder, move them
# when files are in folder create the launcher
# use copy, not mv.

PATH = "/.local/share/blankonoff/"
HOME = os.path.expanduser("~")
APP_NAME = "blankonoff.desktop"
START_NAME= "blankonoff_start.desktop"
SCRIPT_NAME = "finalSaver.py"
ICON_NAME = "off.svg"

# launcher desktop file
LAUNCHER_FILE= ["[Desktop Entry]", 
              "Version=1.0", 
              "Type=Application", 
              "Name=BlankOnOff", 
              "Comment=Enables/Disables the screen blanking", 
              "Terminal=false"]

# start file desktop file
START_FILE= ["[Desktop Entry]", 
              "Version=1.0", 
              "Type=Application", 
              "Name=BlankOnOff Starter", 
              "Comment=Checks the Blankonoff state and sets the screen according to it", 
              "Terminal=true",
              f"Exec={HOME}{PATH}start.py",
              f"TryExec={HOME}{PATH}start.py",
              f"Path={HOME}{PATH}",
              "Categories=Python;Desktop;Screensaver;Xfce4;"]



def get_installation_paths() -> (str, str):
    """
    Gets the paths where the file is and the destination as 
    HOME+PATH

    Returns:
        tuple[str, str]: path where the file is and destination
    """
    source = os.path.dirname(os.path.abspath(__file__))
    destination = f"{HOME}{PATH}"
    
    return (source, destination)
    
    
def create_installation_directory(source: str, destination: str) -> bool: 
    """
    Creates the directory for the installation. OJU! This is not for the 
    launcher, only for the data

    Args:
        source (str): where the file is
        destination (str): where to put the data

    Returns:
        bool: is the directory created?
    """
    # cambiar eso para file     
    print(f"Desired Path: {destination}")
    print(f"Current Path: {source}")
    
    # if file not in path, create directories and move files
    # oju! it doesn't check if all files are in the path.
    if source != destination:
        print(f"Directories don't match.\nCheckin directory at: {destination}")
        
        # check if path exists
        if not os.path.exists(destination):
            print(f"Directory not exists. Creatring directory at: {destination}")
            try:
                os.makedirs(destination)
            except OSError:
                print(f"Creation of path {destination} failed.")
                return False
            else:
                print(f"Succefully created directory at: {destination}")
        else:
            print("Directory already exists.")
            
    return True           
    


def move_files(source: str, destination: str) -> bool:
    """Moves files from the source to the destination
    plus: it works for every file

    Args:
        source (str): where the files are
        destination (str): destination

    Returns:
        bool: moved succefully?
    """
    
    print("Copying files...")
    
    for file in os.listdir(source):
        full_sr = f"{source}/{file}"
        full_dest = f"{destination}/{file}"
        
        if os.path.isfile(full_sr):
            try:
                shutil.copy(full_sr, full_dest)
                print(f"Copied from {full_sr} to {full_dest}")
            except FileNotFoundError:
                print("File not found")
                return False
            except shutil.SameFileError:
                print("Origin and destination are the same")
                return True # true 'cause the files are but don't know if the app is
            except:
                print("Error")
                return False
                
    
    return True


# Queries to add the panel
CMD_ADD_LAUNCHER = "xfce4-panel --add=launcher"
CMD_GET_PANELS = "xfconf-query -c xfce4-panel -p /panels"
CMD_GET_IDS = "xfconf-query -c xfce4-panel -p /panels/%s/plugin-ids"
CMD_GET_TYPE = "xfconf-query -c xfce4-panel -p /plugins/plugin-%s" # change name
CMD_ADD_PLUGIN = "xfconf-query -c xfce4-panel -p /plugins/plugin-%s --create -t string -s launcher"
CMD_ADD_PLUGIN_DATA = "xfconf-query -c xfce4-panel -p /plugins/plugin-%s/blankonoff --create -t string -s 1.7"
                    
CMD_GET_ITEMS = "xfconf-query -c xfce4-panel -p /plugins/plugin-%s/items "
CMD_ADD_IDS = "xfconf-query -c xfce4-panel -p /panels/%s/plugin-ids %s -a"
CMD_ADD_ID_ARGS = "-t int -s %s"

def get_panel_id_to_register(panel_ids: list) -> str:
    print("Choose the panel where to put the launcher:")
    in_app = True
    to_add_id : str
    while in_app:   
        index = 0         
        for i in panel_ids:                
            print(f"{index} - panel-{i}")   
            index += 1        
        try:                
            to_add_id = int(input(">>"))
        except:
            print("Only numbers allowed")
            continue
        
        if to_add_id < 0 or to_add_id >= len(panel_ids) :
            print("Incorrect panel. Write the number of the panel")
        else:    
            in_app = False
            panel_to_add = f"panel-{panel_ids[to_add_id]}"
    
    return panel_to_add


def get_plugins_by_panel(panel_ids : list) -> dict:
    plugins_by_panel = dict()
    for panel in panel_ids:
        panel_name = f"panel-{panel}"
        try:
            resp = subprocess.check_output(CMD_GET_IDS % panel_name, shell=True).decode("UTF-8").splitlines()
            print(f"Raw Id's for {panel_name}: {resp}")
        except Exception as e:
            print(e)
            continue
            
        ids = [i for i in resp if i.isdigit()]
        # print(ids)
        plugins_by_panel[panel_name] = ids
        print(f"Id's from {panel_name}: {plugins_by_panel[panel_name]}")
    
    return plugins_by_panel

def get_next_plugin_id(plugins_by_panel: dict) -> int:
    launcher_id : int
    try:  
        print(f"values: {plugins_by_panel.values}")
        launcher_id = int(max(plugins_by_panel.values())[0]) + 1
        print(f"Launcher id: {launcher_id}")
    except Exception as e:
        print(e)
        # in case there's no value
        launcher_id = 0 
    
    return launcher_id
    
    
def register_to_panel() -> str:
    """Registers the plugin to xfce4-panel

    Returns:
        str: id of the plugin
    """
        
    print("Getting panels")
    resp = subprocess.check_output(CMD_GET_PANELS, shell=True).decode("UTF-8").splitlines()
    panel_ids = [i for i in resp if i.isdigit()]
    print("Panel id's:", panel_ids)

    panel_id : str
    # get the panel where to put
    if len(panel_ids) > 1:        
        panel_id = get_panel_id_to_register(panel_ids)
                
    # get the ids by panel
    print(f"Panel to add launcher selected: {panel_id}")
    plugins_by_panel = get_plugins_by_panel(panel_ids)        
    launcher_id = get_next_plugin_id(plugins_by_panel)   
    print(f"Found launcher id: {launcher_id}")
    
    # add the array
    ids_string = " ".join([CMD_ADD_ID_ARGS % i for i in plugins_by_panel[panel_id]])
    
    # add the new id
    ids_string += " " + CMD_ADD_ID_ARGS % launcher_id
    print(f"Args: {ids_string}")
    output = subprocess.check_output(CMD_ADD_IDS % (panel_id, ids_string), shell=True).decode("UTF-8")
    print(output)
    
    output = subprocess.check_output(CMD_ADD_PLUGIN % (launcher_id), shell=True).decode("UTF-8")
    output = subprocess.check_output(CMD_ADD_PLUGIN_DATA % (launcher_id), shell=True).decode("UTF-8")
    print(output)
    # add the property to the panel    
    subprocess.check_output("xfce4-panel -r", shell=True)
     
    return launcher_id    


def create_desktop_file(path: str, lines: list) -> bool:
    
    print(f"Creating desktop file at {path}")
    with open(path, "w") as f:
        try:
            f.writelines(line + "\n" for line in lines)
            return True
        except Exception as e:
            print("Oju! Something went wrong: {e}")
            return False


def set_launcher(id: str, source: str, destination: str, filename:str) -> bool:
    """Creates a launcher and copies it to the plugin folder in order
    to have the launcher in the panel

    Args:
        id (str): id of the plugin
        source (str): where the file is
        destination (str): where the files is going
        filename (str): desktop filename

    Returns:
        bool: _description_
    """
    os.makedirs(destination, exist_ok=True)
    
    # create the destkop file
    panel_file = LAUNCHER_FILE
    panel_file.extend((f"Exec={source}{SCRIPT_NAME}\n",
                       f"Icon={source}{ICON_NAME}\n"))
    full_path = f"{source}/{filename}"
        
    if create_desktop_file(full_path, panel_file):    
        # copy the desktop to ~/.config/xfce4/plugin/launcher-id
        shutil.copy(full_path, f"{destination}/{filename}")
        subprocess.check_output(f"xfconf-query -c xfce4-panel -p /plugins/plugin-{id}/items -t string -s {filename} -a --create", shell=True)
        return True
    
    return False

    
def set_autostart(home:str) -> bool:
    """
    Sets the autostart folder and creates the launcher to work properly.
    It uses /$HOME/.config/autostart/

    Args:
        source (str): the home directory

    Returns:
        bool: is the autostart correctly installed?
    """
    os.makedirs(f"{HOME}/.config/autostart/", exist_ok=True)
    path_start = f"{HOME}/.config/autostart/"
   
    if create_desktop_file(f"{home}/{START_NAME}", START_FILE):
         shutil.copy(f"{home}/{START_NAME}", f"{path_start}/{START_NAME}")
         return True
     
    return False      
    
    
    
    
def main():
    """Main loop
    """
    (source, destination) = get_installation_paths()
    created = create_installation_directory(source, destination)  
      
    if created:
        if move_files(source, destination) == False:
            return               
       
        id = register_to_panel()
        
        if id == "":
            return
         
        del(source)
        
        home = f"{HOME}{PATH}" 
        destination = f"{HOME}/.config/xfce4/panel/launcher-{id}"            
        set_launcher(id, home, destination, APP_NAME)
        set_autostart(home)
        
        # disable on start
        Saver.disable_blanking()
             
    
if __name__ == "__main__":    
    main()
    
    
        
        
        
        