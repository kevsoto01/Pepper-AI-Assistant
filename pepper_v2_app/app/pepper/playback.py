from ..utils.paths import LOCAL_PEPPER_AUDIO, REMOTE_PEPPER_AUDIO

class PepperPlaybackManager:
    
    def __init__(self, ssh_manager):
        self.ssh_manager = ssh_manager
        self.previous_volume = None
                  
    def upload_audio(self, local, remote):
        return self.ssh_manager.upload_file(local, remote)

    def play_audio(self, local=str(LOCAL_PEPPER_AUDIO), remote=REMOTE_PEPPER_AUDIO):
        if self.upload_audio(local, remote):
            command = (
                f'nohup qicli call ALAudioPlayer.playFile "{remote}" '
                f'> /tmp/pepper_audio.log 2>&1 &'
                )
            out, err = self.ssh_manager.send_command(command)
            return out, err
        else:
            error_msg = "Audio upload failed, cannot commence playback."
            print(error_msg)
            return "", error_msg
     
    def stop_audio(self):
        out, err = self.ssh_manager.send_command('qicli call ALAudioPlayer.stopAll')
        return out, err
    
    def set_master_volume(self, volume:float):
        if volume>1 or volume<0:
            raise ValueError("Pepper master volume is bounded between 0 and 1")
        
        if self.previous_volume is None or volume != self.previous_volume:
            self.previous_volume = volume
            out, err = self.ssh_manager.send_command(f"qicli call ALAudioDevice.setOutputVolume {volume}")
            return out, err
        
        return "", ""
    
    def set_tts_volume(self, volume:float):
        if volume>1 or volume<0:
            raise ValueError("Pepper TTS volume is bounded between 0 and 1")
        out, err = self.ssh_manager.send_command(f"qicli call ALTextToSpeech.setVolume {volume}")
        return out, err
        
    def sing_happy_birthday(self, upload):
        local = r"C:\\Users\\Kidworks\Downloads\\happy_bday_4.wav"
        remote_christina_trimmed = r"/home/nao/recordings/happy_bday_4.wav"
        remote_christina = r"/home/nao/recordings/happy_birthday.wav"
        remote_christina_full = r"/home/nao/recordings/happy_birthday_christina.wav"
        remote_girl = r"/home/nao/recordings/happy_birthday_girl.wav"
        remote = [remote_christina_trimmed, remote_christina, remote_christina_full, remote_girl]
        used_audio = remote[0]
        if upload: self.upload_audio(local,used_audio)
        command = (
            f'nohup qicli call ALAudioPlayer.playFile "{used_audio}" '
            f'> /tmp/pepper_audio.log 2>&1 &'
            )
        out, err = self.ssh_manager.send_command(command)
        return out, err