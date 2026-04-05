import random


def generate_tick(base_price=60000):
    """
    Генерирует Pmin и Pmax для 10-секундного окна.
    Гарантирует Pmax > Pmin и реалистичный спред для HFT.
    """
    # p1 — стартовая точка
    p1 = base_price + random.uniform(-50, 50)
    # p2 — отклонение. Используем abs + константа, чтобы спред был всегда > 0
    p2 = p1 + random.uniform(5, 80)

    return round(min(p1, p2), 2), round(max(p1, p2), 2)


def calculate_order(Pmin, Pmax, capital, leverage, max_position_usdt):
    """
    Расчет объема позиции (Q) с учетом:
    1. Доступного капитала
    2. Плеча
    3. Лимита ликвидности стакана (max_position_usdt)
    """
    # usable_cap — сколько маржи мы можем выделить под сделку
    usable_cap = min(capital, max_position_usdt / leverage)

    # Номинальный объем позиции в USD
    position_notional = usable_cap * leverage

    # Количество актива (BTC)
    Q = position_notional / Pmin

    return Q, position_notional


def calc_net_profit(Q, position_notional, Pmin, Pmax, maker_fee, capital=None, max_drawdown_pct=0.1):
    """
    Расчет чистой прибыли для Maker-стратегии.
    Добавлен ограничитель убытков (Stop-loss logic) для симулятора.
    """
    gross_profit = Q * (Pmax - Pmin)

    total_fees = position_notional * (maker_fee * 2)

    net_profit = gross_profit - total_fees

    if capital is not None:
        max_loss = -capital * max_drawdown_pct
        return max(net_profit, max_loss)

    return net_profit