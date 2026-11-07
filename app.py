import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
import logging
import sqlite3
from datetime import datetime

DB_path = 'history.db'

logging.basicConfig(
    level = logging.INFO, 
    format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers = [
        logging.FileHandler('app.log', encoding = 'utf-8'),
        logging.StreamHandler()
        ]
)

logger = logging.getLogger(__name__)

def init_db() -> None:
    try:
        with sqlite3.connect(DB_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS requests(
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                start REAL NOT NULL,
                end REAL NOT NULL,
                step REAL NOT NULL
                )
                """)
            conn.commit()
            logger.info('База данных успешно инициализирована')
    except sqlite3.Error as e:
        logger.error('Ошибка инициализации БД: %s', e, exc_info=True)

def save_requests(start: float, end: float, step: float) -> None:
    try:
        with sqlite3.connect(DB_path) as conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO requests (timestamp, start, end, step) VALUES (?, ?, ?, ?)",
                (datetime.now().isoformat(), start, end, step)
                )
            conn.commit()
        logging.info('Запрос сохранен: start=%.2f, end=%.2f, step=%.2f',
                     start,
                     end,
                     step)
    except sqlite3.Error as e:
            logger.error('Ошибка при сохранении запроса: %s', e, exc_info=True)

def load_history() -> list:
    try:
        with sqlite3.connect(DB_path) as conn:
            cursor = conn.cursor()
            cursor.execute(
                    'SELECT timestamp, start, end, step FROM requests ORDER BY id DESC LIMIT 5'
                    )
            return cursor.fetchall()
    except sqlite3.Error as e:
        logger.error('Ошибка при чтении истории: %s', e, exc_info=True)
        return []

def plot_functions(start: float, end: float, step: float) -> plt.figure:
    if step <= 0:
        raise ValueError('Шаг должен быть положительным!')
    if start >= end:
        raise ValueError('Начало диапазона не может быть меньше конца!')
    x = np.arange(start, end + step/1, step)
    y_sin = np.sin(x)
    y_cos = np.cos(x)

    fig, ax = plt.subplots(figsize = (8,5))
    ax.plot(x, y_sin, color = 'blue', linestyle = '--', marker = 'o', label = 'Функция sin')
    ax.plot(x, y_cos, color = 'red', linestyle = '-', marker = 's', label = 'Функция cos')

    ax.set_title('Графики функций sin и cos')
    ax.set_xlabel('Значения x, радианы')
    ax.set_ylabel('Значения y')
    ax.grid(True)
    ax.legend(loc = 'upper left')

    return fig

def main() -> None:
    st.set_page_config(page_title = 'Тренажер', layout = 'centered')
    st.title('Исследования колебаний по физике')

    st.sidebar.header('Параметры диапазона')
    start = st.sidebar.number_input('Начало диапазона', value = -3.14, step = 0.5)
    end = st.sidebar.number_input('Конец диапазона', value = 3.14, step = 0.5)
    step = st.sidebar.number_input('Шаг', value = 0.5, step = 0.1)

    if st.sidebar.button('Построить график'):
        try:
            fig = plot_functions(start, end, step)
            st.pyplot(fig)
            save_requests(start, end, step)
        except ValueError as e:
            st.error(f'Ошибка ввода: {e}')
            logger.warning('Некорректный ввод: %s', e)
        except Exception:
            st.error('Произошла непредвиденная ошибка')
            logger.exception('Неожиданная ошибка при построении графика')

    st.sidebar.subheader('Последние запросы')
    history = load_history()
    if history:
        for ts, s, e, stp in history:
            st.sidebar.text(f'{ts[:19]} | [{s}; {e}] шаг {stp}')
    else:
        st.sidebar.text('История пуста')

if __name__ == '__main__':
    init_db()
    main()
