from ..utils.paths import LOCAL_PEPPER_AUDIO, REMOTE_PEPPER_AUDIO

def open_sftp(ssh):
    return ssh.open_sftp()

def upload_audio(sftp, local_file=LOCAL_PEPPER_AUDIO, remote_file=REMOTE_PEPPER_AUDIO):
    sftp.put(str(local_file), remote_file)
