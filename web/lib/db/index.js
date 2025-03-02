import { connectToMongoDB } from '../mongodb';
import { QueryBuilder } from '../sql/queryBuilder';
import sql from 'mssql';

export class DatabaseManager {
  constructor() {
    this.mongo = null;
    this.sql = null;
    this.queryBuilder = new QueryBuilder();
  }

  async connect() {
    // Connect to MongoDB
    const { db } = await connectToMongoDB();
    this.mongo = db;

    // Connect to SQL Server
    this.sql = await sql.connect({
      user: process.env.SQL_USER,
      password: process.env.SQL_PASSWORD,
      server: process.env.SQL_SERVER,
      database: process.env.SQL_DATABASE,
      options: {
        encrypt: true,
        trustServerCertificate: true
      }
    });
  }

  // Sync data between MongoDB and SQL Server
  async syncData(collection, table, mapping) {
    try {
      // Get data from SQL
      const sqlQuery = this.queryBuilder
        .select('*')
        .from(table)
        .getQuery();
      
      const sqlResult = await this.sql.request().query(sqlQuery.text);
      const sqlData = sqlResult.recordset;

      // Get data from MongoDB
      const mongoData = await this.mongo.collection(collection).find().toArray();

      // Find records to sync
      for (const sqlRecord of sqlData) {
        const mongoRecord = mongoData.find(m => m.sqlId === sqlRecord.id);

        if (!mongoRecord) {
          // Create in MongoDB
          const mappedData = {};
          for (const [mongoField, sqlField] of Object.entries(mapping)) {
            mappedData[mongoField] = sqlRecord[sqlField];
          }
          mappedData.sqlId = sqlRecord.id;

          await this.mongo.collection(collection).insertOne(mappedData);
        } else {
          // Update in MongoDB if needed
          const updates = {};
          let needsUpdate = false;

          for (const [mongoField, sqlField] of Object.entries(mapping)) {
            if (mongoRecord[mongoField] !== sqlRecord[sqlField]) {
              updates[mongoField] = sqlRecord[sqlField];
              needsUpdate = true;
            }
          }

          if (needsUpdate) {
            await this.mongo.collection(collection).updateOne(
              { sqlId: sqlRecord.id },
              { $set: updates }
            );
          }
        }
      }

      // Handle deletes
      const sqlIds = sqlData.map(record => record.id);
      await this.mongo.collection(collection).deleteMany({
        sqlId: { $nin: sqlIds }
      });

    } catch (error) {
      console.error('Error syncing data:', error);
      throw error;
    }
  }

  // Execute query on both databases
  async executeHybridQuery({ sql: sqlQuery, mongo: mongoQuery }) {
    try {
      const [sqlResult, mongoResult] = await Promise.all([
        sqlQuery ? this.sql.request().query(sqlQuery) : null,
        mongoQuery ? this.mongo.collection(mongoQuery.collection)[mongoQuery.operation](
          mongoQuery.query,
          mongoQuery.options
        ) : null
      ]);

      return {
        sql: sqlResult?.recordset || null,
        mongo: mongoResult || null
      };
    } catch (error) {
      console.error('Error executing hybrid query:', error);
      throw error;
    }
  }

  // Transaction across both databases
  async hybridTransaction(callback) {
    const sqlTransaction = new sql.Transaction(this.sql);
    const session = this.mongo.client.startSession();

    try {
      await sqlTransaction.begin();
      await session.startTransaction();

      await callback({
        sql: sqlTransaction,
        mongo: session
      });

      await sqlTransaction.commit();
      await session.commitTransaction();
    } catch (error) {
      await sqlTransaction.rollback();
      await session.abortTransaction();
      throw error;
    } finally {
      session.endSession();
    }
  }

  async close() {
    if (this.mongo) {
      await this.mongo.client.close();
    }
    if (this.sql) {
      await this.sql.close();
    }
  }
}
