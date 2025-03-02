import { Vehicle } from '../mongodb/models/vehicle';
import { QueryBuilder } from '../sql/queryBuilder';

export class DataSynchronizer {
  constructor(dbManager) {
    this.db = dbManager;
    this.queryBuilder = new QueryBuilder();
  }

  // Sync vehicles with configurable batch size and delay
  async syncVehicles(batchSize = 100, delayMs = 1000) {
    try {
      // Get total count from SQL
      const countQuery = this.queryBuilder
        .select('COUNT(*) as count')
        .from('Vehicles')
        .getQuery();
      
      const { recordset } = await this.db.sql.request().query(countQuery.text);
      const totalRecords = recordset[0].count;
      
      // Calculate number of batches
      const batches = Math.ceil(totalRecords / batchSize);
      
      for (let i = 0; i < batches; i++) {
        // Get batch of vehicles from SQL
        const query = this.queryBuilder
          .select('*')
          .from('Vehicles')
          .orderBy('Id')
          .offset(i * batchSize)
          .limit(batchSize)
          .getQuery();
        
        const { recordset: vehicles } = await this.db.sql.request().query(query.text);
        
        // Process each vehicle
        for (const sqlVehicle of vehicles) {
          await this.syncVehicle(sqlVehicle);
        }
        
        // Add delay between batches
        if (i < batches - 1) {
          await new Promise(resolve => setTimeout(resolve, delayMs));
        }
      }
      
      console.log(`Synced ${totalRecords} vehicles successfully`);
    } catch (error) {
      console.error('Error syncing vehicles:', error);
      throw error;
    }
  }

  // Sync a single vehicle
  async syncVehicle(sqlVehicle) {
    try {
      // Map SQL fields to MongoDB schema
      const vehicleData = {
        model: sqlVehicle.Model,
        year: sqlVehicle.Year,
        type: sqlVehicle.Type.toLowerCase(),
        manufacturer: sqlVehicle.Manufacturer,
        sqlId: sqlVehicle.Id,
        specs: {
          range: sqlVehicle.Range,
          batteryCapacity: sqlVehicle.BatteryCapacity,
          chargingTime: sqlVehicle.ChargingTime,
          acceleration: sqlVehicle.Acceleration,
          topSpeed: sqlVehicle.TopSpeed,
          power: sqlVehicle.Power,
          torque: sqlVehicle.Torque
        },
        pricing: {
          base: sqlVehicle.BasePrice,
          currency: sqlVehicle.Currency || 'USD'
        },
        availability: {
          status: sqlVehicle.AvailabilityStatus,
          quantity: sqlVehicle.StockQuantity
        },
        'metadata.lastSync': new Date()
      };

      // Update or create vehicle in MongoDB
      await Vehicle.findOneAndUpdate(
        { sqlId: sqlVehicle.Id },
        vehicleData,
        { upsert: true, new: true }
      );

    } catch (error) {
      console.error(`Error syncing vehicle ${sqlVehicle.Id}:`, error);
      throw error;
    }
  }

  // Verify data consistency
  async verifyConsistency() {
    try {
      // Get counts from both databases
      const sqlQuery = this.queryBuilder
        .select('COUNT(*) as count')
        .from('Vehicles')
        .getQuery();
      
      const [sqlCount, mongoCount] = await Promise.all([
        this.db.sql.request().query(sqlQuery.text),
        Vehicle.countDocuments()
      ]);

      const inconsistencies = {
        countMismatch: sqlCount.recordset[0].count !== mongoCount,
        sqlCount: sqlCount.recordset[0].count,
        mongoCount: mongoCount,
        details: []
      };

      // Check individual records if counts match
      if (!inconsistencies.countMismatch) {
        const sqlVehicles = await this.db.sql.request().query('SELECT Id, Model, Year FROM Vehicles');
        
        for (const sqlVehicle of sqlVehicles.recordset) {
          const mongoVehicle = await Vehicle.findOne({ sqlId: sqlVehicle.Id });
          
          if (!mongoVehicle || mongoVehicle.model !== sqlVehicle.Model) {
            inconsistencies.details.push({
              sqlId: sqlVehicle.Id,
              sql: sqlVehicle,
              mongo: mongoVehicle
            });
          }
        }
      }

      return inconsistencies;
    } catch (error) {
      console.error('Error verifying consistency:', error);
      throw error;
    }
  }

  // Repair inconsistencies
  async repairInconsistencies() {
    try {
      const inconsistencies = await this.verifyConsistency();
      
      if (inconsistencies.details.length > 0) {
        for (const item of inconsistencies.details) {
          await this.syncVehicle(item.sql);
        }
        
        console.log(`Repaired ${inconsistencies.details.length} inconsistencies`);
      }
      
      return inconsistencies;
    } catch (error) {
      console.error('Error repairing inconsistencies:', error);
      throw error;
    }
  }
}
