import Link from 'next/link';
import { useTheme } from './CustomTheme';

export default function Custom404() {
  const { theme } = useTheme();

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50">
      <div className="max-w-xl w-full p-8 text-center">
        <div className="mb-8">
          <h1 className="text-6xl font-bold text-gray-800 mb-4">404</h1>
          <p className="text-xl text-gray-600 mb-8">
            Oops! The page you're looking for doesn't exist.
          </p>
          <div className="space-y-4">
            <Link
              href="/"
              className={`inline-block px-6 py-3 rounded-lg transition-colors
                ${theme.mode === 'dark'
                  ? 'bg-blue-600 text-white hover:bg-blue-700'
                  : 'bg-blue-500 text-white hover:bg-blue-600'
                }`}
            >
              Return Home
            </Link>
            <button
              onClick={() => window.history.back()}
              className={`block w-full px-6 py-3 rounded-lg transition-colors
                ${theme.mode === 'dark'
                  ? 'bg-gray-700 text-white hover:bg-gray-800'
                  : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                }`}
            >
              Go Back
            </button>
          </div>
        </div>

        {/* Quick Links */}
        <div className="border-t border-gray-200 pt-8">
          <h2 className="text-lg font-semibold text-gray-700 mb-4">
            Popular Pages
          </h2>
          <div className="grid grid-cols-2 gap-4">
            <Link
              href="/products"
              className={`p-4 rounded-lg transition-colors
                ${theme.mode === 'dark'
                  ? 'bg-gray-800 hover:bg-gray-700'
                  : 'bg-white hover:bg-gray-50'
                } shadow-sm`}
            >
              <div className="text-lg font-medium mb-1">Products</div>
              <div className="text-sm text-gray-500">
                Browse our eco-friendly vehicles
              </div>
            </Link>
            <Link
              href="/contact"
              className={`p-4 rounded-lg transition-colors
                ${theme.mode === 'dark'
                  ? 'bg-gray-800 hover:bg-gray-700'
                  : 'bg-white hover:bg-gray-50'
                } shadow-sm`}
            >
              <div className="text-lg font-medium mb-1">Contact</div>
              <div className="text-sm text-gray-500">
                Get in touch with our team
              </div>
            </Link>
            <Link
              href="/about"
              className={`p-4 rounded-lg transition-colors
                ${theme.mode === 'dark'
                  ? 'bg-gray-800 hover:bg-gray-700'
                  : 'bg-white hover:bg-gray-50'
                } shadow-sm`}
            >
              <div className="text-lg font-medium mb-1">About</div>
              <div className="text-sm text-gray-500">
                Learn about our mission
              </div>
            </Link>
            <Link
              href="/support"
              className={`p-4 rounded-lg transition-colors
                ${theme.mode === 'dark'
                  ? 'bg-gray-800 hover:bg-gray-700'
                  : 'bg-white hover:bg-gray-50'
                } shadow-sm`}
            >
              <div className="text-lg font-medium mb-1">Support</div>
              <div className="text-sm text-gray-500">
                Get help and support
              </div>
            </Link>
          </div>
        </div>
      </div>
    </div>
  );
}
