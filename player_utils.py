import pygame

class Render_img:
    def __init__(self, surface, img, x, y):
        self.surf = surface
        self.img = img
        self.x = x
        self.y = y
    
    def draw(self, surf, img, x, y):
        if isinstance(img, pygame.Surface):
            img_rect = img.get_rect()
            img_rect.x = x
            img_rect.y = y
            surf.blit(img, img_rect)

class TextInputBox:
    def __init__(self, x, y, w, h, font, is_command = False, text='', color_active=(200,200,200), color_inactive=(150,150,150)):
        self.rect = pygame.Rect(x, y, w, h)
        self.h = h
        self.color_active = color_active
        self.color_inactive = color_inactive
        self.color = self.color_inactive
        self.text = text
        self.font = font
        self.txt_surface = font.render(text, True, self.color)
        self.active = False
        self.is_command = is_command

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            self.active = self.rect.collidepoint(event.pos)
            self.color = self.color_active if self.active else self.color_inactive

        if event.type == pygame.KEYDOWN and self.active:
            if event.key == pygame.K_RETURN:
                entered = self.text
                self.text = '' if self.is_command == False else ">> "
                self.txt_surface = self.font.render(self.text, True, self.color)
                return entered  # 回傳使用者輸入
            elif event.key == pygame.K_BACKSPACE:
                self.text = self.text[:-1]
            else:
                self.text += event.unicode
                if len(self.text) > 30:
                    self.text = self.text[:30]
            self.txt_surface = self.font.render(self.text, True, self.color)
        return None

    def update(self):
        width = max(200, self.txt_surface.get_width()+10)
        self.rect.w = width

    def draw(self, screen):
        screen.blit(self.txt_surface, (self.rect.x+5, self.rect.y + 3))
        pygame.draw.rect(screen, self.color, self.rect, 2)
        if self.active: pygame.draw.line(screen, (255, 255, 255), (self.rect.x + self.txt_surface.get_width() + 10, self.rect.y + 10), (self.rect.x + self.txt_surface.get_width() + 10, self.rect.y + self.h - 10))