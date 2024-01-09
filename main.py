from Stock_Information import StockGrapher
import matplotlib.pyplot as plt
import tkinter as tk
import customtkinter
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import json
import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageTk, ImageOps
import datetime as dt
import os
base_dir = os.path.dirname(__file__)
customtkinter.set_default_color_theme(os.path.join(base_dir, 'Theme.json'))
customtkinter.set_appearance_mode("light")

class App(customtkinter.CTk):
    def GenerateGraph(self):
        if hasattr(self, 'canvas'):
            self.canvas.get_tk_widget().destroy()
        if hasattr(self, 'sidebar_frameTitle_dailychange'):
            self.sidebar_frameTitle_dailychange.destroy()
        fig, ax = plt.subplots(figsize=(10,7))
        stocks = self.Stocks.get()
        start = self.Start.get()
        end = self.End.get()
        data = StockGrapher(stocks, start, end)
        self.percent_change = data[1]
        data = data[0]
        data.plot(ax=ax,color=["#2CC985", "green", "red","orange"]) # ,marker='o', markersize=2
        ax.fill_between(x=data.index, y1=data.values,color="lightgreen", alpha=0.2, y2=(data.min()-(data.mean()-data.min())))
        ax.set_facecolor("white")
        fig.patch.set_facecolor("white")
        ax.set_title(f"{stocks} stock: {start}-{end}")
        ax.tick_params(labelsize=6, colors="black")
        self.canvas = FigureCanvasTkAgg(fig, master=self)
        self.canvas.get_tk_widget().grid(row=0, column=4, rowspan=3) # , rowspan=2
        self.sidebar_frameTitle_dailychange = customtkinter.CTkLabel(self.sidebar_frame_Stockinfo, text=f"Current Price: ${round(data.iloc[-1],2)}\n"
                                                                                                        f"Daily Change: {self.percent_change}%",
                                                          font=("Helvetica", 16), bg_color="#E1F6DD")
        self.sidebar_frameTitle_dailychange.grid(row=1, column = 0, padx=(30,0), sticky="nsw")

    def favouritesButton (self):
        with open(os.path.join(base_dir,"Hey.json"), "r") as file:
            favourites = json.load(file)
            self.favorite_buttons = []
            for i, stock in enumerate(favourites):
                self.stock = customtkinter.CTkButton(master=self.scrollable_frame, text=f"{stock}".upper(), corner_radius=0,fg_color="gray86",text_color="white",
                                                 command=lambda s=stock: self.ChangeStock(s))
                self.stock.grid(row=(i+4), column=0, pady = 5,sticky="ew")
                self.favorite_buttons.append(self.stock)

    def addFavourite(self):
        add = self.Stocks.get().upper()
        with open(os.path.join(base_dir,"Hey.json"), "r+") as file:
            favourites = json.load(file)
            if add not in favourites:
                favourites.append(add)
                file.seek(0)
                json.dump(favourites, file)
                file.truncate()
        self.favouritesButton()

    def removeFavourite(self):
        for button in self.favorite_buttons:
            button.destroy()
        self.favorite_buttons = []
        remove = self.Stocks.get()
        with open(os.path.join(base_dir,"Hey.json"), "r+") as file:
            favourites = json.load(file)
            if remove in favourites:
                favourites.remove(remove)
                file.seek(0)
                json.dump(favourites, file)
                file.truncate()

        self.favouritesButton()

    def ChangeStock(self, stockbutton):
        self.Stocks.delete(0, 'end')
        self.Stocks.insert(0,stockbutton.upper())
        if self.Start.get() == "":
            self.Start.set("01/01/2023") # Make this today's date - 60 days
        if self.End.get() == "":
            self.End.set(dt.datetime.now().strftime("%d/%m/%Y")) # Make this today's date
        self.GenerateGraph()

    def userImage(self, imagePath):
        self.source_image = Image.open(imagePath)
        self.source_image = self.source_image.resize((100, 100), reducing_gap=3.0, resample=Image.LANCZOS) # , reducing_gap=3.0, resample=Image.LANCZOS
        self.size = self.source_image.size
        self.circular_image = Image.new('RGBA', self.size, (0, 0, 0, 0))
        H, V = 50,50
        S = 49
        mask = np.zeros(self.size, dtype=np.uint8)
        cv2.circle(mask, (H, V), S, 255, -1, lineType=cv2.LINE_AA)
        mask_pil = Image.fromarray(mask)
        self.circular_image.paste(self.source_image, (0, 0), mask_pil)
        self.img = self.circular_image
        self.new_img = ImageTk.PhotoImage(self.img)
        self.my_label_user_image = tk.Label(self.sidebar_frame, image=self.new_img,bg="gray86")
        self.my_label_user_image.grid(row=1, column=0, pady=(5,10), sticky="ew")
        self.label_user = tk.Label(self.sidebar_frame,text="Luke Carroll",bg="gray86",font=("Helvetica bold",18))
        self.label_user.grid(row=0,column=0,pady=(10,0), sticky="we")


    def __init__(self):
        super().__init__()
        window_height = self.winfo_screenheight()*0.75
        window_width = self.winfo_screenwidth()*0.75
        self.title("Cali rox!")
        x_cordinate = abs((window_width / 2) - (self.winfo_screenwidth() / 2))
        y_cordinate = abs((window_height / 2) - (self.winfo_screenheight() / 2))
        self.geometry("%dx%d+%d+%d" % (window_width, window_height,x_cordinate, y_cordinate))
        self.grid_columnconfigure(4, weight=1)
        self.grid_columnconfigure([ 1, 2, 3], weight=0)
        self.grid_rowconfigure([0,1,2], weight=1)
        self.grid_rowconfigure(3, minsize=200)

        self.sidebar_frame_StockForm = customtkinter.CTkFrame(self, corner_radius=20,fg_color="#E1F6DD")
        self.sidebar_frame_StockForm.grid(row=0, column=1, rowspan=3, columnspan = 2, sticky="nsew", padx=20, pady=(20,10))
        self.sidebar_frame_StockForm.grid_rowconfigure([0, 1, 2, 3], weight=1)

        self.labelText = tk.StringVar()
        self.labelText.set(f"Enter stocks here \n(seperated by column: \nstock1, stock2, etc...): ")
        self.labelDir = customtkinter.CTkLabel(self.sidebar_frame_StockForm, textvariable=self.labelText)
        self.labelDir.grid(row=0, column=1,padx=(10,5),pady=10,sticky="e")

        self.Stocks = tk.StringVar()
        self.Stocks = customtkinter.CTkEntry(self.sidebar_frame_StockForm, textvariable=self.Stocks)
        # Make it so that you can submit one at a time and each entry gets held in a waiting zone until submit button is pressed
        self.Stocks.grid(row=0, column=2,padx=(5,10),pady=10)

        self.labelText1 = tk.StringVar()
        self.labelText1.set(f"Enter start date \n(dd/MM/yyyy): ")
        self.labelDir1 = customtkinter.CTkLabel(self.sidebar_frame_StockForm, textvariable=self.labelText1)
        self.labelDir1.grid(row=1, column=1,padx=(10,5),pady=10,sticky="e")

        self.Start = tk.StringVar()
        self.StartDate_Input = customtkinter.CTkEntry(self.sidebar_frame_StockForm, textvariable=self.Start)
        self.StartDate_Input.grid(row=1, column=2,padx=(5,10),pady=10)

        self.labelText2 = tk.StringVar()
        self.labelText2.set(f"Enter end date \n(dd/MM/yyyy): ")
        self.labelDir2 = customtkinter.CTkLabel(self.sidebar_frame_StockForm, textvariable=self.labelText2)
        self.labelDir2.grid(row=2, column=1, padx=(10,5),pady=10,sticky="e")

        self.End = tk.StringVar()
        self.EndDate_Input = customtkinter.CTkEntry(self.sidebar_frame_StockForm, textvariable=self.End)
        self.EndDate_Input.grid(row=2, column=2,padx=(5,10),pady=10)

        self.sidebar_frame_Stockinfo = customtkinter.CTkFrame(self, corner_radius=20,fg_color="#E1F6DD")
        self.sidebar_frame_Stockinfo.grid(row=3, column=1, columnspan = 4,sticky="nsew", padx=20, pady=(10,20)) # rowspan=2, sticky="nsew"

        self.sidebar_frameTitle2 = customtkinter.CTkLabel(self.sidebar_frame_Stockinfo, text="Stock Information",
                                                         font=("Helvetica", 24, "bold"), bg_color="#E1F6DD")
        self.sidebar_frameTitle2.grid(row=0, pady=15, padx=30)


        self.sub_btn = customtkinter.CTkButton(self.sidebar_frame_StockForm, text='Submit', command=self.GenerateGraph)
        self.sub_btn.grid(row=3, column=1, pady=10,padx=10,columnspan = 2,sticky="ew")

        # ADD SCROLLABLE FRAME TO THE SIDEBAR TO KEEP THE FAVOURITES IN. MAKE IT HAVE A ROWSPAN = 2 OR 3?
        self.sidebar_frame = customtkinter.CTkFrame(self,corner_radius=0) #fg_color="lightgreen"
        self.sidebar_frame.grid(row=0, column=0, rowspan=4,sticky="nsew")
        self.sidebar_frame.grid_columnconfigure(0, weight=0)

        self.separator = customtkinter.CTkFrame(self.sidebar_frame,fg_color="gray50", height=3,corner_radius=20)
        self.separator.grid(row=2,column=0, padx=10,sticky="ew")

        self.scrollable_frame = customtkinter.CTkScrollableFrame(self.sidebar_frame)
        self.scrollable_frame.grid(row=4, column=0, padx=10, sticky="nsew")
        self.scrollable_frame.grid_columnconfigure(0, weight=1)

        self.sidebar_frameTitle = customtkinter.CTkLabel(self.sidebar_frame,text="Favourites",font=("Helvetica",24,"bold"),bg_color="gray86")
        self.sidebar_frameTitle.grid(row=3,pady=15,padx=30)

        self.sidebar_frameBUT = customtkinter.CTkFrame(self, corner_radius=0)  # fg_color="lightgreen"
        self.sidebar_frameBUT.grid(row=3, column=0, sticky="nsew")
        self.sidebar_frameBUT.grid_columnconfigure(0, weight=1)

        self.favouritesButton()

        self.sub_btnFav = customtkinter.CTkButton(self.sidebar_frameBUT, text='Favourite', command=self.addFavourite)
        self.sub_btnFav.pack(side = "bottom", pady = 10, padx = 10, fill="x")

        self.sub_btnUnFav = customtkinter.CTkButton(self.sidebar_frameBUT, text='Unfavourite', command=self.removeFavourite)
        self.sub_btnUnFav.pack(side="bottom", pady=10, padx=10, fill="x")

        self.userImage(os.path.join(base_dir,"IMG_0510.JPG"))

if __name__ == "__main__":
    app = App()
    app.mainloop()