import keyboard

def is_key_pressed(key) -> bool:
    return keyboard.is_pressed(key)

def exit_key_pressed():
    return is_key_pressed("esc")

def record_key_pressed():
    return is_key_pressed("end")

def stop_key_pressed():
    return is_key_pressed("home")

ptt_released = False

def on_ptt_release(event):
    global ptt_released
    ptt_released = True
    
    