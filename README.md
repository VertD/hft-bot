# HFT Bot for BTC/USDT Futures

## Описание проекта

Проект реализует **HFT бота** для торговли фьючерсами BTC/USDT.  
Основная цель — моделировать и тестировать торговлю с ограничениями на синтетических данных и в продовом режиме через Sandbox ccxt.

Бот использует **лимитные ордера (Limit/Maker)** для минимизации комиссии и исключения проскальзывания (slippage).

---

## Математическая модель

### Переменные и определения

| Переменная | Описание |
|------------|----------|
| `capital` | Текущий капитал (USD) |
| `leverage` | Плечо позиции |
| `P_min` | Нижняя граница прогноза цены |
| `P_max` | Верхняя граница прогноза цены |
| `position_notional` | Стоимость позиции в USD |
| `Q` | Количество базового актива (BTC) для ордера |
| `maker_fee` | Комиссия биржи для лимитного ордера |
| `max_position_usdt` | Лимит максимальной позиции по капиталу |
| `net_profit` | Чистая прибыль по ордеру |

### Основные формулы

#### 1. Расчёт объёма позиции

$$
usable\_capital = \min(capital, \frac{max\_position\_usdt}{leverage})
$$

$$
position\_notional = usable\_capital \cdot leverage
$$

$$
Q = \frac{position\_notional}{P\_min}
$$

#### 2. Чистая прибыль по лимитным ордерам

$$
gross\_profit = Q \cdot (P\_max - P\_min)
$$

$$
total\_fees = position\_notional \cdot (maker\_fee \cdot 2)
$$

$$
net\_profit = gross\_profit - total\_fees
$$

> Примечание: slippage для лимитных ордеров не применяется, так как они исполняются только по цене или лучше.

#### 3. Минимальный рентабельный спред

$$
required\_spread = 2 \cdot maker\_fee + min\_profit
$$

Ордер считается выгодным только если прогнозный спред выше `required_spread`.

---

## Ограничения и риски

1. **Execution latency**
   - Время между сигналом и исполнением 5–50ms

2. **Position limits**
   - Биржа ограничивает плечо и максимальную позицию

3. **Rate limits API**
   - Binance: 1200 requests/min
   - Для HFT частота обновления ордеров требует оптимизации (batch modify, co-location)

---

## Структура проекта

hft-bot/
├─ src/
│ ├─ strategy.py # Продовый бот (Sandbox ccxt), лимитные ордера, фиксированное плечо
│ ├─ simulator.py # Оффлайн симулятор на синтетике с математической моделью
│ ├─ utils.py # Генерация тиков, расчёт объёмов и прибыли
├─ main.py # Запуск продового или оффлайн режима
├─ config.py # Ключи API, плечо, капитал, базовая директория
├─ README.md

---

## Запуск

### Offline режим (тест на синтетике)

```bash
python main.py
```

Генерируются 864000 тиков по умолчанию
Результаты сохраняются в results/sim_history.json
Строится график equity curve results/equity_curve.png
Выводится общая прибыль: Total simulated profit: XXX.XX USD
