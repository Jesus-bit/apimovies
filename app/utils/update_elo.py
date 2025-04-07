def update_elo(player_a_elo, player_b_elo, result):
    k = 32  # Factor de escala K
    new_elo_a = player_a_elo + k * (result - 1 / (1 + 10 ** ((player_b_elo - player_a_elo) / 400)))
    new_elo_b = player_b_elo + k * ((1 - result) - 1 / (1 + 10 ** ((player_a_elo - player_b_elo) / 400)))
    return int(new_elo_a), int(new_elo_b)