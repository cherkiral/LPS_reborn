from sqlalchemy import or_, and_, not_, cast, String
from sqlalchemy.sql import sqltypes

def apply_filters(query, model, filter_criteria):
    conditions = []

    for field, value in filter_criteria.items():
        if hasattr(model, field):
            column = getattr(model, field)

            # Check if the column is a DateTime type
            is_datetime = isinstance(column.type, sqltypes.DateTime)

            if isinstance(value, dict):
                for filter_type, filter_value in value.items():
                    if filter_type == 'eq':
                        conditions.append(column == filter_value)
                    elif filter_type == 'neq':
                        conditions.append(column != filter_value)
                    elif filter_type in ['contains', 'ncontains', 'begins_with', 'nbegins_with', 'ends_with', 'nends_with']:
                        # Cast DateTime to string for these filters
                        if is_datetime:
                            column = cast(column, String)

                        if filter_type == 'contains':
                            conditions.append(column.contains(filter_value))
                        elif filter_type == 'ncontains':
                            conditions.append(not_(column.contains(filter_value)))
                        elif filter_type == 'begins_with':
                            conditions.append(column.like(f'{filter_value}%'))
                        elif filter_type == 'nbegins_with':
                            conditions.append(not_(column.like(f'{filter_value}%')))
                        elif filter_type == 'ends_with':
                            conditions.append(column.like(f'%{filter_value}'))
                        elif filter_type == 'nends_with':
                            conditions.append(not_(column.like(f'%{filter_value}')))
                    elif filter_type == 'is_empty':
                        conditions.append(or_(column == None, column == ''))
                    elif filter_type == 'is_not_empty':
                        conditions.append(and_(column != None, column != ''))
            else:
                conditions.append(column == value)

    return query.filter(and_(*conditions))


def apply_transformers(query, model, transformers):
    if transformers.get('distinct'):
        query = query.distinct(model.user_id)
    return query

