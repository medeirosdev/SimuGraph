from __future__ import annotations
import pygame
import os
import simugraph.settings as cfg

def scale_cover(image: pygame.Surface, target_w: int, target_h: int) -> pygame.Surface:
    """Scale image to cover target dimensions while preserving aspect ratio."""
    img_w, img_h = image.get_size()
    scale = max(target_w / img_w, target_h / img_h)
    new_w = int(img_w * scale)
    new_h = int(img_h * scale)
    scaled = pygame.transform.smoothscale(image, (new_w, new_h))
    
    # Crop centered
    crop_x = (new_w - target_w) // 2
    crop_y = (new_h - target_h) // 2
    cropped = pygame.Surface((target_w, target_h))
    cropped.blit(scaled, (0, 0), pygame.Rect(crop_x, crop_y, target_w, target_h))
    return cropped

def draw_gradient_rect(surface: pygame.Surface, color1: tuple[int, int, int], color2: tuple[int, int, int], rect: pygame.Rect):
    """Draw a rectangle filled with a horizontal color gradient."""
    x, y, w, h = rect.x, rect.y, rect.width, rect.height
    for i in range(w):
        t = i / max(1, w - 1)
        r = int(color1[0] + (color2[0] - color1[0]) * t)
        g = int(color1[1] + (color2[1] - color1[1]) * t)
        b = int(color1[2] + (color2[2] - color1[2]) * t)
        pygame.draw.line(surface, (r, g, b), (x + i, y), (x + i, y + h))

