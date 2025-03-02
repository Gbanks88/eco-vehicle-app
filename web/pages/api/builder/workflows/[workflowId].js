import { ObjectId } from 'mongodb';
import { connectToDatabase } from '../../../../lib/mongodb';

export default async function handler(req, res) {
  const { db } = await connectToDatabase();
  const collection = db.collection('workflows');
  const { workflowId } = req.query;

  if (!ObjectId.isValid(workflowId)) {
    return res.status(400).json({ error: 'Invalid workflow ID' });
  }

  const _id = new ObjectId(workflowId);

  switch (req.method) {
    case 'GET':
      try {
        const workflow = await collection.findOne({ _id });
        if (!workflow) {
          return res.status(404).json({ error: 'Workflow not found' });
        }
        res.status(200).json(workflow);
      } catch (error) {
        console.error('Error fetching workflow:', error);
        res.status(500).json({ error: 'Internal server error' });
      }
      break;

    case 'PUT':
      try {
        const { name, description, steps } = req.body;
        const update = {
          $set: {
            ...(name && { name }),
            ...(description && { description }),
            ...(steps && { steps }),
            updatedAt: new Date()
          }
        };

        const result = await collection.findOneAndUpdate(
          { _id },
          update,
          { returnDocument: 'after' }
        );

        if (!result.value) {
          return res.status(404).json({ error: 'Workflow not found' });
        }

        res.status(200).json(result.value);
      } catch (error) {
        console.error('Error updating workflow:', error);
        res.status(500).json({ error: 'Internal server error' });
      }
      break;

    case 'DELETE':
      try {
        const result = await collection.deleteOne({ _id });
        if (result.deletedCount === 0) {
          return res.status(404).json({ error: 'Workflow not found' });
        }
        res.status(204).end();
      } catch (error) {
        console.error('Error deleting workflow:', error);
        res.status(500).json({ error: 'Internal server error' });
      }
      break;

    default:
      res.status(405).json({ error: 'Method not allowed' });
  }
}
