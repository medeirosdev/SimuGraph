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

def draw_gradient_line(surface: pygame.Surface, color1: tuple[int, int, int], color2: tuple[int, int, int], rect: pygame.Rect):
    """Draw a horizontal rectangle filled with a horizontal color gradient."""
    x, y, w, h = rect.x, rect.y, rect.width, rect.height
    for i in range(w):
        t = i / max(1, w - 1)
        r = int(color1[0] + (color2[0] - color1[0]) * t)
        g = int(color1[1] + (color2[1] - color1[1]) * t)
        b = int(color1[2] + (color2[2] - color1[2]) * t)
        pygame.draw.line(surface, (r, g, b), (x + i, y), (x + i, y + h))

def show_splash_screen(screen: pygame.Surface, clock: pygame.time.Clock) -> None:
    """Show an animated splash screen on startup with progress bar, description, and banner."""
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
        draw_gradient_line(banner_surf, (30, 20, 50), (15, 15, 25), pygame.Rect(0, 0, left_w, h))
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
        status_font = pygame.font.Font(cfg.FONT_MONO_PATH, 13)
        skip_font = pygame.font.Font(cfg.FONT_MONO_PATH, 11)
    except Exception:
        title_font = pygame.font.SysFont("monospace", 44)
        subtitle_font = pygame.font.SysFont("monospace", 15)
        feature_font = pygame.font.SysFont("monospace", 14)
        status_font = pygame.font.SysFont("monospace", 13)
        skip_font = pygame.font.SysFont("monospace", 11)
        
    features = [
        "Interactive Graph Editor & Manipulation",
        "13+ Animated Algorithms (BFS, Dijkstra, Kruskal...)",
        "Advanced Exporters (GraphML, GEXF, DOT, CSV, GIF)",
        "Real-time Topological & Metric Properties Analysis",
        "Dynamic Plugin Loading & Keyboard Navigation Mode"
    ]
    
    total_frames = 120 # 2 seconds at 60 FPS
    frame = 0
    fade_frames = 15
    skipped = False
    
    while frame < total_frames and not skipped:
        # Event handling
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                import sys
                sys.exit()
            elif event.type in (pygame.KEYDOWN, pygame.MOUSEBUTTONDOWN):
                # Press any key or click to skip loading immediately
                skipped = True
                break
                
        if skipped:
            break
            
        progress = frame / total_frames
        
        # Decide status text
        if progress < 0.25:
            status_text = "Loading system configurations..."
        elif progress < 0.55:
            status_text = "Scanning plugins directory..."
        elif progress < 0.85:
            status_text = "Initializing canvas & UI components..."
        else:
            status_text = "Starting SimuGraph engine..."
            
        # Draw on a temp surface for smooth alpha fading
        splash_surf = pygame.Surface((w, h))
        splash_surf.fill((18, 18, 28)) # match theme bg
        
        # 1. Left side: Draw banner
        splash_surf.blit(banner_surf, (0, 0))
        
        # Optional overlay gradient on the banner border to blend left & right halves
        blend_w = 40
        for i in range(blend_w):
            alpha = int(255 * (i / blend_w))
            blend_col = (18, 18, 28, alpha)
            pygame.draw.line(splash_surf, blend_col, (left_w - blend_w + i, 0), (left_w - blend_w + i, h))

        # 2. Right side content
        right_start_x = left_w + 50
        
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
            # Bullet point symbol
            pygame.draw.rect(splash_surf, (90, 160, 255), (right_start_x, bullet_y + 5, 6, 6))
            feat_surf = feature_font.render(feat, True, (200, 205, 225))
            splash_surf.blit(feat_surf, (right_start_x + 18, bullet_y))
            bullet_y += 35
            
        # 3. Progress / Loading bar at bottom right
        bar_x = right_start_x
        bar_y = h - 220
        bar_w = w - bar_x - 50
        bar_h = 8
        
        # Status text
        status_surf = status_font.render(status_text, True, (130, 135, 165))
        splash_surf.blit(status_surf, (bar_x, bar_y - 25))
        
        # Progress percent
        pct_surf = status_font.render(f"{int(progress * 100)}%", True, (90, 160, 255))
        splash_surf.blit(pct_surf, (bar_x + bar_w - pct_surf.get_width(), bar_y - 25))
        
        # Draw track
        pygame.draw.rect(splash_surf, (30, 30, 45), (bar_x, bar_y, bar_w, bar_h), border_radius=4)
        
        # Draw progress fill
        fill_w = int(bar_w * progress)
        if fill_w > 0:
            fill_rect = pygame.Rect(bar_x, bar_y, fill_w, bar_h)
            draw_gradient_line(splash_surf, (90, 160, 255), (180, 120, 255), fill_rect)
            
        # Draw skip label
        skip_surf = skip_font.render("Press SPACE or click to skip", True, (80, 85, 110))
        splash_surf.blit(skip_surf, (bar_x + (bar_w - skip_surf.get_width()) // 2, h - 80))
        
        # Apply fade-in and fade-out alpha overlays
        alpha = 255
        if frame < fade_frames:
            # Fade-in
            alpha = int(255 * (frame / fade_frames))
        elif frame > total_frames - fade_frames:
            # Fade-out
            alpha = int(255 * ((total_frames - frame) / fade_frames))
            
        if alpha < 255:
            # Create a fading copy
            splash_surf.set_alpha(alpha)
            
        screen.fill((18, 18, 28))
        screen.blit(splash_surf, (0, 0))
        pygame.display.flip()
        
        frame += 1
        clock.tick(60)
        
    # Draw a quick final fade out if skipped
    if skipped:
        fade_out_surf = screen.copy()
        for f in range(fade_frames, 0, -1):
            alpha = int(255 * (f / fade_frames))
            fade_out_surf.set_alpha(alpha)
            screen.fill((18, 18, 28))
            screen.blit(fade_out_surf, (0, 0))
            pygame.display.flip()
            clock.tick(60)
