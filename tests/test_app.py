import pytest
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from app import init_db, save_requests, load_history, plot_functions

@pytest.fixture
def temp_db(tmp_path, monkeypatch):
    db_file = tmp_path/'test_history.db'
    monkeypatch.setattr('app.DB_path', str(db_file))
    init_db()
    yield str(db_file)

def test_plot_func_invalid_step():
    with pytest.raises(ValueError, match = 'Шаг должен быть положительным!'):
        plot_functions(-3, 3, 0)

def test_save_and_load_history(temp_db):
    save_requests(-3.14, 3.14, 0.5)

    history = load_history()

    assert len(history) > 0
    assert history[0][1] == -3.14  # start
    assert history[0][2] == 3.14   # end
    assert history[0][3] == 0.5    # step