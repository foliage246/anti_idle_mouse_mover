import pygame
import threading
import webbrowser
import time
import os
import sys

# --- Key Fix: Create a function to handle resource paths ---
def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)

# --- Configuration ---
# You can customize colors and settings here
CONFIG = {
    "window_size": (340, 320), # Slightly larger window
    "fps": 60,
    "donation_url": "https://buymeacoffee.com/foliage246",
    "icon_file": "anti_idle_mouse_mover.png", # Define the icon filename
    "colors": {
        "bg_main": (248, 250, 252),      # Main background color (light gray)
        "bg_card": (255, 255, 255),      # Card background color (white)
        "text_primary": (30, 41, 59),    # Primary text color (dark slate blue)
        "text_secondary": (100, 116, 139), # Secondary text color (gray)
        "text_light": (255, 255, 255),   # Light text (white)
        "accent": (59, 130, 246),        # Accent color (blue)
        "accent_hover": (37, 99, 235),   # Accent color on hover
        "success": (22, 163, 74),        # Success color (green)
        "success_hover": (21, 128, 61),  # Success color on hover
        "danger": (220, 38, 38),         # Danger color (red)
        "danger_hover": (185, 28, 28),   # Danger color on hover
        "disabled": (203, 213, 225),     # Disabled color
        "border": (226, 232, 240),      # Border color
    },
    "fonts": {
        "default": ("Arial", 18),
        "small": ("Arial", 14),
        "large": ("Arial", 22),
    }
}


