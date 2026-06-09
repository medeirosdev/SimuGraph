"""
settings.py — All visual and runtime constants for SimuGraph.

Themes are plain dicts so they can be swapped at runtime with a single
reassignment: `simugraph.settings.THEME = THEMES["light"]`.
"""

from __future__ import annotations

# ---------------------------------------------------------------------------
# Window
# ---------------------------------------------------------------------------
WINDOW_TITLE = "SimuGraph"
WINDOW_W = 1400
WINDOW_H = 860
FPS = 60

# ---------------------------------------------------------------------------
# Fonts
# ---------------------------------------------------------------------------
FONT_MONO_PATH = "assets/fonts/JetBrainsMono.ttf"
FONT_SIZE_NODE = 13
FONT_SIZE_UI = 14
FONT_SIZE_HUD = 12
FONT_SIZE_TOOLTIP = 12

# ---------------------------------------------------------------------------
# Dark theme (default)
# ---------------------------------------------------------------------------
DARK: dict = {
    # Canvas
    "bg":               (18, 18, 28),
    "grid":             (255, 255, 255, 18),
    "grid_major":       (255, 255, 255, 36),

    # Nodes
    "node_fill":        (60, 130, 220),
    "node_stroke":      (120, 180, 255),
    "node_hover":       (100, 200, 255),
    "node_selected":    (255, 200, 60),
    "node_pinned":      (180, 100, 255),
    "node_visited":     (80, 220, 120),
    "node_frontier":    (255, 160, 60),
    "node_path":        (255, 80, 160),
    "node_bridge_ap":   (255, 60, 60),    # articulation points
    "node_label":       (255, 255, 255),

    # Edges
    "edge":             (150, 155, 185),
    "edge_directed":    (200, 120, 255),
    "edge_selected":    (255, 200, 60),
    "edge_mst":         (80, 220, 160),
    "edge_bridge":      (255, 80, 80),
    "edge_weight_bg":   (30, 30, 50, 210),
    "edge_weight_text": (220, 220, 255),

    # UI chrome
    "sidebar_bg":       (22, 22, 36),
    "toolbar_bg":       (18, 18, 30),
    "inspector_bg":     (22, 22, 36),
    "panel_border":     (50, 55, 80),
    "accent":           (90, 160, 255),
    "accent_hover":     (120, 190, 255),
    "text":             (220, 220, 240),
    "text_dim":         (130, 135, 160),
    "hud_bg":           (15, 15, 25, 200),
    "tooltip_bg":       (30, 32, 50, 230),
    "context_bg":       (25, 25, 40),
    "context_hover":    (45, 50, 75),
    "minimap_bg":       (15, 15, 25, 200),
    "minimap_border":   (60, 65, 90),
    "minimap_viewport": (90, 160, 255, 80),
    "selection_box":    (90, 160, 255, 50),
    "selection_border": (90, 160, 255),
}

# ---------------------------------------------------------------------------
# Light theme
# ---------------------------------------------------------------------------
LIGHT: dict = {
    "bg":               (240, 242, 248),
    "grid":             (0, 0, 0, 20),
    "grid_major":       (0, 0, 0, 40),

    "node_fill":        (60, 130, 220),
    "node_stroke":      (30, 90, 180),
    "node_hover":       (80, 160, 240),
    "node_selected":    (220, 160, 0),
    "node_pinned":      (140, 60, 220),
    "node_visited":     (40, 180, 80),
    "node_frontier":    (220, 120, 20),
    "node_path":        (220, 40, 120),
    "node_bridge_ap":   (220, 30, 30),
    "node_label":       (20, 20, 40),

    "edge":             (110, 115, 150),
    "edge_directed":    (160, 80, 220),
    "edge_selected":    (220, 160, 0),
    "edge_mst":         (40, 180, 120),
    "edge_bridge":      (220, 50, 50),
    "edge_weight_bg":   (200, 205, 220, 220),
    "edge_weight_text": (40, 40, 80),

    "sidebar_bg":       (225, 228, 238),
    "toolbar_bg":       (210, 214, 228),
    "inspector_bg":     (225, 228, 238),
    "panel_border":     (180, 185, 210),
    "accent":           (50, 120, 220),
    "accent_hover":     (30, 100, 200),
    "text":             (30, 30, 60),
    "text_dim":         (100, 105, 130),
    "hud_bg":           (200, 205, 225, 210),
    "tooltip_bg":       (215, 218, 235, 240),
    "context_bg":       (225, 228, 238),
    "context_hover":    (200, 205, 225),
    "minimap_bg":       (200, 205, 225, 210),
    "minimap_border":   (160, 165, 195),
    "minimap_viewport": (50, 120, 220, 80),
    "selection_box":    (50, 120, 220, 50),
    "selection_border": (50, 120, 220),
}

