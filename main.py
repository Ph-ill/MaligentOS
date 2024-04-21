#!/usr/bin/env python3
import shutil,time,os
from rgbprint import rgbprint
from asciimatics.widgets import Frame, ListBox, Layout, Divider, Text, \
    Button, TextBox, Widget, PopUpDialog, Label
from asciimatics.scene import Scene
from asciimatics.screen import Screen
from asciimatics.exceptions import ResizeScreenError, NextScene, StopApplication
from asciimatics.effects import Cog, Print
from asciimatics.renderers import ColourImageFile, ImageFile
from asciimatics.parsers import AnsiTerminalParser, Parser
import sys
import sqlite3
import subprocess 

debug = False

# Run the command and capture the output 
output = subprocess.check_output("bin/climage --unicode Images/Users-10/User6.jpg", shell=True) # Replace "ls" with your desired command 
# Convert the output to a string (Python 3.x) 
output = output.decode("utf-8") 
# Print the output 
ansi_text1 = output
# Run the command and capture the output 
output = subprocess.check_output("bin/climage --unicode Images/Users-25/User6.jpg", shell=True) # Replace "ls" with your desired command 
# Convert the output to a string (Python 3.x) 
output = output.decode("utf-8") 
# Print the output 
ansi_text2 = output
# Run the command and capture the output 
output = subprocess.check_output("bin/climage --unicode Images/Users-50/User6.jpg", shell=True) # Replace "ls" with your desired command 
# Convert the output to a string (Python 3.x) 
output = output.decode("utf-8") 
# Print the output 
ansi_text3 = output



# Initial data for the form
form_data = {
    "ansi_test1": ansi_text1,
    "ansi_test2": ansi_text2,
    "ansi_test3": ansi_text3
}

def print_centre(s):
    #print(s.center(shutil.get_terminal_size().columns))
    rgbprint(s.center(shutil.get_terminal_size().columns))

def print_centre_colour_delay(s,d,c):
    #print(s.center(shutil.get_terminal_size().columns))
    rgbprint(s.center(shutil.get_terminal_size().columns), color=c)
    time.sleep(d)

class ContactModel():
    def __init__(self):
        # Create a database in RAM.
        self._db = sqlite3.connect(':memory:')
        self._db.row_factory = sqlite3.Row

        # Create the basic contact table.
        self._db.cursor().execute('''
            CREATE TABLE contacts(
                id INTEGER PRIMARY KEY,
                name TEXT,
                phone TEXT,
                address TEXT,
                email TEXT,
                notes TEXT)
        ''')
        self._db.commit()

        # Current contact when editing.
        self.current_id = None

    def add(self, contact):
        self._db.cursor().execute('''
            INSERT INTO contacts(name, phone, address, email, notes)
            VALUES(:name, :phone, :address, :email, :notes)''',
                                  contact)
        self._db.commit()

    def get_summary(self):
        return self._db.cursor().execute(
            "SELECT name, id from contacts").fetchall()

    def get_contact(self, contact_id):
        return self._db.cursor().execute(
            "SELECT * from contacts WHERE id=:id", {"id": contact_id}).fetchone()

    def get_current_contact(self):
        if self.current_id is None:
            return {"name": "", "address": "", "phone": "", "email": "", "notes": ""}
        else:
            return self.get_contact(self.current_id)

    def update_current_contact(self, details):
        if self.current_id is None:
            self.add(details)
        else:
            self._db.cursor().execute('''
                UPDATE contacts SET name=:name, phone=:phone, address=:address,
                email=:email, notes=:notes WHERE id=:id''',
                                      details)
            self._db.commit()

    def delete_contact(self, contact_id):
        self._db.cursor().execute('''
            DELETE FROM contacts WHERE id=:id''', {"id": contact_id})
        self._db.commit()


