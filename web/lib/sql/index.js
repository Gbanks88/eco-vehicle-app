import sql from 'mssql';

const config = {
  user: process.env.SQL_USER,
  password: process.env.SQL_PASSWORD,
  server: process.env.SQL_SERVER,
  database: process.env.SQL_DATABASE,
  options: {
    encrypt: true,
    trustServerCertificate: process.env.NODE_ENV !== 'production'
  },
  pool: {
    max: 10,
    min: 0,
    idleTimeoutMillis: 30000
  }
};

// SQL Server connection pool
let pool;

export async function connectToSQL() {
  try {
    if (!pool) {
      pool = await sql.connect(config);
    }
    return pool;
  } catch (err) {
    console.error('SQL Connection Error:', err);
    throw err;
  }
}

export async function executeQuery(query, params = []) {
  try {
    const pool = await connectToSQL();
    const request = pool.request();

    // Add parameters to request
    params.forEach(param => {
      request.input(param.name, param.type, param.value);
    });

    const result = await request.query(query);
    return result.recordset;
  } catch (err) {
    console.error('SQL Query Error:', err);
    throw err;
  }
}

export async function executeProcedure(procedure, params = []) {
  try {
    const pool = await connectToSQL();
    const request = pool.request();

    // Add parameters to request
    params.forEach(param => {
      request.input(param.name, param.type, param.value);
    });

    const result = await request.execute(procedure);
    return result.recordset;
  } catch (err) {
    console.error('SQL Procedure Error:', err);
    throw err;
  }
}

export async function beginTransaction() {
  try {
    const pool = await connectToSQL();
    const transaction = new sql.Transaction(pool);
    await transaction.begin();
    return transaction;
  } catch (err) {
    console.error('SQL Transaction Error:', err);
    throw err;
  }
}

export const sqlTypes = sql.TYPES;
