import { sqlTypes } from './index';

export class QueryBuilder {
  constructor() {
    this.query = '';
    this.params = [];
    this.paramIndex = 0;
  }

  select(columns = ['*']) {
    this.query = `SELECT ${Array.isArray(columns) ? columns.join(', ') : columns}`;
    return this;
  }

  from(table) {
    this.query += ` FROM ${table}`;
    return this;
  }

  where(conditions) {
    if (Object.keys(conditions).length === 0) return this;

    this.query += ' WHERE';
    Object.entries(conditions).forEach(([key, value], index) => {
      if (index > 0) this.query += ' AND';
      
      const paramName = `p${this.paramIndex++}`;
      this.query += ` ${key} = @${paramName}`;
      this.params.push({
        name: paramName,
        value,
        type: this.inferSqlType(value)
      });
    });

    return this;
  }

  join(table, conditions) {
    this.query += ` JOIN ${table} ON`;
    Object.entries(conditions).forEach(([key, value], index) => {
      if (index > 0) this.query += ' AND';
      this.query += ` ${key} = ${value}`;
    });
    return this;
  }

  leftJoin(table, conditions) {
    this.query += ` LEFT JOIN ${table} ON`;
    Object.entries(conditions).forEach(([key, value], index) => {
      if (index > 0) this.query += ' AND';
      this.query += ` ${key} = ${value}`;
    });
    return this;
  }

  orderBy(column, direction = 'ASC') {
    this.query += ` ORDER BY ${column} ${direction}`;
    return this;
  }

  groupBy(columns) {
    this.query += ` GROUP BY ${Array.isArray(columns) ? columns.join(', ') : columns}`;
    return this;
  }

  having(conditions) {
    if (Object.keys(conditions).length === 0) return this;

    this.query += ' HAVING';
    Object.entries(conditions).forEach(([key, value], index) => {
      if (index > 0) this.query += ' AND';
      
      const paramName = `p${this.paramIndex++}`;
      this.query += ` ${key} = @${paramName}`;
      this.params.push({
        name: paramName,
        value,
        type: this.inferSqlType(value)
      });
    });

    return this;
  }

  limit(count) {
    this.query += ` TOP ${count}`;
    return this;
  }

  offset(count) {
    this.query += ` OFFSET ${count} ROWS`;
    return this;
  }

  insert(table, data) {
    const columns = Object.keys(data);
    const values = Object.values(data);
    const paramNames = values.map((_, i) => `@p${this.paramIndex + i}`);

    this.query = `INSERT INTO ${table} (${columns.join(', ')}) VALUES (${paramNames.join(', ')})`;

    values.forEach((value, index) => {
      this.params.push({
        name: `p${this.paramIndex++}`,
        value,
        type: this.inferSqlType(value)
      });
    });

    return this;
  }

  update(table, data, conditions) {
    this.query = `UPDATE ${table} SET`;

    Object.entries(data).forEach(([key, value], index) => {
      if (index > 0) this.query += ',';
      
      const paramName = `p${this.paramIndex++}`;
      this.query += ` ${key} = @${paramName}`;
      this.params.push({
        name: paramName,
        value,
        type: this.inferSqlType(value)
      });
    });

    if (conditions) {
      this.where(conditions);
    }

    return this;
  }

  delete(table, conditions) {
    this.query = `DELETE FROM ${table}`;
    if (conditions) {
      this.where(conditions);
    }
    return this;
  }

  inferSqlType(value) {
    switch (typeof value) {
      case 'string':
        return sqlTypes.NVarChar;
      case 'number':
        return Number.isInteger(value) ? sqlTypes.Int : sqlTypes.Float;
      case 'boolean':
        return sqlTypes.Bit;
      case 'object':
        if (value instanceof Date) return sqlTypes.DateTime;
        if (value === null) return sqlTypes.NVarChar;
        return sqlTypes.NVarChar;
      default:
        return sqlTypes.NVarChar;
    }
  }

  getQuery() {
    return {
      text: this.query,
      params: this.params
    };
  }
}
