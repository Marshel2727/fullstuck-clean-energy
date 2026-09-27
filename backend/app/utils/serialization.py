"""Shared serialization helpers."""
def row_data(row):
    return {column.name: getattr(row, column.name) for column in row.__table__.columns}
