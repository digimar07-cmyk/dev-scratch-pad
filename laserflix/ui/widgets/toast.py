# -*- coding: utf-8 -*-
"""
Widget de notificação toast
"""

import tkinter as tk

class Toast:
    """Notificação temporária na tela"""
    
    def __init__(self, parent, message, duration=3000):
        self.parent = parent
        self.message = message
        self.duration = duration
    
    def show(self):
        """Exibe o toast"""
        pass
