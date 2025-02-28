import { useState } from 'react';
import Head from 'next/head';
import Link from 'next/link';
import Layout from '../../components/Layout';

// Sample blog posts - in production, these would come from a CMS or API
const BLOG_POSTS = [
  {
    id: 1,
    title: 'The Future of Eco-Friendly Vehicles',
    slug: 'future-of-eco-friendly-vehicles',
    excerpt: 'Exploring the latest trends and innovations in sustainable transportation.',
    date: '2025-02-28',
    author: 'John Allen',
    category: 'Technology',
    readTime: '5 min read',
  },
  {
    id: 2,
    title: 'Top 10 Electric Vehicle Maintenance Tips',
    slug: 'ev-maintenance-tips',
    excerpt: 'Essential maintenance tips to keep your electric vehicle running efficiently.',
    date: '2025-02-25',
    author: 'Sarah Chen',
    category: 'Maintenance',
    readTime: '8 min read',
  },
  // Add more sample posts as needed
];

export default function Blog() {
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedCategory, setSelectedCategory] = useState('');

  const categories = [...new Set(BLOG_POSTS.map(post => post.category))];

  const filteredPosts = BLOG_POSTS.filter(post => {
    const matchesSearch = post.title.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         post.excerpt.toLowerCase().includes(searchTerm.toLowerCase());
    const matchesCategory = !selectedCategory || post.category === selectedCategory;
    return matchesSearch && matchesCategory;
  });

  return (
    <Layout>
      <Head>
        <title>Blog - Eco Vehicle Project</title>
        <meta name="description" content="Latest insights and updates about eco-friendly vehicles, sustainable transportation, and green technology." />
      </Head>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        <div className="max-w-3xl mx-auto">
          <h1 className="text-4xl font-bold text-gray-900 mb-8">Blog</h1>

          <div className="mb-8 flex flex-col sm:flex-row gap-4">
            <div className="flex-1">
              <input
                type="text"
                placeholder="Search articles..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="w-full px-4 py-2 border border-gray-300 rounded-md focus:ring-green-500 focus:border-green-500"
              />
            </div>
            <div>
              <select
                value={selectedCategory}
                onChange={(e) => setSelectedCategory(e.target.value)}
                className="w-full sm:w-auto px-4 py-2 border border-gray-300 rounded-md focus:ring-green-500 focus:border-green-500"
              >
                <option value="">All Categories</option>
                {categories.map(category => (
                  <option key={category} value={category}>{category}</option>
                ))}
              </select>
            </div>
          </div>

          {filteredPosts.length === 0 ? (
            <div className="text-center py-12">
              <p className="text-gray-500">No articles found matching your criteria.</p>
            </div>
          ) : (
            <div className="space-y-8">
              {filteredPosts.map(post => (
                <article key={post.id} className="bg-white rounded-lg shadow-md overflow-hidden">
                  <Link href={`/blog/${post.slug}`}>
                    <div className="p-6 cursor-pointer hover:bg-gray-50 transition duration-150">
                      <div className="flex items-center text-sm text-gray-500 mb-2">
                        <span className="bg-green-100 text-green-800 px-2 py-1 rounded-full text-xs font-medium">
                          {post.category}
                        </span>
                        <span className="mx-2">•</span>
                        <time dateTime={post.date}>{new Date(post.date).toLocaleDateString()}</time>
                        <span className="mx-2">•</span>
                        <span>{post.readTime}</span>
                      </div>
                      <h2 className="text-xl font-semibold text-gray-900 mb-2">{post.title}</h2>
                      <p className="text-gray-600 mb-4">{post.excerpt}</p>
                      <div className="flex items-center">
                        <div className="text-sm">
                          <p className="text-gray-900 font-medium">By {post.author}</p>
                        </div>
                      </div>
                    </div>
                  </Link>
                </article>
              ))}
            </div>
          )}
        </div>
      </div>
    </Layout>
  );
}