class LoginWindow(Frame):
    def __init__(self, screen, model):
        super(LoginWindow, self).__init__(screen,
                                       screen.height * 2 // 3,
                                       screen.width * 2 // 3,
                                       on_load=self._reload_list,
                                       data=form_data,
                                       hover_focus=True,
                                       can_scroll=False,
                                       title="MaligentOS™")
        # Save off the model that accesses the contacts database.
        self._model = model

        # Create the form for displaying the list of contacts.
        self._list_view = ListBox(
            Widget.FILL_FRAME,
            model.get_summary(),
            name="contacts",
            add_scroll_bar=False,
            on_change=self._on_pick,
            on_select=self._edit)

        self.set_theme("maligent")
        self._login_button = Button("Login", self._login)
        self._createuser_button = Button("Create User", self._createuser)
        self._exit_button = Button("Exit", self._exit)
        layout = Layout([100], fill_frame=False)
        layout2 = Layout([1,1,1], fill_frame=True)
        layout3 = Layout([1,1,1], fill_frame=False)
        self.add_layout(layout)
        self.add_layout(layout2)
        self.add_layout(layout3)
        self.add_effect(Cog(screen, 20, 10, 20, direction=1, colour=1))
        self.add_effect(Cog(screen, 200, 40, 25, direction=-1, colour=1))
        layout.add_widget(Label("", align="^"), 0)
        layout.add_widget(Label("Welcome to MalignentOS™,", align="^"), 0)
        layout.add_widget(Label("Lorem ipsum dolor sit amet, consectetur adipiscing elit,", align="^"), 0)
        layout.add_widget(Label("sed do eiusmod tempor incididunt ut labore et dolore magna aliqua.", align="^"), 0)
        layout2.add_widget(TextBox(Widget.FILL_FRAME, "", "ansi_test1", as_string=True, line_wrap=False, parser=AnsiTerminalParser(), readonly=True),0)
        layout2.add_widget(TextBox(Widget.FILL_FRAME, "", "ansi_test2", as_string=True, line_wrap=False, parser=AnsiTerminalParser(), readonly=True),1)
        layout2.add_widget(TextBox(Widget.FILL_FRAME, "", "ansi_test3", as_string=True, line_wrap=False, parser=AnsiTerminalParser(), readonly=True),2)
        layout3.add_widget(Divider(draw_line=True,height=1), 0)
        layout3.add_widget(Divider(draw_line=True,height=1), 1)
        layout3.add_widget(Divider(draw_line=True,height=1), 2)
        layout3.add_widget(Button("Login", self._login), 0)
        layout3.add_widget(Button("Create User", self._createuser), 1)
        layout3.add_widget(Button("Exit", self._exit), 2)
        self.fix()
        self._on_pick()

    def _on_pick(self):
        self._login_button.disabled = self._list_view.value is None
        self._exit_button.disabled = self._list_view.value is None

    def _reload_list(self, new_value=None):
        self._list_view.options = self._model.get_summary()
        self._list_view.value = new_value

    def _add(self):
        self._model.current_id = None
        raise NextScene("Edit Contact")

    def _edit(self):
        self.save()
        self._model.current_id = self.data["contacts"]
        raise NextScene("Edit Contact")

    def _delete(self):
        self.save()
        self._model.delete_contact(self.data["contacts"])
        self._reload_list()

    def _login(self):
        self.save()
        #self._model.delete_contact(self.data["contacts"])
        self._reload_list()

    def _createuser(self):
        self.save()
        #self._model.delete_contact(self.data["contacts"])
        self._reload_list()

    def _exit(self):
        self._scene.add_effect(
            PopUpDialog(self._screen,
                "Are you sure?",
                ["Yes", "No"],
                has_shadow=True,
                on_close=self._quit_on_yes))

    @staticmethod
    def _quit():
        raise StopApplication("User pressed quit")

    @staticmethod
    def _quit_on_yes(selected):
        # Yes is the first button
        if selected == 0:
            os.system('cls' if os.name == 'nt' else 'clear')
            raise StopApplication("User requested exit")

class ContactView(Frame):
    def __init__(self, screen, model):
        super(ContactView, self).__init__(screen,
                                          screen.height * 2 // 3,
                                          screen.width * 2 // 3,
                                          hover_focus=True,
                                          can_scroll=False,
                                          title="Contact Details",
                                          reduce_cpu=True)
        # Save off the model that accesses the contacts database.
        self._model = model

        # Create the form for displaying the list of contacts.
        self.set_theme("maligent")
        layout = Layout([100], fill_frame=True)
        self.add_layout(layout)
        layout.add_widget(Text("Name:", "name"))
        layout.add_widget(Text("Address:", "address"))
        layout.add_widget(Text("Phone number:", "phone"))
        layout.add_widget(Text("Email address:", "email"))
        layout.add_widget(TextBox(
            Widget.FILL_FRAME, "Notes:", "notes", as_string=True, line_wrap=True))
        layout2 = Layout([1, 1, 1, 1])
        self.add_layout(layout2)
        layout2.add_widget(Button("OK", self._ok), 0)
        layout2.add_widget(Button("Cancel", self._cancel), 3)
        self.fix()

    def reset(self):
        # Do standard reset to clear out form, then populate with new data.
        super(ContactView, self).reset()
        self.data = self._model.get_current_contact()

    def _ok(self):
        self.save()
        self._model.update_current_contact(self.data)
        #raise NextScene("Main")
        intro()

    @staticmethod
    def _cancel():
        #raise NextScene("Main")
        intro()

