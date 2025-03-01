import { config } from 'dotenv';
import { resolve } from 'path';
import { fileURLToPath } from 'url';

const __dirname = fileURLToPath(new URL('.', import.meta.url));
config();

console.log('MONGODB_URI:', process.env.MONGODB_URI);
console.log('NEXTAUTH_URL:', process.env.NEXTAUTH_URL);
console.log('NEXTAUTH_SECRET:', process.env.NEXTAUTH_SECRET);
console.log('ADMIN_EMAIL:', process.env.ADMIN_EMAIL);
