import dbConnect from '../lib/mongodb';
import User from '../models/User';

async function createAdmin() {
  try {
    await dbConnect();
    console.log('Connected to MongoDB...');

    const adminEmail = process.env.ADMIN_EMAIL;
    const adminPassword = process.env.ADMIN_PASSWORD;
    const adminName = process.env.ADMIN_NAME;

    if (!adminEmail || !adminPassword || !adminName) {
      console.error('Please provide ADMIN_EMAIL, ADMIN_PASSWORD, and ADMIN_NAME in environment variables');
      process.exit(1);
    }

    // Check if admin already exists
    const existingAdmin = await User.findOne({ email: adminEmail });
    if (existingAdmin) {
      console.log('Admin user already exists');
      process.exit(0);
    }

    // Create admin user
    const admin = await User.create({
      email: adminEmail,
      password: adminPassword,
      name: adminName,
      role: 'admin'
    });

    console.log('Admin user created successfully:', admin.email);
    process.exit(0);
  } catch (error) {
    console.error('Error creating admin user:', error);
    process.exit(1);
  }
}

createAdmin();
