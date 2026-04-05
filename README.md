# HFT Bot for BTC/USDT Futures

## Описание проекта

Проект реализует **HFT бота** для торговли фьючерсами BTC/USDT.  
Используются **лимитные ордера (Limit/Maker)** для минимизации комиссии и исключения соскальзывания (slippage).  

---

## Математическая модель

### Основные переменные

| Переменная | Описание |
|------------|----------|
| capital | Текущий капитал (USD) |
| leverage | Плечо позиции |
| P_min | Нижняя граница прогноза цены |
| P_max | Верхняя граница прогноза цены |
| position_notional | Стоимость позиции в USD |
| Q | Количество базового актива (BTC) для ордера |
| maker_fee | Комиссия биржи для лимитного ордера |
| max_position_usdt | Лимит максимальной позиции по капиталу |
| net_profit | Чистая прибыль по ордеру |

### Расчёт объёма позиции

$$
\text{usable\_capital} = \min(\text{capital}, \frac{\text{max\_position\_usdt}}{\text{leverage}})
$$

$$
\text{position\_notional} = \text{usable\_capital} \cdot \text{leverage}
$$

$$
Q = \frac{\text{position\_notional}}{P_{\min}}
$$

### Чистая прибыль по лимитным ордерам

$$
\text{gross\_profit} = Q \cdot (P_{\max} - P_{\min})
$$

$$
\text{total\_fees} = \text{position\_notional} \cdot (2 \cdot \text{maker\_fee})
$$

$$
\text{net\_profit} = \text{gross\_profit} - \text{total\_fees}
$$

> Примечание: slippage для лимитных ордеров не применяется.

### Минимальный рентабельный спред

$$
required\_spread = 2 \cdot \text{maker\_fee} + min\_profit
$$

---

## Ограничения и риски

1. **Execution latency** — задержка между сигналом и исполнением 5–50 ms  
2. **Position limits** — биржа ограничивает плечо и максимальную позицию  
3. **Rate limits API** — Binance: 1200 requests/min, HFT требует частого обновления ордеров

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
