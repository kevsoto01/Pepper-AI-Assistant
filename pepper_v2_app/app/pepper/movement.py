import shlex
import math

from time import sleep

from ..utils.paths import LOCAL_PEPPER_AUDIO, REMOTE_PEPPER_AUDIO, PEPPER_ANIMATION_PATHS


T_DURATION_MILLISECONDS = 67 
# probably measure 20 t's manually then divide by 20

class PepperMovementManager:
    
    def __init__(self, ssh_manager):
        self.ssh_manager = ssh_manager
                  
    def get_animation_name(self, animation:str):
        return PEPPER_ANIMATION_PATHS[animation]

    def play_animation(self, animation:str, verbose=False):
        animation_dir = self.get_animation_name(animation)
        text = shlex.quote(animation_dir)
        command = (
            f"qicli call ALAnimationPlayer.run {text} "
            f"> /tmp/pepper_animation.log 2>&1"
        )
        out, err = self.ssh_manager.send_command(command, verbose)
        return out, err
    
    def stop_animation(self, animation: str, verbose=False):
        animation_dir = self.get_animation_name(animation)

        command = (
            "qicli call ALBehaviorManager.stopBehavior "
            f"{shlex.quote(animation_dir)} "
            "> /tmp/pepper_stop_animation.log 2>&1 &"
        )

        out, err = self.ssh_manager.send_command(command, verbose)
        return out, err

    def reset_to_natural_position(self, verbose=False):
        command = "qicli call ALRobotPosture.goToPosture StandInit 0.5"
        out, err = self.ssh_manager.send_command(command, verbose)
        return out, err

    def birthday_dance(self):
        print("playing birthday dance")
        sleep(2)
        max_loops = 3
        for iteration in range(max_loops):
            print(iteration+1)
            self.play_animation("air_guitar", verbose=False)
            sleep(0.25)
            # sleep(6)
            # if iteration < max_loops-1:
            #     self.stop_animation("air_guitar")
        self.play_animation("give")
        self.reset_to_natural_position()
        print("birthday dance done")

    def perform_body_talk(self, speech_duration_seconds):
        t_string = self.make_t_string(float(speech_duration_seconds))
        text = shlex.quote(f"^mode(random) {t_string}")
        command = (
            f"nohup qicli call ALAnimatedSpeech.say {text} "
            f"> /tmp/pepper_animated_say.log 2>&1 &"
        )
        out, err = self.ssh_manager.send_command(command)
        return out, err
    
    def make_t_string(self, speech_duration_seconds:float):
        """
        time_speaking = 0.186629*length_of_t_string+0.471333 
        
        coefficients obtained via linear regression of experimental values
        
        constant term is to account for time spent converting text into 
        speech, which is nonlinear
        
        length = (time - 0.471333)/0.186629
        """

        t_count = (float(speech_duration_seconds)-0.471333)/0.186629

        if t_count <= 1: t_count = 2.0
        else: t_count = math.ceil(t_count)

        return " ".join(["t"] * t_count)  
    

    

