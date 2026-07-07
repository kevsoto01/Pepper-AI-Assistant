class WebStateManager:
    def __init__(self):
        self.state = {
            "mode": "idle", # Options: idle, listening, thinking, speaking, connecting, disconnected
            "heard": "",
            "reply": "",
        }

    def get_state(self):
        return self.state.copy()

    def update(self, mode=None, heard=None, reply=None):
        changed = False
        
        if mode is not None and self.state["mode"] != mode:
            self.state["mode"] = mode
            changed = True
            
        if heard is not None and self.state["heard"] != heard:
            self.state["heard"] = heard
            changed = True
            
        if reply is not None and self.state["reply"] != reply:
            self.state["reply"] = reply
            changed = True
            
        return changed