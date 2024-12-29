import tkinter as tk
from tkinter import filedialog
import subprocess
import os
from sys import platform



def createFrame(window):
	global frame
	frame = tk.Frame(window, width=600, height=380)

	global showPage, hidePage
	def hidePage():
		frame.place_forget()
	def showPage():
		frame.place(y=34)








