import tkinter

import customtkinter
from PIL import Image
import requests
from io import BytesIO
import os

from pytube import Stream, YouTube

from main import YTDown
from save import Save


class CheckBoxItem(customtkinter.CTkFrame):
    def __init__(self, master,youtube:YouTube,stream:Stream,  **kwargs):
        super().__init__(master, **kwargs)
        self.youtube = youtube
        self.title = youtube.title
        self.stream = stream
        self.checked = tkinter.BooleanVar()
        self.checked.set(False)
        response = requests.get(youtube.thumbnail_url)
        image_data = response.content
        my_image = customtkinter.CTkImage(light_image=Image.open(BytesIO(image_data)),
                                          dark_image=Image.open(BytesIO(image_data)),
                                          size=(90, 90))
        self.button = customtkinter.CTkLabel(self, image=my_image,text="")
        self.checkbox = customtkinter.CTkCheckBox(self, text=self.title,variable=self.checked)
        self.button.pack(side="left", padx=5)
        self.checkbox.pack(side="left", padx=5)
    def configure_command(self, command):
        self.checkbox.configure(command=command)
        #self.button.configure(command=command)

    def is_checked(self):
        return self.checked.get()
    def get_title(self):
        return self.title


class CheckBoxFrame(customtkinter.CTkFrame):
    def __init__(self, master, item_list:list[(YouTube,Stream)], command=None, **kwargs):
        super().__init__(master, **kwargs)
        self.command = command
        self.checkbox_list = []
        for youtube, stream_choice in item_list:
            self.add_item(youtube,stream_choice)

    def add_item(self, youtube:YouTube,stream:Stream):
        item_checkbox = CheckBoxItem(self, youtube,stream)
        if self.command is not None:
            item_checkbox.configure_command(command=self.command)

        item_checkbox.grid(row=len(self.checkbox_list), column=0, pady=(0, 10))
        #button = customtkinter.CTkButton(item_frame, image=my_image,fg_color="transparent",text="")
        self.checkbox_list.append( item_checkbox)



    def get_checked_items(self):
        return [( checkbox.youtube,checkbox.stream ) for checkbox in self.checkbox_list if checkbox.is_checked()]


