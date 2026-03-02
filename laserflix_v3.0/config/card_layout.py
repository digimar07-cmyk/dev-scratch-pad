"""
card_layout.py
==============
Constantes de layout do grid de cards da tela principal.

EDITE APENAS ESTE ARQUIVO para ajustar o visual dos cards.
Não é necessário mexer em nenhum outro .py.

  COLS     → quantos cards cabem por linha
  CARD_W   → largura de cada card em pixels
  CARD_H   → altura total de cada card em pixels
  COVER_H  → altura da imagem/capa dentro do card
  CARD_PAD → espaçamento (gap) entre os cards em pixels

Dica rápida de proporção:
  - COVER_H deve ficar entre 40% e 50% de CARD_H
  - CARD_W  deve ser no mínimo CARD_H * 0.45 para não ficar muito estreito
"""

# ---------------------------------------------------------------------------
# ✨ EDITE AQUI ✨
# ---------------------------------------------------------------------------

COLS     = 6      # colunas por linha  (ex: 4, 5, 6, 7)
CARD_W   = 200    # largura do card    (ex: 180, 200, 220, 240)
CARD_H   = 410    # altura do card     (ex: 380, 410, 440, 480)
COVER_H  = 180    # altura da capa     (ex: 160, 180, 200, 220)
CARD_PAD = 8      # gap entre cards    (ex: 5, 8, 10, 12)
