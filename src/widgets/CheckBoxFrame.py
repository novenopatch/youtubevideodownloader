import customtkinter
from pytube import YouTube, Stream

from widgets.CheckBoxItem import CheckBoxItem


class CheckBoxFrame(customtkinter.CTkFrame):
    def __init__(self, master, item_list:list[tuple[YouTube,Stream]], command=None, **kwargs):
        super().__init__(master, **kwargs)
        self.command = command
        self.checkbox_list = []
        self.set_item_list(item_list)

    def add_item(self, youtube:YouTube,stream:Stream):
        item_checkbox = CheckBoxItem(self, youtube,stream)
        if self.command is not None:
            item_checkbox.configure_command(command=self.command)

        item_checkbox.grid(row=len(self.checkbox_list), column=0, pady=(0, 10))
        #button = customtkinter.CTkButton(item_frame, image=my_image,fg_color="transparent",text="")
        self.checkbox_list.append( item_checkbox)

    def set_item_list(self,item_list:list[tuple[YouTube,Stream]]):
        for youtube, stream_choice in item_list:
            self.add_item(youtube,stream_choice)

    def get_checked_items(self):
        return [( checkbox.youtube,checkbox.stream ) for checkbox in self.checkbox_list if checkbox.is_checked()]