contacts = ContactModel()

def demo(screen, scene):
    scenes = [
        Scene([LoginWindow(screen, contacts)], -1, name="Main"),
        #Scene([ContactView(screen, contacts)], -1, name="Edit Contact")
    ]
    screen.play(scenes, stop_on_resize=True, start_scene=scene, allow_int=True)

def intro():
    last_scene = None

    if debug:
        logo_globe_delay = float(0.001)
        logo_text_delay = float(0.001)
    else:
        logo_globe_delay = float(0.05)
        logo_text_delay = float(0.25)


    world_gradient = ["#00d4f0","#00d4ec","#00d4e8","#00d3e3","#00d2dd","#00d1d6","#00d0d0","#00cfc9","#00cdc3","#00ccbc","#00cbb5","#00caae","#00c9a7","#00c89f","#00c797","#00c68f","#00c586","#00c47d","#00c373","#00c268","#00c15c","#00c04e","#00bf3f","#00bd31","#00bb20","#04b901"]
    text_gradient = ["#ff0000","#f20001","#e50002","#d80003","#cb0003","#bf0004","#b20004","#a60004","#9a0003","#8e0002","#820000"]

    print_centre_colour_delay('                           @@@@@@@@@@@@@@@@@@@                             ',logo_globe_delay,world_gradient[0])
    print_centre_colour_delay('                       @@@@@@@              @@@@@@@                        ',logo_globe_delay,world_gradient[0])
    print_centre_colour_delay('                    @@@@@                        @@@@@                     ',logo_globe_delay,world_gradient[1])
    print_centre_colour_delay('                  @@@                               @@@@                   ',logo_globe_delay,world_gradient[1])
    print_centre_colour_delay('               @@@@                                    @@@                 ',logo_globe_delay,world_gradient[2])
    print_centre_colour_delay('              @@                                         @@@               ',logo_globe_delay,world_gradient[2])
    print_centre_colour_delay('            @@@                                            @@              ',logo_globe_delay,world_gradient[3])
    print_centre_colour_delay('           @@     @@@@                                   @@ @@@            ',logo_globe_delay,world_gradient[3])
    print_centre_colour_delay('          @@  @@@@@@                                      @@  @@           ',logo_globe_delay,world_gradient[4])
    print_centre_colour_delay('         @@ @@@@@                   @     @@@@             @@  @@          ',logo_globe_delay,world_gradient[4])
    print_centre_colour_delay('        @@ @@@@                    @             @@@@@@    @@@  @@         ',logo_globe_delay,world_gradient[5])
    print_centre_colour_delay('       @@ @@@@@                  @@@@@@@@@     @@@@@@@@ @@@@@@@  @@        ',logo_globe_delay,world_gradient[5])
    print_centre_colour_delay('      @@  @@@@                @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@ @@        ',logo_globe_delay,world_gradient[6])
    print_centre_colour_delay('      @@ @@                 @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@  @@       ',logo_globe_delay,world_gradient[6])
    print_centre_colour_delay('     @@ @@@                 @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@ @@       ',logo_globe_delay,world_gradient[7])
    print_centre_colour_delay('     @@  @@@@                @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@  @@      ',logo_globe_delay,world_gradient[7])
    print_centre_colour_delay('     @  @@@@@@@@@             @@@@@@@@@@@@@@@@@@@@@@@@@@@  @@@@@@@ @@      ',logo_globe_delay,world_gradient[8])
    print_centre_colour_delay('     @  @@@@@@@@@@@@             @@  @@@@@@@@@@@@@@@@@@@@@@@   @@@ @@      ',logo_globe_delay,world_gradient[8])
    print_centre_colour_delay('     @  @@@@@@@@@@@@@                 @@@@@@@@@@@@@@@@@@ @@   @@   @@      ',logo_globe_delay,world_gradient[9])
    print_centre_colour_delay('     @  @@@@@@@@@@@@@@@                @@@@@@@@@@@@@@@     @@@@@   @@      ',logo_globe_delay,world_gradient[9])
    print_centre_colour_delay('     @  @@@@@@@@@@@@@@@@               @@@@@@@@@@@@@@    @@ @@     @@      ',logo_globe_delay,world_gradient[10])
    print_centre_colour_delay('     @  @@@@@@@@@@@@@@                 @@@@@@@@@@@@@     @@        @@      ',logo_globe_delay,world_gradient[10])
    print_centre_colour_delay('     @@  @@@@@@@@@@@@                  @@@@@@@@@@@       @@@@@    @@@      ',logo_globe_delay,world_gradient[11])
    print_centre_colour_delay('      @  @@@@@@@@@@@         @ @        @@@@@@@@@@       @@@@@@@  @@       ',logo_globe_delay,world_gradient[11])
    print_centre_colour_delay('      @@  @@@@@@                         @@@@@@@@        @@@@@@@  @@       ',logo_globe_delay,world_gradient[12])
    print_centre_colour_delay('       @@ @@@@@                          @@@@@       @@  @@@@@@  @@        ',logo_globe_delay,world_gradient[12])
    print_centre_colour_delay('        @  @@@                                       @@     @   @@         ',logo_globe_delay,world_gradient[13])
    print_centre_colour_delay('        @@  @@                                                 @@          ',logo_globe_delay,world_gradient[13])
    print_centre_colour_delay('         @@  @@                                               @@           ',logo_globe_delay,world_gradient[14])
    print_centre_colour_delay('           @@  @                                             @@            ',logo_globe_delay,world_gradient[15])
    print_centre_colour_delay('            @@                                             @@@             ',logo_globe_delay,world_gradient[15])
    print_centre_colour_delay('             @@@                                          @@@              ',logo_globe_delay,world_gradient[16])
    print_centre_colour_delay('               @@@                                      @@@                ',logo_globe_delay,world_gradient[16])
    print_centre_colour_delay('                 @@@                                 @@@@                  ',logo_globe_delay,world_gradient[17])
    print_centre_colour_delay('                   @@@@    @@@@@@@   @@           @@@@@                    ',logo_globe_delay,world_gradient[18])
    print_centre_colour_delay('                      @@@@@@  @@@@@@@@@@@@@@  @@@@@@                       ',logo_globe_delay,world_gradient[18])
    print_centre_colour_delay('                         @@@@@@@@@@@@@@@@@@@@@@@@                          ',logo_globe_delay,world_gradient[19])
    print_centre_colour_delay('                                @@@@@@@@@@                                 ',logo_globe_delay,world_gradient[19])
    print(' ')
    print_centre_colour_delay(' ██████   ██████           ████   ███                                █████       ███████     █████████ (TM)',logo_text_delay,text_gradient[0])
    print_centre_colour_delay('░░██████ ██████           ░░███  ░░░                                ░░███      ███░░░░░███  ███░░░░░███    ',logo_text_delay,text_gradient[1])
    print_centre_colour_delay(' ░███░█████░███   ██████   ░███  ████   ███████  ██████  ████████   ███████   ███     ░░███░███    ░░░     ',logo_text_delay,text_gradient[2])
    print_centre_colour_delay(' ░███░░███ ░███  ░░░░░███  ░███ ░░███  ███░░███ ███░░███░░███░░███ ░░░███░   ░███      ░███░░█████████     ',logo_text_delay,text_gradient[3])
    print_centre_colour_delay(' ░███ ░░░  ░███   ███████  ░███  ░███ ░███ ░███░███████  ░███ ░███   ░███    ░███      ░███ ░░░░░░░░███    ',logo_text_delay,text_gradient[4])
    print_centre_colour_delay(' ░███      ░███  ███░░███  ░███  ░███ ░███ ░███░███░░░   ░███ ░███   ░███ ███░░███     ███  ███    ░███    ',logo_text_delay,text_gradient[5])
    print_centre_colour_delay(' █████     █████░░████████ █████ █████░░███████░░██████  ████ █████  ░░█████  ░░░███████░  ░░█████████     ',logo_text_delay,text_gradient[6])
    print_centre_colour_delay('░░░░░     ░░░░░  ░░░░░░░░ ░░░░░ ░░░░░  ░░░░░███ ░░░░░░  ░░░░ ░░░░░    ░░░░░     ░░░░░░░     ░░░░░░░░░      ',logo_text_delay,text_gradient[7])
    print_centre_colour_delay('                                       ███ ░███                                                            ',logo_text_delay,text_gradient[8])
    print_centre_colour_delay('                                      ░░██████                                                             ',logo_text_delay,text_gradient[9])
    print_centre_colour_delay('                                       ░░░░░░                                                              ',logo_text_delay,text_gradient[10])

    if debug:
        time.sleep(0.001)
    else:
        time.sleep(2)

    while True:
            try:
                Screen.wrapper(demo, catch_interrupt=True, arguments=[last_scene])
                sys.exit(0)
            except ResizeScreenError as e:
                last_scene = e.scene


intro()