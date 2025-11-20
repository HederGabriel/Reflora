import pygame

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (200, 200, 200)


class Button:
    def __init__(self, rect, text, font, callback=None):
        self.rect = pygame.Rect(rect)
        self.text = text
        self.font = font
        self.callback = callback
        self.hover = False

    def draw(self, surf):
        color = (170, 170, 170) if self.hover else GRAY
        pygame.draw.rect(surf, color, self.rect, border_radius=6)
        text = self.font.render(self.text, True, BLACK)
        surf.blit(text, text.get_rect(center=self.rect.center))

    def handle_event(self, ev):
        if ev.type == pygame.MOUSEMOTION:
            self.hover = self.rect.collidepoint(ev.pos)
        elif ev.type == pygame.MOUSEBUTTONDOWN and ev.button == 1:
            if self.rect.collidepoint(ev.pos) and self.callback:
                self.callback()


def centered_text(surf, text, font, y, color=BLACK):
    img = font.render(text, True, color)
    rect = img.get_rect(center=(surf.get_width() // 2, y))
    surf.blit(img, rect)