def show_splash_screen(screen: pygame.Surface, clock: pygame.time.Clock) -> None:
    """Show an animated splash screen on startup with an interactive Enter button, description, and banner."""
    w, h = cfg.WINDOW_W, cfg.WINDOW_H
    left_w = w // 2
    right_w = w - left_w
    
    # Load banner image
    banner_surf = None
    if os.path.exists("assets/banner.png"):
        try:
            raw_banner = pygame.image.load("assets/banner.png").convert_alpha()
            banner_surf = scale_cover(raw_banner, left_w, h)
        except Exception:
            pass
            
    # If banner failed to load, create a placeholder gradient canvas
    if banner_surf is None:
        banner_surf = pygame.Surface((left_w, h))
        draw_gradient_rect(banner_surf, (30, 20, 50), (15, 15, 25), pygame.Rect(0, 0, left_w, h))
        # Draw some decorative abstract nodes/edges
        pygame.draw.circle(banner_surf, (90, 160, 255), (left_w // 2, h // 2), 60, 2)
        pygame.draw.circle(banner_surf, (180, 120, 255), (left_w // 2 - 120, h // 2 + 100), 40, 2)
        pygame.draw.circle(banner_surf, (80, 220, 160), (left_w // 2 + 120, h // 2 - 100), 50, 2)
        pygame.draw.line(banner_surf, (100, 100, 150), (left_w // 2 - 120, h // 2 + 100), (left_w // 2, h // 2), 2)
        pygame.draw.line(banner_surf, (100, 100, 150), (left_w // 2 + 120, h // 2 - 100), (left_w // 2, h // 2), 2)

    # Load Fonts
    try:
        title_font = pygame.font.Font(cfg.FONT_MONO_PATH, 44)
        subtitle_font = pygame.font.Font(cfg.FONT_MONO_PATH, 15)
        feature_font = pygame.font.Font(cfg.FONT_MONO_PATH, 14)
        btn_font = pygame.font.Font(cfg.FONT_MONO_PATH, 16)
        footer_font = pygame.font.Font(cfg.FONT_MONO_PATH, 12)
    except Exception:
        title_font = pygame.font.SysFont("monospace", 44)
        subtitle_font = pygame.font.SysFont("monospace", 15)
        feature_font = pygame.font.SysFont("monospace", 14)
        btn_font = pygame.font.SysFont("monospace", 16)
        footer_font = pygame.font.SysFont("monospace", 12)
        
    features = [
        "Interactive Graph Editor & Manipulation",
        "13+ Animated Algorithms (BFS, Dijkstra, Kruskal...)",
        "Advanced Exporters (GraphML, GEXF, DOT, CSV, GIF)",
        "Real-time Topological & Metric Properties Analysis",
        "Dynamic Plugin Loading & Keyboard Navigation Mode"
    ]
    
    right_start_x = left_w + 50
    btn_rect = pygame.Rect(right_start_x, h - 230, 260, 52)
    credits_area_rect = pygame.Rect(right_start_x, h - 95, 260, 50)
    
    def draw_splash(target_screen: pygame.Surface, alpha: int):
        # Create temp surface for alpha blitting
        splash_surf = pygame.Surface((w, h))
        splash_surf.fill((18, 18, 28)) # match theme bg
        
        # 1. Left side: Draw banner
        splash_surf.blit(banner_surf, (0, 0))
        
        # Overlay gradient on the banner border to blend left & right halves
        blend_w = 40
        for i in range(blend_w):
            col_alpha = int(255 * (i / blend_w))
            blend_col = (18, 18, 28, col_alpha)
            pygame.draw.line(splash_surf, blend_col, (left_w - blend_w + i, 0), (left_w - blend_w + i, h))

        # 2. Right side content
        # Draw Title
        title_surf = title_font.render("SimuGraph", True, (240, 245, 255))
        splash_surf.blit(title_surf, (right_start_x, 150))
        
        # Draw Subtitle
        sub_surf = subtitle_font.render("Interactive Graph & Algorithm Simulator", True, (150, 155, 185))
        splash_surf.blit(sub_surf, (right_start_x, 210))
        
        # Decorative divider line
        pygame.draw.line(splash_surf, (60, 65, 90), (right_start_x, 245), (w - 50, 245), 1)
        
        # Draw features list
        bullet_y = 280
        for feat in features:
            pygame.draw.rect(splash_surf, (90, 160, 255), (right_start_x, bullet_y + 5, 6, 6))
            feat_surf = feature_font.render(feat, True, (200, 205, 225))
            splash_surf.blit(feat_surf, (right_start_x + 18, bullet_y))
            bullet_y += 35
            
        # 3. Interactive button and Credits hover
        mx, my = pygame.mouse.get_pos()
        is_hover = btn_rect.collidepoint(mx, my)
        credits_hover = credits_area_rect.collidepoint(mx, my)
        
        # Gradient colors based on hover state
        if is_hover:
            color1, color2 = (110, 180, 255), (200, 140, 255)
        else:
            color1, color2 = (90, 160, 255), (180, 120, 255)

        if is_hover or credits_hover:
            # Hover cursor change hint
            try:
                pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_HAND)
            except Exception:
                pass
        else:
            try:
                pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_ARROW)
            except Exception:
                pass
                
        # Draw button background gradient
        draw_gradient_rect(splash_surf, color1, color2, btn_rect)
        
        # Draw button border / outline
        pygame.draw.rect(splash_surf, (255, 255, 255), btn_rect, width=1, border_radius=4)
        
        # Draw button text centered
        btn_text_surf = btn_font.render("ENTRAR NO SIMULADOR", True, (255, 255, 255))
        tx = btn_rect.x + (btn_rect.width - btn_text_surf.get_width()) // 2
        ty = btn_rect.y + (btn_rect.height - btn_text_surf.get_height()) // 2
        splash_surf.blit(btn_text_surf, (tx, ty))
        
        # Draw shortcut tip
        tip_surf = footer_font.render("Pressione ENTER ou ESPAÇO para entrar", True, (100, 105, 130))
        splash_surf.blit(tip_surf, (right_start_x + (btn_rect.width - tip_surf.get_width()) // 2, h - 150))
        
        # Draw developer credits (clickable)
        credits_color = (130, 180, 255) if credits_hover else (130, 135, 160)
        credits_surf = footer_font.render("Guilherme de Medeiros - UNICAMP", True, credits_color)
        credits_surf2 = footer_font.render("Matemática Aplicada e Computacional", True, (90, 95, 115))
        
        cx1 = right_start_x + (btn_rect.width - credits_surf.get_width()) // 2
        cx2 = right_start_x + (btn_rect.width - credits_surf2.get_width()) // 2
        splash_surf.blit(credits_surf, (cx1, h - 90))
        splash_surf.blit(credits_surf2, (cx2, h - 70))

        # Set alpha if fading
        if alpha < 255:
            splash_surf.set_alpha(alpha)
            
        target_screen.fill((18, 18, 28))
        target_screen.blit(splash_surf, (0, 0))
        pygame.display.flip()

    fade_frames = 15
    should_exit = False
    
    # Phase 1: Fade-in
    for frame in range(fade_frames):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                import sys
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key in (pygame.K_RETURN, pygame.K_KP_ENTER, pygame.K_SPACE):
                    should_exit = True
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    if btn_rect.collidepoint(event.pos):
                        should_exit = True
                    elif credits_area_rect.collidepoint(event.pos):
                        import webbrowser
                        webbrowser.open("https://www.linkedin.com/in/guilhermedemedeiros/")
                        
        if should_exit:
            break
            
        alpha = int(255 * (frame / fade_frames))
        draw_splash(screen, alpha)
        clock.tick(60)
        
    # Phase 2: Interactive loop (waiting for user input)
    while not should_exit:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                import sys
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key in (pygame.K_RETURN, pygame.K_KP_ENTER, pygame.K_SPACE):
                    should_exit = True
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    if btn_rect.collidepoint(event.pos):
                        should_exit = True
                    elif credits_area_rect.collidepoint(event.pos):
                        import webbrowser
                        webbrowser.open("https://www.linkedin.com/in/guilhermedemedeiros/")
                    
        if should_exit:
            break
            
        draw_splash(screen, 255)
        clock.tick(60)
        
    # Restore normal cursor before exiting splash screen
    try:
        pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_ARROW)
    except Exception:
        pass

    # Phase 3: Fade-out
    fade_out_surf = screen.copy()
    for frame in range(fade_frames, 0, -1):
        alpha = int(255 * (frame / fade_frames))
        screen.fill((18, 18, 28))
        fade_out_surf.set_alpha(alpha)
        screen.blit(fade_out_surf, (0, 0))
        pygame.display.flip()
        clock.tick(60)
