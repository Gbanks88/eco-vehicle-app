import { connectToDatabase } from '../../../lib/mongodb';
import { getSession } from 'next-auth/react';

export default async function handler(req, res) {
  try {
    const { db } = await connectToDatabase();

    switch (req.method) {
      case 'GET':
        const { game, limit = 10 } = req.query;
        
        const scores = await db.collection('scores')
          .find({ game })
          .sort({ score: -1 })
          .limit(parseInt(limit))
          .toArray();
        
        res.status(200).json(scores);
        break;

      case 'POST':
        const session = await getSession({ req });
        if (!session) {
          res.status(401).json({ message: 'Not authenticated!' });
          return;
        }

        const { score, gameType } = req.body;
        
        const result = await db.collection('scores').insertOne({
          game: gameType,
          score: parseInt(score),
          userId: session.user.id,
          userName: session.user.name,
          createdAt: new Date(),
        });

        res.status(201).json(result);
        break;

      default:
        res.setHeader('Allow', ['GET', 'POST']);
        res.status(405).end(`Method ${req.method} Not Allowed`);
    }
  } catch (error) {
    console.error('API Error:', error);
    res.status(500).json({ message: 'Internal Server Error' });
  }
}
