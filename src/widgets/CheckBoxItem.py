import tkinter

import customtkinter
import requests
from pytube import YouTube, Stream
from io import BytesIO
from PIL import Image



class CheckBoxItem(customtkinter.CTkFrame):
    def __init__(self, master,youtube:YouTube,stream:Stream,  **kwargs):
        super().__init__(master, **kwargs)
        self.youtube = youtube
        self.title = f"{youtube.title}-{stream.resolution}({stream.fps}-{stream.mime_type})-({(stream.filesize_approx /1024 /1024):.2f}/Mb)"
        self.stream = stream
        self.checked = tkinter.BooleanVar()
        self.checked.set(False)
        response = requests.get(youtube.thumbnail_url)
        #response = requests.get("https://images.unsplash.com/photo-1611746872915-64382b5c76da?ixlib=rb-4.0.3&ixid=MnwxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8&auto=format&fit=crop&w=870&q=80")
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
