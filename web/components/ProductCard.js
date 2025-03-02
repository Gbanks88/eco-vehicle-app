import Image from 'next/image';
import Link from 'next/link';
import { useSession } from 'next-auth/react';
import { useState } from 'react';

export default function ProductCard({ product }) {
  const { data: session } = useSession();
  const [isLoading, setIsLoading] = useState(false);

  const trackProductView = async () => {
    try {
      await fetch('/api/analytics/track', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          eventType: 'product_view',
          eventData: { productId: product._id },
          url: window.location.href
        })
      });
    } catch (error) {
      console.error('Failed to track product view:', error);
    }
  };

  return (
    <div className="bg-white rounded-lg shadow-md overflow-hidden transition-transform hover:scale-105">
      <Link href={`/products/${product._id}`} onClick={trackProductView}>
        <div className="relative h-48 w-full">
          <Image
            src={product.imageUrl || '/placeholder-vehicle.jpg'}
            alt={product.name}
            layout="fill"
            objectFit="cover"
          />
        </div>
      </Link>
      <div className="p-4">
        <h3 className="text-lg font-semibold text-gray-800">{product.name}</h3>
        <p className="text-sm text-gray-600 mt-1">{product.description}</p>
        <div className="mt-4 flex justify-between items-center">
          <span className="text-xl font-bold text-green-600">
            ${product.price.toLocaleString()}
          </span>
          {session && (
            <button
              onClick={() => {/* Add to cart logic */}}
              className="bg-blue-600 text-white px-4 py-2 rounded-md hover:bg-blue-700 transition-colors"
              disabled={isLoading}
            >
              {isLoading ? 'Adding...' : 'Add to Cart'}
            </button>
          )}
        </div>
        <div className="mt-2 flex items-center">
          <div className="flex text-yellow-400">
            {[...Array(5)].map((_, i) => (
              <svg
                key={i}
                className={`h-4 w-4 ${
                  i < Math.floor(product.rating) ? 'fill-current' : 'fill-gray-300'
                }`}
                viewBox="0 0 20 20"
              >
                <path d="M10 15l-5.878 3.09 1.123-6.545L.489 6.91l6.572-.955L10 0l2.939 5.955 6.572.955-4.756 4.635 1.123 6.545z" />
              </svg>
            ))}
          </div>
          <span className="ml-2 text-sm text-gray-600">
            ({product.reviewCount || 0} reviews)
          </span>
        </div>
      </div>
    </div>
  );
}
