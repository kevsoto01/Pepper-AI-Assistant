from time import sleep

class PepperController:
    def __init__(self,ssh_manager,tablet_manager,audio_manager,movement_manager):
        self.ssh_manager = ssh_manager
        self.tablet_manager = tablet_manager
        self.audio_manager = audio_manager
        self.movement_manager = movement_manager

        self.ssh = None
        self.sftp = None

    # Global
    def start(self):
        self.connect_ssh()
        self.connect_sftp()
        self.tablet_manager.enable_wifi()
        self.show_tablet_ui() 
 
    def stop(self):
       self.hide_tablet_ui()
       self.disconnect()  
   
    # Connectivity
    def connect_ssh(self):
        self.ssh = self.ssh_manager.open_ssh()
        return self.ssh        
    
    def connect_sftp(self):
        self.sftp = self.ssh_manager.get_sftp()
        return self.sftp 
    
    def connect(self):
        self.ssh = self.connect_ssh()
        self.sftp = self.connect_sftp()
        return self.ssh, self.sftp 
    
    def disconnect(self):
        self.ssh = None
        self.sftp = None
        self.ssh_manager.close_ssh()
      
    # Playback
    def play_audio(self):
        self.audio_manager.play_audio()
        
    def stop_audio(self):
        self.audio_manager.stop_audio()

    def sing_happy_birthday(self, upload=False):
        # Play song
        self.audio_manager.sing_happy_birthday(upload)

        # Dance
        self.movement_manager.birthday_dance()

    def set_volume(self, volume):
        self.audio_manager.set_master_volume(volume)

    # Tablet
    def show_tablet_ui(self):
        self.tablet_manager.show()

    def refresh_tablet_ui(self):
        self.tablet_manager.refresh()

    def hide_tablet_ui(self):
        self.tablet_manager.hide()   
        
    # Movement
    def body_talk(self, duration_seconds):
        self.audio_manager.set_tts_volume(0.0)
        self.movement_manager.perform_body_talk(duration_seconds)


        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        


    

    

    