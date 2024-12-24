import wx
import wx.svg
from wx import adv
import time
import threading
from playsound import playsound
import os


VERSION= "v0.2.0"
def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)


class SettingsDialog(wx.Dialog):
    def __init__(self, parent):
        super().__init__(parent, title="Settings", size=(300, 250))
        self.SetIcon(wx.Icon(resource_path("tomato.ico")))
        self.parent = parent
        
        panel = wx.Panel(self)
        vbox = wx.BoxSizer(wx.VERTICAL)
        
        self.work = wx.SpinCtrl(panel, value="25", min=1, max=60)
        self.short_break = wx.SpinCtrl(panel, value="5", min=1, max=30)
        self.long_break = wx.SpinCtrl(panel, value="15", min=1, max=60)
        self.cycles = wx.SpinCtrl(panel, value="4", min=1, max=10)
        
        grid = wx.FlexGridSizer(4, 2, 10, 10)
        grid.Add(wx.StaticText(panel, label="Work (minutes):"))
        grid.Add(self.work)
        grid.Add(wx.StaticText(panel, label="Short Break (minutes):"))
        grid.Add(self.short_break)
        grid.Add(wx.StaticText(panel, label="Long Break (minutes):"))
        grid.Add(self.long_break)
        grid.Add(wx.StaticText(panel, label="Cycles before Long Break:"))
        grid.Add(self.cycles)
        
        vbox.Add(grid, proportion=1, flag=wx.ALL|wx.EXPAND, border=10)
        
        buttons = wx.BoxSizer(wx.HORIZONTAL)
        ok_button = wx.Button(panel, wx.ID_OK, "OK")
        cancel_button = wx.Button(panel, wx.ID_CANCEL, "Cancel")
        buttons.Add(ok_button)
        buttons.Add(cancel_button, flag=wx.LEFT, border=5)
        
        vbox.Add(buttons, flag=wx.ALIGN_CENTER|wx.ALL, border=10)
        
        panel.SetSizer(vbox)

