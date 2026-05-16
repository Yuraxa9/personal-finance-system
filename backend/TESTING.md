# Тестирование

## Запуск unit тестов
```bash
pytest --cov=app --cov-report=term-missing
```

## Запуск фаззинг тестов
```bash
pytest tests/test_fuzz.py -v
```

## Покрытие
```bash
pytest --cov=app --cov-report=html
```
