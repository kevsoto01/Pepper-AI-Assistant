from ..utils.paths import UI_URL # autodetect IPv4 address in the future
import time

class PepperTabletManager:
    
    def __init__(self, ssh_manager):
        self.ssh = ssh_manager
        self.url = UI_URL  
    
    def enable_wifi(self, verbose=False):
        cmd = "qicli call ALTabletService.enableWifi"
        self.ssh.send_command(cmd, verbose)    
        
    def disable_wifi(self, verbose=False):
        cmd = "qicli call ALTabletService.disableWifi"
        self.ssh.send_command(cmd, verbose)  
    
    def build_cache_buster_url(self):
        return f"{self.url}?v={int(time.time() * 1000)}"
    
    def show(self, verbose=False):
        url = self.build_cache_buster_url()
        cmd = f'qicli call ALTabletService.showWebview "{url}"'
        return self.ssh.send_command(cmd, verbose)

    def refresh(self, verbose=False):
        return self.show(verbose)
    
    # def show(self, verbose=False):
    #     cmd = f'qicli call ALTabletService.showWebview "{self.url}"'
    #     self.ssh.send_command(cmd, verbose)
     
    # def refresh(self, verbose=False):
    #     cache_buster_url = f"{self.url}?v={int(time.time() * 1000)}"
    #     cmd = f'qicli call ALTabletService.showWebview "{cache_buster_url}"'
    #     self.ssh.send_command(cmd, verbose)
    
    def hide(self, verbose=False):
        cmd = "qicli call ALTabletService.hideWebview"
        self.ssh.send_command(cmd, verbose)            
        