import { useRouter } from 'next/router';
import Head from 'next/head';
import Link from 'next/link';
import Layout from '../../components/Layout';

// Sample blog post data - in production, this would come from a CMS or API
const BLOG_POSTS = {
  'future-of-eco-friendly-vehicles': {
    title: 'The Future of Eco-Friendly Vehicles',
    date: '2025-02-28',
    author: 'John Allen',
    category: 'Technology',
    readTime: '5 min read',
    content: `
      <h2>Introduction</h2>
      <p>The automotive industry is undergoing a revolutionary transformation as we move towards more sustainable transportation solutions. In this article, we'll explore the latest trends and innovations in eco-friendly vehicles.</p>

      <h2>Electric Vehicles: The New Standard</h2>
      <p>Electric vehicles (EVs) have come a long way since their inception. With improved battery technology, extended range, and faster charging capabilities, EVs are becoming increasingly practical for everyday use.</p>

      <h2>Hydrogen Fuel Cell Technology</h2>
      <p>While EVs dominate the current eco-friendly vehicle market, hydrogen fuel cell technology presents another promising avenue for sustainable transportation. These vehicles combine the benefits of electric motors with quick refueling times.</p>

      <h2>The Role of Autonomous Technology</h2>
      <p>Self-driving capabilities are becoming increasingly integrated with eco-friendly vehicles, promising to optimize energy usage and reduce environmental impact through efficient routing and driving patterns.</p>

      <h2>Conclusion</h2>
      <p>The future of eco-friendly vehicles is bright, with multiple technologies competing and complementing each other to create a more sustainable transportation ecosystem.</p>
    `,
  },
  'ev-maintenance-tips': {
    title: 'Top 10 Electric Vehicle Maintenance Tips',
    date: '2025-02-25',
    author: 'Sarah Chen',
    category: 'Maintenance',
    readTime: '8 min read',
    content: `
      <h2>Introduction</h2>
      <p>Maintaining your electric vehicle properly is key to ensuring its longevity and optimal performance. Here are our top 10 maintenance tips for EV owners.</p>

      <h2>1. Regular Battery Care</h2>
      <p>Your EV's battery is its most crucial component. Learn how to maintain optimal charge levels and avoid extreme temperatures to maximize battery life.</p>

      <h2>2. Tire Maintenance</h2>
      <p>Due to the instant torque of electric motors, EV tires may wear differently than those on conventional vehicles. Regular rotation and proper inflation are essential.</p>

      <h2>3. Brake System Care</h2>
      <p>While regenerative braking reduces wear on brake pads, it's still important to inspect and maintain your EV's brake system regularly.</p>

      <h2>Conclusion</h2>
      <p>Following these maintenance tips will help ensure your electric vehicle provides reliable, efficient transportation for years to come.</p>
    `,
  },
};

export default function BlogPost() {
  const router = useRouter();
  const { slug } = router.query;
  const post = BLOG_POSTS[slug];

  if (router.isFallback || !post) {
    return (
      <Layout>
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
          <div className="max-w-3xl mx-auto">
            <p>Loading...</p>
          </div>
        </div>
      </Layout>
    );
  }

  return (
    <Layout>
      <Head>
        <title>{post.title} - Eco Vehicle Project</title>
        <meta name="description" content={post.content.substring(0, 160)} />
      </Head>

      <article className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        <div className="max-w-3xl mx-auto">
          <Link href="/blog">
            <div className="text-green-600 hover:text-green-700 mb-4 inline-flex items-center">
              <svg className="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 19l-7-7m0 0l7-7m-7 7h18" />
              </svg>
              Back to Blog
            </div>
          </Link>

          <header className="mb-8">
            <div className="flex items-center text-sm text-gray-500 mb-2">
              <span className="bg-green-100 text-green-800 px-2 py-1 rounded-full text-xs font-medium">
                {post.category}
              </span>
              <span className="mx-2">•</span>
              <time dateTime={post.date}>{new Date(post.date).toLocaleDateString()}</time>
              <span className="mx-2">•</span>
              <span>{post.readTime}</span>
            </div>
            <h1 className="text-4xl font-bold text-gray-900 mb-4">{post.title}</h1>
            <div className="flex items-center">
              <div className="text-sm">
                <p className="text-gray-900 font-medium">By {post.author}</p>
              </div>
            </div>
          </header>

          <div 
            className="prose prose-green max-w-none"
            dangerouslySetInnerHTML={{ __html: post.content }}
          />

          <div className="mt-8 pt-8 border-t border-gray-200">
            <div className="flex justify-between items-center">
              <div className="flex items-center space-x-4">
                <button className="text-gray-500 hover:text-gray-600">
                  <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4.318 6.318a4.5 4.5 0 000 6.364L12 20.364l7.682-7.682a4.5 4.5 0 00-6.364-6.364L12 7.636l-1.318-1.318a4.5 4.5 0 00-6.364 0z" />
                  </svg>
                </button>
                <button className="text-gray-500 hover:text-gray-600">
                  <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8.684 13.342C8.886 12.938 9 12.482 9 12c0-.482-.114-.938-.316-1.342m0 2.684a3 3 0 110-2.684m0 2.684l6.632 3.316m-6.632-6l6.632-3.316m0 0a3 3 0 105.367-2.684 3 3 0 00-5.367 2.684zm0 9.316a3 3 0 105.368 2.684 3 3 0 00-5.368-2.684z" />
                  </svg>
                </button>
              </div>
              <Link href="/blog">
                <div className="text-green-600 hover:text-green-700">
                  More Articles
                </div>
              </Link>
            </div>
          </div>
        </div>
      </article>
    </Layout>
  );
}

// In production, this would fetch data from a CMS or API
export async function getStaticPaths() {
  const paths = Object.keys(BLOG_POSTS).map(slug => ({
    params: { slug },
  }));

  return {
    paths,
    fallback: false,
  };
}

export async function getStaticProps({ params }) {
  return {
    props: {}, // The post data is already available in the component
  };
}
