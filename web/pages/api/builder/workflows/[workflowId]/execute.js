import { ObjectId } from 'mongodb';
import { connectToDatabase } from '../../../../../lib/mongodb';
import { ApplicationBuilder } from '../../../../../lib/builder';

export default async function handler(req, res) {
  if (req.method !== 'POST') {
    return res.status(405).json({ error: 'Method not allowed' });
  }

  const { workflowId } = req.query;
  const { context = {} } = req.body;

  if (!ObjectId.isValid(workflowId)) {
    return res.status(400).json({ error: 'Invalid workflow ID' });
  }

  try {
    const { db } = await connectToDatabase();
    const workflow = await db.collection('workflows')
      .findOne({ _id: new ObjectId(workflowId) });

    if (!workflow) {
      return res.status(404).json({ error: 'Workflow not found' });
    }

    const builder = new ApplicationBuilder();
    await builder.initialize();

    const execution = {
      workflowId,
      status: 'running',
      startTime: new Date(),
      context
    };

    // Log execution start
    const result = await db.collection('workflow_executions')
      .insertOne(execution);

    try {
      // Execute workflow
      const executionResult = await builder.executeWorkflow(workflow.name, workflow.steps);

      // Update execution record with success
      await db.collection('workflow_executions').updateOne(
        { _id: result.insertedId },
        {
          $set: {
            status: 'completed',
            endTime: new Date(),
            duration: Date.now() - execution.startTime,
            result: executionResult
          }
        }
      );

      // Update workflow metrics
      await db.collection('workflows').updateOne(
        { _id: new ObjectId(workflowId) },
        {
          $inc: { 'metrics.executions': 1 },
          $set: {
            'metrics.avgDuration': (
              (workflow.metrics.avgDuration * workflow.metrics.executions +
                Date.now() - execution.startTime) /
              (workflow.metrics.executions + 1)
            )
          }
        }
      );

      res.status(200).json({
        id: result.insertedId,
        workflowId,
        status: 'completed',
        startTime: execution.startTime,
        endTime: new Date(),
        duration: Date.now() - execution.startTime,
        result: executionResult
      });
    } catch (error) {
      // Update execution record with failure
      await db.collection('workflow_executions').updateOne(
        { _id: result.insertedId },
        {
          $set: {
            status: 'failed',
            endTime: new Date(),
            duration: Date.now() - execution.startTime,
            error: error.message
          }
        }
      );

      // Update workflow metrics
      await db.collection('workflows').updateOne(
        { _id: new ObjectId(workflowId) },
        {
          $inc: {
            'metrics.executions': 1,
            'metrics.failures': 1
          }
        }
      );

      throw error;
    }
  } catch (error) {
    console.error('Error executing workflow:', error);
    res.status(500).json({
      error: 'Workflow execution failed',
      message: error.message
    });
  }
}