class App:
    def __init__(self):
        pygame.init()
        # --- Core App State ---
        self.running = True
        self.mover_active = False
        self.clock = pygame.time.Clock()
        self.screen = pygame.display.set_mode(CONFIG["window_size"])
        pygame.display.set_caption("Anti-Idle Mover")

        # --- Set Window Icon ---
        self._set_window_icon()

        # --- Fonts ---
        self.font_default = pygame.font.SysFont(*CONFIG["fonts"]["default"])
        self.font_small = pygame.font.SysFont(*CONFIG["fonts"]["small"])
        self.font_large = pygame.font.SysFont(*CONFIG["fonts"]["large"])

        # --- UI State & Rectangles ---
        self.interval_seconds = 60
        self.input_text = str(self.interval_seconds)
        self.input_active = False
        self.last_move_time = 0
        self.status_message = "Stopped"
        self.temp_message_end_time = 0

        # --- Threading ---
        self.mover_thread = None

    def _set_window_icon(self):
        """Sets the icon for the Pygame window."""
        try:
            icon_path = resource_path(CONFIG["icon_file"])
            self.app_icon_surface = pygame.image.load(icon_path)
            pygame.display.set_icon(self.app_icon_surface)
        except Exception as e:
            self.app_icon_surface = None
            print(f"Could not load window icon: {e}")

    def _mouse_move_worker(self):
        """The worker function that runs in a separate thread."""
        self.last_move_time = time.time()
        while self.mover_active:
            if time.time() - self.last_move_time >= self.interval_seconds:
                try:
                    pos = pygame.mouse.get_pos()
                    pygame.mouse.set_pos((pos[0] + 1, pos[1]))
                    pygame.mouse.set_pos(pos)
                    self.last_move_time = time.time()
                except pygame.error:
                    break
            time.sleep(0.1)

    def _start_mover(self):
        if self.mover_active:
            return
        try:
            interval = int(self.input_text)
            if not 1 <= interval <= 3600:
                raise ValueError
            self.interval_seconds = interval
            self.mover_active = True
            self.input_active = False
            self.mover_thread = threading.Thread(target=self._mouse_move_worker, daemon=True)
            self.mover_thread.start()
        except (ValueError, TypeError):
            self._set_temp_status("Error: Interval must be 1-3600", 3)

    def _stop_mover(self):
        if not self.mover_active:
            return
        self.mover_active = False
        self.status_message = "Stopped"

    def _donate(self):
        try:
            webbrowser.open(CONFIG["donation_url"])
            self._set_temp_status("Thank you for your support! ❤️", 3)
        except webbrowser.Error:
            self._set_temp_status("Error: Could not open web browser.", 3)
            
    def _set_temp_status(self, message, duration_seconds):
        """Sets a status message that reverts after a duration."""
        self.status_message = message
        self.temp_message_end_time = time.time() + duration_seconds

    def _handle_events(self):
        # Define rectangles here for mouse collision detection
        input_rect = pygame.Rect(40, 110, 260, 40)
        start_btn_rect = pygame.Rect(40, 170, 125, 45)
        stop_btn_rect = pygame.Rect(175, 170, 125, 45)
        donate_btn_rect = pygame.Rect(40, 260, 260, 40)
        
        mouse_pos = pygame.mouse.get_pos()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False

            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if input_rect.collidepoint(mouse_pos) and not self.mover_active:
                    self.input_active = True
                else:
                    self.input_active = False

                if start_btn_rect.collidepoint(mouse_pos) and not self.mover_active:
                    self._start_mover()
                elif stop_btn_rect.collidepoint(mouse_pos) and self.mover_active:
                    self._stop_mover()
                elif donate_btn_rect.collidepoint(mouse_pos):
                    self._donate()

            if event.type == pygame.KEYDOWN and self.input_active:
                if event.key == pygame.K_RETURN:
                    self.input_active = False
                elif event.key == pygame.K_BACKSPACE:
                    self.input_text = self.input_text[:-1]
                elif event.unicode.isdigit():
                    self.input_text += event.unicode
                    if len(self.input_text) > 4:
                        self.input_text = self.input_text[:4]

    def _update_status(self):
        if self.temp_message_end_time and time.time() > self.temp_message_end_time:
            self.temp_message_end_time = 0
            if not self.mover_active:
                self.status_message = "Stopped"

        if self.mover_active and not self.temp_message_end_time:
            time_left = int(self.interval_seconds - (time.time() - self.last_move_time))
            self.status_message = f"Running... Next move in {time_left}s"
    
    def _draw_text(self, text, font, color, position, centered=False):
        """Helper function to draw text."""
        text_surf = font.render(text, True, color)
        text_rect = text_surf.get_rect()
        if centered:
            text_rect.center = position
        else:
            text_rect.topleft = position
        self.screen.blit(text_surf, text_rect)

    def _draw_ui(self):
        self.screen.fill(CONFIG["colors"]["bg_main"])
        
        # Draw main card
        card_rect = pygame.Rect(20, 20, 300, 280)
        pygame.draw.rect(self.screen, CONFIG["colors"]["bg_card"], card_rect, border_radius=12)
        pygame.draw.rect(self.screen, CONFIG["colors"]["border"], card_rect, 1, border_radius=12)

        # Draw title
        if self.app_icon_surface:
             self.screen.blit(pygame.transform.scale(self.app_icon_surface, (24, 24)), (40, 40))
        self._draw_text("Anti-Idle Mover", self.font_large, CONFIG["colors"]["text_primary"], (70, 40))

        # Draw input box
        self._draw_text("Move Interval (s)", self.font_small, CONFIG["colors"]["text_secondary"], (40, 85))
        input_rect = pygame.Rect(40, 110, 260, 40)
        
        if self.mover_active:
            border_color = CONFIG["colors"]["disabled"]
            bg_color = CONFIG["colors"]["bg_main"]
            text_color = CONFIG["colors"]["text_secondary"]
        else:
            border_color = CONFIG["colors"]["accent"] if self.input_active else CONFIG["colors"]["border"]
            bg_color = CONFIG["colors"]["bg_card"]
            text_color = CONFIG["colors"]["text_primary"]
        
        pygame.draw.rect(self.screen, bg_color, input_rect, border_radius=8)
        pygame.draw.rect(self.screen, border_color, input_rect, 2, border_radius=8)
        
        input_text_surf = self.font_default.render(self.input_text, True, text_color)
        self.screen.blit(input_text_surf, (input_rect.x + 15, input_rect.y + (input_rect.height - input_text_surf.get_height()) / 2))

        # Draw buttons
        mouse_pos = pygame.mouse.get_pos()
        start_btn_rect = pygame.Rect(40, 170, 125, 45)
        stop_btn_rect = pygame.Rect(175, 170, 125, 45)
        
        start_color = CONFIG["colors"]["disabled"] if self.mover_active else (CONFIG["colors"]["success_hover"] if start_btn_rect.collidepoint(mouse_pos) else CONFIG["colors"]["success"])
        pygame.draw.rect(self.screen, start_color, start_btn_rect, border_radius=8)
        self._draw_text("Start", self.font_default, CONFIG["colors"]["text_light"], start_btn_rect.center, centered=True)
        
        stop_color = CONFIG["colors"]["disabled"] if not self.mover_active else (CONFIG["colors"]["danger_hover"] if stop_btn_rect.collidepoint(mouse_pos) else CONFIG["colors"]["danger"])
        pygame.draw.rect(self.screen, stop_color, stop_btn_rect, border_radius=8)
        self._draw_text("Stop", self.font_default, CONFIG["colors"]["text_light"], stop_btn_rect.center, centered=True)

        # Draw status bar
        status_rect = pygame.Rect(40, 225, 260, 25)
        status_color = CONFIG["colors"]["success"] if self.mover_active else CONFIG["colors"]["text_secondary"]
        pygame.draw.circle(self.screen, status_color, (status_rect.x + 10, status_rect.centery), 5)
        self._draw_text(self.status_message, self.font_small, CONFIG["colors"]["text_secondary"], (status_rect.x + 25, status_rect.y + 5))

        # Draw donation button
        donate_btn_rect = pygame.Rect(40, 260, 260, 40)
        donate_color = CONFIG["colors"]["accent_hover"] if donate_btn_rect.collidepoint(mouse_pos) else CONFIG["colors"]["accent"]
        pygame.draw.rect(self.screen, donate_color, donate_btn_rect, border_radius=8)
        self._draw_text("Treat Me to a Coffee ☕", self.font_default, CONFIG["colors"]["text_light"], donate_btn_rect.center, centered=True)

        pygame.display.flip()

    def run(self):
        """The main application loop."""
        while self.running:
            self._handle_events()
            self._update_status()
            self._draw_ui()
            self.clock.tick(CONFIG["fps"])
        
        self.mover_active = False
        pygame.quit()

if __name__ == "__main__":
    app = App()
    app.run()