class App(customtkinter.CTk):
    def __init__(self,save: Save):
        self.save = save
        super().__init__()

        self.title("YDOWN.py")
        self.geometry("720x480")


        self.navigation_frame = customtkinter.CTkFrame(self, corner_radius=0)

        self.home_frame = customtkinter.CTkScrollableFrame(self, corner_radius=0, fg_color="transparent")

        self.downloads_frame = customtkinter.CTkFrame(self, corner_radius=0, fg_color="transparent")

        self.home_button = customtkinter.CTkButton(self.navigation_frame, corner_radius=0, height=40, border_spacing=10,
                                                   text="Home",
                                                   fg_color="transparent", text_color=("gray10", "gray90"),
                                                   hover_color=("gray70", "gray30"),
                                                   anchor="w", command=self.home_button_event)
        self.downloads_button = customtkinter.CTkButton(self.navigation_frame, corner_radius=0, height=40,
                                                        border_spacing=10,
                                                        text="Downloads",
                                                        fg_color="transparent", text_color=("gray10", "gray90"),
                                                        hover_color=("gray70", "gray30"),
                                                        anchor="w", command=self.downloads_button_event)

        self.appearance_mode_menu = customtkinter.CTkOptionMenu(self.navigation_frame,
                                                                values=["Light", "Dark", "System"],
                                                                command=self.change_appearance_mode_event)

        self.progressbar = customtkinter.CTkProgressBar(self.home_frame)



        self.download_button = customtkinter.CTkButton(self.home_frame, corner_radius=0, height=40,
                                                       border_spacing=10,
                                                       text="Download",
                                                       fg_color="#f44336", text_color=("#fffff", "#ffffff"),
                                                       hover_color=("#ba000d", "#ff7961"),
                                                       command=self.downloads_button_event)

        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)

        self.navigation_frame.grid(row=0, column=0, sticky="nsew")
        self.navigation_frame.grid_rowconfigure(3, weight=1)
        self.home_frame.grid_columnconfigure(0, weight=1, )
        self.downloads_frame.grid_columnconfigure(0, weight=1)
        self.home_button.grid(row=1, column=0, sticky="ew")
        self.downloads_button.grid(row=2, column=0, sticky="ew")
        self.appearance_mode_menu.grid(row=6, column=0, padx=20, pady=20, sticky="s")
        self.progressbar.grid(row=1, column=0, padx=20, pady=10)

        self.download_button.grid(row=5, padx=(20, 20), pady=(20, 0), )


        self.add_input_frame()
        self.add_radio_button()
        self.add_option_frame()
        #self.add_choice_frame()
        self.home_frame.grid(row=0, column=1, sticky="nsew", padx=20, pady=20)



    def add_input_frame(self):
        self.video_or_playlist_var = tkinter.IntVar(value=0)
        self.url_input_frame = customtkinter.CTkFrame(self.home_frame)
        self.url_var = customtkinter.StringVar(value="")
        self.entry_url = customtkinter.CTkEntry(
            self.url_input_frame, placeholder_text="Past url",
            textvariable=self.url_var,
        )
        self.output_var = customtkinter.StringVar(value=f"{os.getcwd()}/downloads/")
        self.entry_output = customtkinter.CTkEntry(self.url_input_frame, placeholder_text="Output",
                                                   textvariable=self.output_var)
        self.label_output = customtkinter.CTkLabel(self.url_input_frame, text="Folder")
        self.url_input_frame.grid(row=2, column=0, padx=(20, 20), pady=(20, 0), sticky="nsew")
        self.url_input_frame.grid_rowconfigure(0, weight=1)
        self.url_input_frame.grid_columnconfigure(3, weight=1)
        self.label_url = customtkinter.CTkLabel(self.url_input_frame, text="url:")
        self.label_url.grid(row=0, column=0, padx=10, pady=10)
        self.entry_url.grid(row=0, column=2, columnspan=2, padx=10, pady=10, sticky="nsew")
        self.label_output.grid(row=1, column=0, padx=10, pady=10)
        self.entry_output.grid(row=1, column=2, columnspan=2, padx=10, pady=10, sticky="nsew")
    def add_radio_button(self):
        self.radiobutton_frame = customtkinter.CTkFrame(self.home_frame)
        self.label_radio_group = customtkinter.CTkLabel(master=self.radiobutton_frame, text="Choice type")
        self.radio_button_1 = customtkinter.CTkRadioButton(master=self.radiobutton_frame,
                                                           variable=self.video_or_playlist_var,
                                                           value=0, text="Video",
                                                           command=self.video_or_playlist_radio_group_event)
        self.radio_button_2 = customtkinter.CTkRadioButton(master=self.radiobutton_frame,
                                                           variable=self.video_or_playlist_var,
                                                           value=1, text="Playlist",
                                                           command=self.video_or_playlist_radio_group_event)
        self.label_radio_group.grid(row=0, column=1, columnspan=1, padx=10, pady=10, sticky="")
        self.radio_button_1.grid(row=0, column=2, pady=10, padx=20, sticky="n")
        self.radio_button_2.grid(row=0, column=3, pady=10, padx=20, sticky="n")
        self.radiobutton_frame.grid(row=3, column=0, padx=(20, 20), pady=(20, 0), sticky="nsew")

    def add_option_frame(self):

        self.option_frame = customtkinter.CTkFrame(self.home_frame)
        self.option_frame.grid(row=4, column=0, padx=(20, 20), pady=(20, 0), sticky="nsew")
        self.option_frame.grid_rowconfigure(1, weight=1)
        self.option_frame.grid_columnconfigure(5, weight=1)
        self.label_resolution = customtkinter.CTkLabel(self.option_frame, text="resolution:")
        self.label_type = customtkinter.CTkLabel(self.option_frame, text="type:")
        self.audio_or_video_var = customtkinter.StringVar(value="audio")
        self.switch = customtkinter.CTkSwitch(master=self.option_frame,
                                              text="audio",
                                              command=self.audio_or_video_switch_event, variable=self.audio_or_video_var, onvalue="audio",
                                              offvalue="video")
        self.resolution_var =  customtkinter.StringVar(value="720p")
        self.combobox_2 = customtkinter.CTkOptionMenu(master=self.option_frame,
                                                      values=["144p", "240p", "360p", "480p", "720p", "1080p"],
                                                      command=self.optionmenu_callback,variable=self.resolution_var)
        self.label_type.grid(row=1, column=1, padx=5, pady=5)
        self.switch.grid(row=1, column=2, padx=5, pady=5)
        self.label_resolution.grid(row=1, column=3, padx=5, pady=5)
        self.combobox_2.grid(row=1, column=4, padx=5, pady=5)
    def add_choice_frame(self):
        yt_down = YTDown(self.save,True)
        self.checkbox_frame = CheckBoxFrame(master=self.home_frame,
                                                                 command=self.checkbox_frame_event,
                                                                 item_list=[f"item {i}" for i in range(10)])
        self.checkbox_frame.grid(row=6, column=0, padx=10, pady=10, sticky="nsew")
        self.checkbox_frame.add_item("new item")

    def optionmenu_callback(self,choice):
        print("optionmenu dropdown clicked:", choice)

    def select_frame_by_name(self, name):
        # set button color for selected button
        self.home_button.configure(fg_color=("gray75", "gray25") if name == "home" else "transparent")
        self.downloads_button.configure(fg_color=("gray75", "gray25") if name == "frame_2" else "transparent")

        # show selected frame
        if name == "home":
            self.home_frame.grid(row=0, column=1, sticky="nsew")
        else:
            self.home_frame.grid_forget()
        if name == "frame_2":
            self.downloads_frame.grid(row=0, column=1, sticky="nsew")
        else:
            self.downloads_frame.grid_forget()

    def change_appearance_mode_event(self, new_appearance_mode):
        customtkinter.set_appearance_mode(new_appearance_mode)

    def get_url_input_text(self)->str:
        return self.url_var.get()
    def home_button_event(self):
        self.select_frame_by_name("home")
        print("home")

    def downloads_button_event(self):
        #self.select_frame_by_name("downloads")
        print(
            f"url:{self.get_url_input_text()},folder:{self.output_var.get()},resolution:{self.resolution_var.get()},audio or video:{self.audio_or_video_var.get()},no:{self.video_or_playlist_var.get()}"

        )

    def checkbox_frame_event(self):
        print(f"checkbox frame modified: {self.checkbox_frame.get_checked_items()}")

    def audio_or_video_switch_event(self):
        self.switch.configure(text=self.audio_or_video_var.get())
        print("switch toggled, current value:", self.audio_or_video_var.get())
    def video_or_playlist_radio_group_event(self):
        print(f"type:{self.video_or_playlist_var.get()}")


if __name__ == "__main__":
    app = App(Save())
    app.mainloop()