# ---------------------------------------------------------------------------
# Colorblind-safe theme (Okabe-Ito palette)
# ---------------------------------------------------------------------------
COLORBLIND: dict = {
    **DARK,                              # inherit dark chrome
    "node_fill":        (0, 114, 178),   # blue
    "node_stroke":      (86, 180, 233),  # sky blue
    "node_hover":       (86, 180, 233),
    "node_selected":    (230, 159, 0),   # orange
    "node_visited":     (0, 158, 115),   # green
    "node_frontier":    (240, 228, 66),  # yellow
    "node_path":        (204, 121, 167), # pink
    "node_bridge_ap":   (213, 94, 0),    # vermillion
    "edge_directed":    (204, 121, 167),
    "edge_mst":         (0, 158, 115),
    "edge_bridge":      (213, 94, 0),
}

# ---------------------------------------------------------------------------
# SCC / graph-coloring palettes (distinct colors per group)
# ---------------------------------------------------------------------------
SCC_PALETTE: list[tuple[int, int, int]] = [
    (255, 100, 100),
    (100, 200, 100),
    (100, 150, 255),
    (255, 200, 80),
    (200, 100, 255),
    (80, 220, 220),
    (255, 140, 60),
    (160, 255, 140),
]

COLOR_PALETTE: list[tuple[int, int, int]] = [
    (255, 80,  80),
    (80,  180, 80),
    (80,  120, 255),
    (255, 180, 0),
    (200, 80,  255),
    (0,   200, 200),
    (255, 120, 40),
    (140, 255, 120),
    (255, 200, 200),
    (200, 255, 200),
]

# ---------------------------------------------------------------------------
# Active theme (mutable at runtime)
# ---------------------------------------------------------------------------
THEMES: dict[str, dict] = {
    "dark": DARK,
    "light": LIGHT,
    "colorblind": COLORBLIND,
}
ACTIVE_THEME_NAME: str = "dark"
THEME: dict = DARK          # alias used throughout the codebase


def set_theme(name: str) -> None:
    """Switch the active theme by name ('dark', 'light', 'colorblind')."""
    global THEME, ACTIVE_THEME_NAME
    if name not in THEMES:
        raise ValueError(f"Unknown theme {name!r}. Choose from {list(THEMES)}")
    ACTIVE_THEME_NAME = name
    THEME = THEMES[name]


# ---------------------------------------------------------------------------
# UI layout constants
# ---------------------------------------------------------------------------
SIDEBAR_W = 60       # left sidebar width  (px)
TOOLBAR_H = 36       # top toolbar height  (px)
INSPECTOR_W = 240    # right inspector width (px)
HUD_H = 28           # bottom status bar height (px)
MINIMAP_W = 200      # mini-map width (px)
MINIMAP_H = 140      # mini-map height (px)
MINIMAP_MARGIN = 10  # distance from bottom-right corner

# ---------------------------------------------------------------------------
# Node / edge defaults
# ---------------------------------------------------------------------------
NODE_RADIUS = 22
NODE_SNAP_GRID = 50   # world units for grid snapping

# ---------------------------------------------------------------------------
# Camera defaults
# ---------------------------------------------------------------------------
ZOOM_FACTOR_SCROLL = 1.1   # multiplier per scroll tick
ZOOM_FACTOR_KEY = 1.2      # multiplier per keyboard +/-
