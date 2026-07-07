import paramiko

from .file_io import REMOTE_PEPPER_AUDIO

def play_audio(ssh, retry_limit, remote_file=REMOTE_PEPPER_AUDIO):

    retry_limit = min(retry_limit, 10)

    for attempt in range(retry_limit):
        
        try:
            stdin, stdout, stderr = ssh.exec_command(
                f'qicli call ALAudioPlayer.playFile "{remote_file}"'
            )
            err = stderr.read().decode("utf-8", errors="ignore").strip()
            
            if err:
                print("Pepper playback stderr:", err)

            return
        
        except paramiko.SSHException as e:
            print("Pepper SSH error:", e)
            
            if ssh is not None:
                try:
                    ssh.close()
                except:
                    pass
                
            if attempt == retry_limit-1:
                raise