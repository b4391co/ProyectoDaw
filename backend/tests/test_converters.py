import pytest
from datetime import datetime
from app.converters import DataConverter

def test_to_csv_empty_data():
    """Prueba la conversión de una lista vacía a CSV."""
    converter = DataConverter()
    result = converter.to_csv([])
    assert result == ""

def test_to_csv_single_row():
    """Prueba la conversión de una sola fila a CSV."""
    converter = DataConverter()
    data = [{"id": 1, "name": "Test", "value": 100}]
    result = converter.to_csv(data)
    expected = "id,name,value\n1,Test,100\n"
    assert result == expected

def test_to_csv_multiple_rows():
    """Prueba la conversión de múltiples filas a CSV."""
    converter = DataConverter()
    data = [
        {"id": 1, "name": "Test1", "value": 100},
        {"id": 2, "name": "Test2", "value": 200}
    ]
    result = converter.to_csv(data)
    expected = "id,name,value\n1,Test1,100\n2,Test2,200\n"
    assert result == expected

def test_to_csv_custom_delimiter():
    """Prueba la conversión a CSV con delimitador personalizado."""
    converter = DataConverter()
    data = [{"id": 1, "name": "Test", "value": 100}]
    result = converter.to_csv(data, delimiter=';')
    expected = "id;name;value\n1;Test;100\n"
    assert result == expected

def test_to_json_empty_data():
    """Prueba la conversión de una lista vacía a JSON."""
    converter = DataConverter()
    result = converter.to_json([])
    assert result == "[]"

def test_to_json_single_row():
    """Prueba la conversión de una sola fila a JSON."""
    converter = DataConverter()
    data = [{"id": 1, "name": "Test", "value": 100}]
    result = converter.to_json(data)
    expected = '[{"id": 1, "name": "Test", "value": 100}]'
    assert result == expected

def test_to_json_pretty():
    """Prueba la conversión a JSON con formato bonito."""
    converter = DataConverter()
    data = [{"id": 1, "name": "Test", "value": 100}]
    result = converter.to_json(data, pretty=True)
    expected = '[\n  {\n    "id": 1,\n    "name": "Test",\n    "value": 100\n  }\n]'
    assert result == expected

def test_convert_csv():
    """Prueba la conversión genérica a CSV."""
    converter = DataConverter()
    data = [{"id": 1, "name": "Test", "value": 100}]
    result = converter.convert(data, "csv")
    expected = "id,name,value\n1,Test,100\n"
    assert result == expected

def test_convert_json():
    """Prueba la conversión genérica a JSON."""
    converter = DataConverter()
    data = [{"id": 1, "name": "Test", "value": 100}]
    result = converter.convert(data, "json")
    expected = '[{"id": 1, "name": "Test", "value": 100}]'
    assert result == expected

def test_convert_invalid_format():
    """Prueba la conversión con formato inválido."""
    converter = DataConverter()
    data = [{"id": 1, "name": "Test", "value": 100}]
    with pytest.raises(ValueError):
        converter.convert(data, "invalid")

def test_format_datetime():
    """Prueba el formateo de fechas."""
    converter = DataConverter()
    dt = datetime(2024, 1, 1, 12, 0, 0)
    result = converter.format_datetime(dt)
    assert result == "2024-01-01T12:00:00" 