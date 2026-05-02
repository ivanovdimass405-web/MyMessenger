DARK_THEME = {
    'bg': '#17212b',
    'header': '#1f2c38',
    'sidebar': '#17212b',
    'chat_bg': '#0e1621',
    'my_msg': '#2b5278',
    'their_msg': '#182533',
    'text': '#ffffff',
    'text_secondary': '#a3b3c6',
    'accent': '#65b9f2',
    'online': '#6bc86b',
    'offline': '#a3b3c6'
}

LIGHT_THEME = {
    'bg': '#ffffff',
    'header': '#f0f0f0',
    'sidebar': '#fafafa',
    'chat_bg': '#f5f5f5',
    'my_msg': '#dcf8c5',
    'their_msg': '#ffffff',
    'text': '#000000',
    'text_secondary': '#666666',
    'accent': '#34b7f1',
    'online': '#31a24c',
    'offline': '#999999'
}

class ThemeManager:
    current_theme = 'dark'
    
    @classmethod
    def get_colors(cls):
        return DARK_THEME if cls.current_theme == 'dark' else LIGHT_THEME
    
    @classmethod
    def toggle(cls):
        cls.current_theme = 'light' if cls.current_theme == 'dark' else 'dark'
        return cls.get_colors()