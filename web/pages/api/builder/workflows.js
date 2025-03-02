import { connectToDatabase } from '../../../lib/mongodb';

export default async function handler(req, res) {
  const { db } = await connectToDatabase();
  const collection = db.collection('workflows');

  switch (req.method) {
    case 'GET':
      try {
        const workflows = await collection.find({}).toArray();
        res.status(200).json(workflows);
      } catch (error) {
        console.error('Error fetching workflows:', error);
        res.status(500).json({ error: 'Internal server error' });
      }
      break;

    case 'POST':
      try {
        const { name, description, steps } = req.body;
        
        if (!name || !steps) {
          return res.status(400).json({ error: 'Name and steps are required' });
        }

        const workflow = {
          name,
          description,
          steps,
          metrics: {
            executions: 0,
            failures: 0,
            avgDuration: 0
          },
          createdAt: new Date(),
          updatedAt: new Date()
        };

        const result = await collection.insertOne(workflow);
        res.status(201).json({ ...workflow, id: result.insertedId });
      } catch (error) {
        console.error('Error creating workflow:', error);
        res.status(500).json({ error: 'Internal server error' });
      }
      break;

    default:
      res.status(405).json({ error: 'Method not allowed' });
  }
}
