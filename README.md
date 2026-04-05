# HFT Bot for BTC/USDT Futures

## Описание проекта

Этот проект реализует **HFT бота** для торговли фьючерсами BTC/USDT. Основная цель — моделировать и тестировать торговлю с ограничениями на синтетических данных и в продовом режиме (через Sandbox ccxt).

Бот использует **лимитные ордера (Limit/Maker)** для минимизации комиссии и исключения соскальзывания (slippage).

---

## Математическая модель

### Переменные и определения

| Переменная | Описание |
|------------|----------|
| `capital` | Текущий капитал (USD) |
| `leverage` | Плечо позиции |
| `Pmin` | Нижняя граница прогноза цены |
| `Pmax` | Верхняя граница прогноза цены |
| `position_notional` | Стоимость позиции в USD |
| `Q` | Количество базового актива (BTC) для ордера |
| `maker_fee` | Комиссия биржи для лимитного ордера |
| `max_position_usdt` | Лимит максимальной позиции по капиталу |
| `net_profit` | Чистая прибыль по ордеру |

### Основные формулы

1. **Расчёт объёма позиции:**
### 1. Расчёт объёма позиции

$$
\text{usable\_capital} = \min(\text{capital}, \frac{\text{max\_position\_usdt}}{\text{leverage}})
$$

$$
\text{position\_notional} = \text{usable\_capital} \cdot \text{leverage}
$$

$$
Q = \frac{\text{position\_notional}}{P_{\min}}
$$

### 2. Чистая прибыль по лимитным ордерам

$$
\text{gross\_profit} = Q \cdot (P_{\max} - P_{\min})
$$

$$
\text{total\_fees} = \text{position\_notional} \cdot (maker\_fee \cdot 2)
$$

$$
\text{net\_profit} = \text{gross\_profit} - \text{total\_fees}
$$
```
> Примечание: slippage для лимитных ордеров не применяется, так как они исполняются только по цене или лучше.

3. **Минимальный рентабельный спред:**

\[
required\_spread = 2 \cdot maker\_fee + min\_profit
\]

Только если текущий прогнозный спред выше `required_spread`, ордер считается выгодным.

---

## Ограничения и риски

1. **Execution latency**
   - Время между сигналом и исполнением 5–50ms

2. **Position limits**
   - Биржа ограничивает плечо и максимальную позицию

3. **Rate limits API**
   - Binance: 1200 requests/min, но HFT требует частого обновления ордеров

---
```
## Структура проекта
hft-bot/
├─ src/
│ ├─ strategy.py
│ ├─ simulator.py
│ ├─ utils.py
├─ main.py
├─ config.py
├─ README.md
```
- `strategy.py` — бот для продового режима (Sandbox ccxt), лимитные ордера, фиксированное плечо.
- `simulator.py` — оффлайн симулятор на синтетических данных с математической моделью.
- `utils.py` — генерация синтетических тиков и расчёт объёмов и прибыли.
- `main.py` — запускает либо продовый, либо оффлайн режим.
- `config.py` — содержит ключи API, плечо, капитал, базовую директорию для результатов.

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
