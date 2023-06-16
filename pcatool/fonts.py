from pcatool.commonlibs import pygame, Path, Tuple

font_path = Path(__file__).parent / 'arial.ttf'

def get_font_map():
    font_map = {}
    fonts = [18, 20, 25, 30, 35, 40, 45, 50]
    for i in fonts:
        font_map[i] = pygame.font.SysFont(None, i)
    return font_map


# def text_fn(surface,
#               text: str,
#               size: int = 20,
#               typeface: str = None,
#               center: Tuple[int, int] = (0, 0),
#               color: Tuple[int, int, int] = (0, 0, 0),
#               align: str = 'center'):
#     # pygame.freetype.init()
#     # ft = pygame.freetype.SysFont(typeface, size)
#     # rect = ft.get_rect(text)
#     # if align == 'center':
#     #     rect.center = center
#     # elif align == 'left':
#     #     rect.left = 20
#     #     rect.centery = center[1]
#     font = pygame.font.SysFont(typeface, size)
#     text_surface = font.render(text, True, color)
#     text_rect = text_surface.get_rect(center=(center[0], center[1]))
#     surface.blit(text_surface, text_rect)
#     # ft.render_to(surface,
#     #              rect.topleft,
#     #              text, color)
#
# def font_10(surface,
#             text: str,
#             typeface: str = None,
#             center: Tuple[int, int] = (0, 0),
#             color: Tuple[int, int, int] = (0, 0, 0),
#             align: str = 'center'):
#     args = (surface, text, 10, typeface, center, color, align)
#     text_fn(*args)
#
# def font_15(surface,
#             text: str,
#             typeface: str = None,
#             center: Tuple[int, int] = (0, 0),
#             color: Tuple[int, int, int] = (0, 0, 0),
#             align: str = 'center'):
#     args = (surface, text, 15, typeface, center, color, align)
#     text_fn(*args)
#
# def font_20(surface,
#             text: str,
#             typeface: str = None,
#             center: Tuple[int, int] = (0, 0),
#             color: Tuple[int, int, int] = (0, 0, 0),
#             align: str = 'center'):
#     args = (surface, text, 20, typeface, center, color, align)
#     text_fn(*args)
#
# def font_25(surface,
#             text: str,
#             typeface: str = None,
#             center: Tuple[int, int] = (0, 0),
#             color: Tuple[int, int, int] = (0, 0, 0),
#             align: str = 'center'):
#     args = (surface, text, 25, typeface, center, color, align)
#     text_fn(*args)
#
# def font_30(surface,
#             text: str,
#             typeface: str = None,
#             center: Tuple[int, int] = (0, 0),
#             color: Tuple[int, int, int] = (0, 0, 0),
#             align: str = 'center'):
#     args = (surface, text, 30, typeface, center, color, align)
#     text_fn(*args)
#
#
# def font_40(surface,
#             text: str,
#             typeface: str = None,
#             center: Tuple[int, int] = (0, 0),
#             color: Tuple[int, int, int] = (0, 0, 0),
#             align: str = 'center'):
#     args = (surface, text, 40, typeface, center, color, align)
#     text_fn(*args)
#
#
# def font_50(surface,
#             text: str,
#             typeface: str = None,
#             center: Tuple[int, int] = (0, 0),
#             color: Tuple[int, int, int] = (0, 0, 0),
#             align: str = 'center'):
#     args = (surface, text, 50, typeface, center, color, align)
#     text_fn(*args)


