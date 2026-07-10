import paramiko
from ..security.details import get_ssh_details

class SSHManager:
   
    def __init__(self):
       self.ssh_details = get_ssh_details()
       self.ssh = None
       self.sftp = None
    
    def open_ssh(self):
        try: 
            self.ssh = paramiko.SSHClient()
            self.ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            self.ssh.connect(
                hostname    = self.ssh_details['ip'],
                port        = self.ssh_details['port'],
                username    = self.ssh_details['username'],
                password    = self.ssh_details['password'],
                timeout     = 10,
                allow_agent= False,
                look_for_keys= False,
                # disabled_algorithms={
                #     "keys": [
                #         "ssh-ed25519",
                #         "ecdsa-sha2-nistp256",
                #         "ecdsa-sha2-nistp384",
                #         "ecdsa-sha2-nistp521",
                #     ],
                #     "kex": [
                #         "curve25519-sha256",
                #         "curve25519-sha256@libssh.org",
                #     ],
                # },
            )
            print("SSH connection with Pepper is established.")
        except Exception as e:
            print("SSH connection failed: ", e)
            self.ssh = None
        return self.ssh
    
    def get_ssh(self):
        if self.ssh is not None:
            transport = self.ssh.get_transport()
            if transport is not None and transport.is_active():
                return self.ssh
            self.close_ssh()
        self.ssh = self.open_ssh()
        return self.ssh
    
    def close_ssh(self):
        self.close_sftp()
        if self.ssh is not None:
            self.ssh.close()
            self.ssh = None
        print("SSH connection with Pepper was dropped.")
    
    def send_command(self, cmd: str, verbose=False):
        if self.get_ssh() is not None:
            stdin, stdout, stderr = self.ssh.exec_command(cmd)
            cmd_out = stdout.read().decode("utf-8", errors="replace").strip()
            cmd_err = stderr.read().decode("utf-8", errors="replace").strip()
            self.print_command_output(cmd, cmd_out, cmd_err, verbose)
            return cmd_out, cmd_err
        else:
            err_msg = "SSH connection could not be established"
            print("Error: ",err_msg)
            return "", err_msg
    
    def print_command_output(self, cmd, out, err, verbose):
        if verbose or err:
            print("CMD: ", cmd)
        if verbose:
            print("OUT: ", out if out else "OK")
        if err:
            print("ERR: ", err) 
    
    def get_sftp(self):
        if self.get_ssh() is not None:
            if self.sftp is not None:
                try:
                    self.sftp.stat(".")
                    return self.sftp
                except Exception:
                    self.close_sftp()
            try:
                self.sftp = self.ssh.open_sftp()
            except Exception as e:
                print("SFTP connection failed:", e)
                self.sftp = None
            return self.sftp
        else:
            return None
    
    def close_sftp(self):
        if self.sftp is not None:
            self.sftp.close()
            self.sftp = None
    
    def upload_file(self, local, remote):
        sftp = self.get_sftp()
        
        if sftp is None:
            print("SFTP connection could not be established")
            return False
        
        try:
            sftp.put(local, remote)
            print("File upload success")
            return True

        except Exception as e:
            print("File upload failed:", e)
            return False

        # if self.ssh.get_sftp() is not None:
        #     try:
        #         self.ssh.sftp.put(local, remote)
        #         print("File upload success")
        #         return True
        #     except Exception as e:
        #         print("File upload failed: ", e)
        #         return False
        # else:
        #     print("SFTP connection could not be established")
        #     return False
