from ...utils.paths import (
    WEB_DIR, 
    UI_TEMPLATE_PATH, 
    UI_TEMPLATE_BACKGROUND_PATH, 
    UI_HTML_PATH, 
    UI_STATE_JSON_PATH
    )
# import html
import json


class WebRenderingManager:

    def __init__(self, state_manager, use_background=False):
        self.state_manager = state_manager
        
        self.web_dir = WEB_DIR
        self.output_file = UI_HTML_PATH
        self.state_json_file = UI_STATE_JSON_PATH
        
        self.use_background = True
        self.template_file = self.get_template_file()
        self.template_html = self.template_file.read_text(encoding="utf-8")
        
        self.last_rendered_html = None
        self.last_state_json = None

    def set_background_enabled(self, use_background:bool) -> None:
        self.use_background = use_background

    def get_template_file(self):
        if self.use_background is None:
            raise TypeError("self.use_background is of type None")
        if self.use_background:
            return UI_TEMPLATE_BACKGROUND_PATH
        return UI_TEMPLATE_PATH
    
    def build_rendered_html(self) -> str:
        return self.template_html

    def build_state_json(self) -> str:
        state = self.state_manager.get_state()

        mode = str(state.get("mode", "idle")).strip().lower() or "idle"
        heard = str(state.get("heard", ""))
        reply = str(state.get("reply", ""))

        data = {
            "mode": mode,
            "mode_text": mode.upper(),
            "heard": heard,
            "reply": reply,
        }

        return json.dumps(data, ensure_ascii=False)

    def render_ui_file_if_changed(self) -> bool:
        rendered = self.build_rendered_html()

        if rendered != self.last_rendered_html:
            self.output_file.write_text(rendered, encoding="utf-8")
            self.last_rendered_html = rendered
            return True

        return False

    def render_state_json_if_changed(self) -> bool:
        state_json = self.build_state_json()

        if state_json != self.last_state_json:
            self.state_json_file.write_text(state_json, encoding="utf-8")
            self.last_state_json = state_json
            return True

        return False

    def init_ui_state(self):
        self.web_dir.mkdir(parents=True, exist_ok=True)
        self.render_ui_file_if_changed()
        self.render_state_json_if_changed()

    def ui_update(self, mode=None, heard=None, reply=None):
        changed = self.state_manager.update(
            mode=mode,
            heard=heard,
            reply=reply,
        )

        if not changed:
            return

        self.render_state_json_if_changed()

# from ..utils.paths import WEB_DIR, UI_TEMPLATE_PATH, UI_HTML_PATH
# import html
# import time


# class RenderingManager:

#     def __init__(self, state_manager, refresh_callback=None, refresh_min_interval=0.20):
#         self.state_manager = state_manager
#         self.template_file = UI_TEMPLATE_PATH
#         self.output_file = UI_HTML_PATH
#         self.web_dir = WEB_DIR
#         self.template_html = self.template_file.read_text(encoding="utf-8")

#         self.refresh_callback = refresh_callback
#         self.refresh_min_interval = refresh_min_interval
#         self.last_rendered_html = None
#         self.last_refresh_time = 0.0

#     def build_rendered_html(self) -> str:
#         state = self.state_manager.get_state()

#         mode = str(state.get("mode", "idle")).strip().lower() or "idle"
#         heard = html.escape(str(state.get("heard", "")))
#         reply = html.escape(str(state.get("reply", "")))

#         return (
#             self.template_html
#             .replace("{{MODE_CLASS}}", mode)
#             .replace("{{MODE_TEXT}}", mode.upper())
#             .replace("{{HEARD}}", heard)
#             .replace("{{REPLY}}", reply)
#         )

#     def render_ui_file_if_changed(self) -> bool:
#         rendered = self.build_rendered_html()

#         if rendered != self.last_rendered_html:
#             self.output_file.write_text(rendered, encoding="utf-8")
#             self.last_rendered_html = rendered
#             return True

#         return False

#     def init_ui_state(self):
#         self.web_dir.mkdir(parents=True, exist_ok=True)
#         self.render_ui_file_if_changed()

#     def ui_update(self, mode=None, heard=None, reply=None):
#         changed = self.state_manager.update(
#             mode=mode,
#             heard=heard,
#             reply=reply,
#         )

#         if not changed:
#             return

#         file_changed = self.render_ui_file_if_changed()
#         now = time.time()
    
#         if (
#             file_changed
#             and self.refresh_callback is not None
#             and (now - self.last_refresh_time) >= self.refresh_min_interval
#         ):
#             self.last_refresh_time = now
#             self.refresh_callback()
        
#         # file_changed = self.render_ui_file_if_changed()
#         # now = time.time()

#         # if file_changed and (now - self.last_refresh_time) >= self.refresh_min_interval:
#         #     self.last_refresh_time = now
#         #     self.refresh_callback()

# # from ..utils.paths import WEB_DIR, UI_TEMPLATE_PATH, UI_HTML_PATH
# # import html
# # import time

# # class RenderingManager:
    
# #     def __init__(self, state_manager, refresh_min_interval = 0.20):
# #         self.state_manager = state_manager
# #         self.template_file = UI_TEMPLATE_PATH
# #         self.output_file = UI_HTML_PATH
# #         self.web_dir = WEB_DIR
# #         self.template_html = self.template_file.read_text(encoding="utf-8")
        
# #         # self.refresh_callback = refresh_callback
# #         self.refresh_min_interval = refresh_min_interval
# #         self.last_rendered_html = None
# #         self.last_refresh_time = 0.0

# #     def build_rendered_html(self) -> str:
# #         state = self.state_manager.get_state()
        
# #         mode = str(state.get("mode", "idle")).strip().lower() or "idle"
# #         heard = html.escape(str(state.get("heard", "")))
# #         reply = html.escape(str(state.get("reply", "")))
        
# #         return (
# #             self.template_html
# #             .replace("{{MODE_CLASS}}", mode)
# #             .replace("{{MODE_TEXT}}", mode.upper())
# #             .replace("{{HEARD}}", heard)
# #             .replace("{{REPLY}}", reply)
# #         )

# #     def render_ui_file_if_changed(self) -> bool:
# #         rendered = self.build_rendered_html()
# #         if rendered != self._last_rendered_html:
# #             self.output_file.write_text(rendered, encoding="utf-8")
# #             self._last_rendered_html = rendered
# #             return True
# #         return False

# #     def init_ui_state(self):
# #         self.web_dir.mkdir(parents=True, exist_ok=True)
# #         self.render_ui_file_if_changed()

# #     def ui_update(self, mode=None, heard=None, reply=None):
# #         changed = self.state_manager.update(mode=mode, heard=heard, reply=reply)
# #         if not changed:
# #             return
# #         file_changed = self.render_ui_file_if_changed()
# #         now = time.time()
# #         if file_changed and (now - self._last_refresh_time) >= self.refresh_min_interval:
# #             self._last_refresh_time = now
# #             # self.refresh_callback()