class PomodoroFrame(wx.Frame):
    def __init__(self):
        super().__init__(parent=None, title='Pomodoro', 
                        size=(400, 200),
                        style=wx.DEFAULT_FRAME_STYLE | wx.STAY_ON_TOP)
        self.SetIcon(wx.Icon(resource_path("tomato.ico")))
        self.svg_icons = {
            'play': '''<?xml version="1.0" encoding="UTF-8"?>
                <svg width="24" height="24" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                    <path d="M8 5v14l11-7z"/>
                </svg>''',
            'pause': '''<?xml version="1.0" encoding="UTF-8"?>
                <svg width="24" height="24" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                    <path d="M6 19h4V5H6v14zm8-14v14h4V5h-4z"/>
                </svg>''',
            'forward': '''<?xml version="1.0" encoding="UTF-8"?>
                <svg width="24" height="24" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                    <path d="M6 18l8.5-6L6 6v12zM16 6v12h2V6h-2z"/>
                </svg>''',
            'reset': '''<?xml version="1.0" encoding="UTF-8"?>
                <svg width="24" height="24" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                    <path d="M12 5V1L7 6l5 5V7c3.31 0 6 2.69 6 6s-2.69 6-6 6-6-2.69-6-6H4c0 4.42 3.58 8 8 8s8-3.58 8-8-3.58-8-8-8z"/>
                </svg>''',
            'reset_all': '''<?xml version="1.0" encoding="UTF-8"?>
                <svg width="16" height="16" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                    <path d="M12 6v3l4-4-4-4v3c-4.42 0-8 3.58-8 8 0 1.57.46 3.03 1.24 4.26L6.7 14.8c-.45-.83-.7-1.79-.7-2.8 0-3.31 2.69-6 6-6zm6.76 1.74L17.3 9.2c.44.84.7 1.79.7 2.8 0 3.31-2.69 6-6 6v-3l-4 4 4 4v-3c4.42 0 8-3.58 8-8 0-1.57-.46-3.03-1.24-4.26z"/>
                </svg>''',
            'settings': '''<?xml version="1.0" encoding="UTF-8"?>
                <svg width="24" height="24" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                    <path d="M19.14 12.94c.04-.3.06-.61.06-.94 0-.32-.02-.64-.07-.94l2.03-1.58c.18-.14.23-.41.12-.61l-1.92-3.32c-.12-.22-.37-.29-.59-.22l-2.39.96c-.5-.38-1.03-.7-1.62-.94l-.36-2.54c-.04-.24-.24-.41-.48-.41h-3.84c-.24 0-.43.17-.47.41l-.36 2.54c-.59.24-1.13.57-1.62.94l-2.39-.96c-.22-.08-.47 0-.59.22L2.74 8.87c-.12.21-.08.47.12.61l2.03 1.58c-.05.3-.07.62-.07.94s.02.64.07.94l-2.03 1.58c-.18.14-.23.41-.12.61l1.92 3.32c.12.22.37.29.59.22l2.39-.96c.5.38 1.03.7 1.62.94l.36 2.54c.05.24.24.41.48.41h3.84c.24 0 .44-.17.47-.41l.36-2.54c.59-.24 1.13-.56 1.62-.94l2.39.96c.22.08.47 0 .59-.22l1.92-3.32c.12-.22.07-.47-.12-.61l-2.01-1.58zM12 15.6c-1.98 0-3.6-1.62-3.6-3.6s1.62-3.6 3.6-3.6 3.6 1.62 3.6 3.6-1.62 3.6-3.6 3.6z"/>
                </svg>'''
        }
        self.init_ui()
        self.init_timer()

        self.sound_work = resource_path("alarm.wav")  # Sound for work period
        self.sound_break =  resource_path("alarm.wav")  # Sound for break period

    def load_svg(self, svg_string, size=(24, 24)):
        """Convert SVG string to wx.Bitmap"""
        svg_image = wx.svg.SVGimage.CreateFromBytes(svg_string.encode())
        return svg_image.ConvertToScaledBitmap(wx.Size(*size), self)

    def init_ui(self):
        panel = wx.Panel(self)
        vbox = wx.BoxSizer(wx.VERTICAL)
        
        # Settings
        self.work_time = 25
        self.short_break = 5
        self.long_break = 15
        self.cycles = 4
        
        # Status variables
        self.current_cycle = 1
        self.is_work = True
        self.time_left = self.work_time * 60
        self.is_running = False
        
        # Create status label
        self.status_label = wx.StaticText(panel, label=self.get_status_text())
        vbox.Add(self.status_label, flag=wx.ALIGN_CENTER|wx.ALL, border=10)
        
        # Create timer label
        self.timer_label = wx.StaticText(panel, label=self.format_time(self.time_left))
        font = wx.Font(32, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD)
        self.timer_label.SetFont(font)
        vbox.Add(self.timer_label, flag=wx.ALIGN_CENTER|wx.ALL, border=10)
        
        hbox = wx.BoxSizer(wx.HORIZONTAL)
        
        self.play_button = wx.BitmapButton(
            panel,
            bitmap=self.load_svg(self.svg_icons['play']),
            size=(32, 32)
        )
        self.next_button = wx.BitmapButton(
            panel,
            bitmap=self.load_svg(self.svg_icons['forward']),
            size=(32,32)
        )
        self.reset_button = wx.BitmapButton(
            panel,
            bitmap=self.load_svg(self.svg_icons['reset']),
            size=(32, 32)
        )
        self.reset_all_button = wx.BitmapButton(
            panel,
            bitmap=self.load_svg(self.svg_icons['reset_all']),
            size=(32, 32)
        )
        self.settings_button = wx.BitmapButton(
            panel,
            bitmap=self.load_svg(self.svg_icons['settings']),
            size=(32, 32)
        )
        
        icon_file = wx.Image(resource_path("tomato.ico"), wx.BITMAP_TYPE_ICO)
        icon_file.Rescale(24, 24, wx.IMAGE_QUALITY_HIGH)
        bitmap = wx.Bitmap(icon_file)
        self.about_button = wx.BitmapButton(panel, bitmap=bitmap, size=(32, 32))    

        hbox.Add(self.play_button, flag=wx.LEFT|wx.RIGHT, border=2)  # Smaller border
        hbox.Add(self.next_button, flag=wx.LEFT|wx.RIGHT, border=2)
        hbox.Add(self.reset_button, flag=wx.LEFT|wx.RIGHT, border=2)
        hbox.Add(self.reset_all_button, flag=wx.LEFT|wx.RIGHT, border=2)
        hbox.Add(self.settings_button, flag=wx.LEFT|wx.RIGHT, border=2)
        hbox.Add(self.about_button, flag=wx.LEFT|wx.RIGHT, border=2)
    
        
        vbox.Add(hbox, flag=wx.ALIGN_CENTER|wx.ALL, border=2)
        
        # Add tooltips
        self.play_button.SetToolTip("Play/Pause")
        self.next_button.SetToolTip("Next Period")
        self.reset_button.SetToolTip("Reset Current Period")
        self.settings_button.SetToolTip("Settings")
        self.reset_all_button.SetToolTip("Reset All Cycles")
        self.about_button.SetToolTip("About")
        
        # Bind events
        self.play_button.Bind(wx.EVT_BUTTON, self.on_play)
        self.next_button.Bind(wx.EVT_BUTTON, self.on_next)
        self.reset_button.Bind(wx.EVT_BUTTON, self.on_reset)
        self.reset_all_button.Bind(wx.EVT_BUTTON, self.on_reset_all)
        self.settings_button.Bind(wx.EVT_BUTTON, self.on_settings)
        self.about_button.Bind(wx.EVT_BUTTON, self.on_about)
        
        panel.SetSizer(vbox)
    
    def init_timer(self):
        self.timer_thread = None
    
    def on_about(self, event):
        info = adv.AboutDialogInfo()
        info.SetName("Pomodoro Timer")
        info.SetVersion(VERSION)
        info.SetCopyright("Created by Sorin Savu")
        info.SetWebSite("https://github.com/sorin25/pomodoro")
        info.SetDescription("A simple Pomodoro timer application")
    
        adv.AboutBox(info)

    def get_status_text(self):
        if self.is_work:
            return f"Work Period - Cycle {self.current_cycle}/{self.cycles}"
        else:
            break_type = "Long" if self.current_cycle >= self.cycles else "Short"
            return f"{break_type} Break - Cycle {self.current_cycle}/{self.cycles}"
    
    def format_time(self, seconds):
        minutes = seconds // 60
        seconds = seconds % 60
        return f"{minutes:02d}:{seconds:02d}"
    
    def play_sound(self):
        try:
            sound_file = self.sound_work if not self.is_work else self.sound_break
            if os.path.exists(sound_file):
                threading.Thread(target=playsound, args=(sound_file,)).start()
            else:
                print(f"Warning: Sound file {sound_file} not found")
        except Exception as e:
            print(f"Error playing sound: {e}")
    
    def timer_function(self):
        while self.is_running and self.time_left > 0:
            time.sleep(1)
            self.time_left -= 1
            wx.CallAfter(self.update_display)
            
        if self.time_left <= 0:
            wx.CallAfter(self.play_sound)
            wx.CallAfter(self.on_next)
    
    def update_display(self):
        self.timer_label.SetLabel(self.format_time(self.time_left))
        self.status_label.SetLabel(self.get_status_text())
    
    def on_play(self, event):
        if not self.is_running:
            self.is_running = True
            self.play_button.SetBitmap(self.load_svg(self.svg_icons['pause']))
            self.timer_thread = threading.Thread(target=self.timer_function)
            self.timer_thread.start()
        else:
            self.is_running = False
            self.play_button.SetBitmap(self.load_svg(self.svg_icons['play']))
            if self.timer_thread:
                self.timer_thread.join()
    def on_reset_all(self, event):
        self.is_running = False
        if self.timer_thread:
            self.timer_thread.join()
        
        self.current_cycle = 1
        self.is_work = True
        self.time_left = self.work_time * 60
        self.update_display()
        # Reset play button to play icon
        self.play_button.SetBitmap(self.load_svg(self.svg_icons['play']))
    
   
    def on_next(self, event=None):
        self.is_running = False
        if self.timer_thread:
            self.timer_thread.join()
        
        if self.is_work:
            self.is_work = False
            if self.current_cycle >= self.cycles:
                self.time_left = self.long_break * 60
            else:
                self.time_left = self.short_break * 60
        else:
            self.is_work = True
            if not self.current_cycle >= self.cycles:
                self.current_cycle += 1
            else:
                self.current_cycle = 1
            self.time_left = self.work_time * 60

        self.play_button.SetBitmap(self.load_svg(self.svg_icons['play']))
        self.update_display()
    
    def on_reset(self, event):
        self.is_running = False
        if self.timer_thread:
            self.timer_thread.join()
        
        if self.is_work:
            self.time_left = self.work_time * 60
        else:
            self.time_left = self.short_break * 60 if self.current_cycle < self.cycles else self.long_break * 60
        self.play_button.SetBitmap(self.load_svg(self.svg_icons['play']))       
        self.update_display()
    
    def on_settings(self, event):
        dialog = SettingsDialog(self)
        if dialog.ShowModal() == wx.ID_OK:
            self.work_time = dialog.work.GetValue()
            self.short_break = dialog.short_break.GetValue()
            self.long_break = dialog.long_break.GetValue()
            self.cycles = dialog.cycles.GetValue()
            
            # Reset timer with new settings
            self.current_cycle = 1
            self.is_work = True
            self.time_left = self.work_time * 60
            self.is_running = False
            self.update_display()
        
        dialog.Destroy()

if __name__ == '__main__':
    app = wx.App()
    frame = PomodoroFrame()
    frame.Show()
    app.MainLoop()