# Layers — em qual camada o objeto existe
LAYER_WORLD    = 1  # tiles de colisão do mapa e objetos estáticos
LAYER_PLAYER   = 2  # jogador
LAYER_ENEMY    = 3  # reservado para NPCs/inimigos futuros
LAYER_TOOL     = 4  # collider de ferramenta ativa
LAYER_FARMABLE = 5  # tiles marcados como farmáveis

# Masks — quais layers este objeto detecta
MASK_PLAYER   = [LAYER_WORLD]    
MASK_TOOL     = [LAYER_FARMABLE] 
MASK_WORLD    = []               
MASK_FARMABLE = []               