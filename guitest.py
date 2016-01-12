import tkinter
import tkinter.ttk

root = tkinter.Tk()

class Main(tkinter.ttk.Frame):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        self.label = tkinter.ttk.Label(self, text="Test")
        
if __name__ == "__main__":
    main = Main(root)
    root.mainloop()