import tkinter as tk

import BasicPage

page1rely = 0

window = tk.Tk()
window.title("YTMediaTool")
lbl = tk.Label(window, text="YTMediaTool")
window.geometry('600x400')
window.configure(bg='gray')

page1frame = BasicPage.createFrame(window)

def page1():
    BasicPage.showPage()

def page2():
    toggle_button("Vaihtoehto 2")
    BasicPage.hidePage()

def page3():
    toggle_button("Vaihtoehto 3")
    BasicPage.hidePage()

def toggle_button(selected):
    current_value.set(selected)

current_value = tk.StringVar(value="None")

button1 = tk.Radiobutton(
    window,
    text="Basic",
    value="Vaihtoehto 1",
    variable=current_value,
    indicatoron=False,
    width=15,
    command=page1,
)
button1.place(x=5, y=5)


button2 = tk.Radiobutton(
    window,
    text="SMLD",
    value="Vaihtoehto 2",
    variable=current_value,
    indicatoron=False,
    width=15,
    command=page2,
)
button2.place(x=155, y=5)


button3 = tk.Radiobutton(
    window,
    text="About",
    value="Vaihtoehto 3",
    variable=current_value,
    indicatoron=False,
    width=15,
    command=page3,
)
button3.place(x=305, y=5)

def quit():
    window.destroy

window.mainloop()
quit()





