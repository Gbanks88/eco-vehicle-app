import { useState, useEffect } from 'react';
import { useRouter } from 'next/router';
import Image from 'next/image';
import { useSession } from 'next-auth/react';
import Head from 'next/head';

export default function ProductDetails() {
  const router = useRouter();
  const { id } = router.query;
  const { data: session } = useSession();
  const [product, setProduct] = useState(null);
  const [recommendations, setRecommendations] = useState([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    if (!id) return;

    const fetchData = async () => {
      try {
        const [productRes, recommendationsRes] = await Promise.all([
          fetch(`/api/products/${id}`),
          fetch(`/api/recommendations/products?productId=${id}`)
        ]);

        if (!productRes.ok) throw new Error('Failed to fetch product');
        
        const productData = await productRes.json();
        setProduct(productData);
        
        if (recommendationsRes.ok) {
          const recommendationsData = await recommendationsRes.json();
          setRecommendations(recommendationsData);
        }

        // Track product view
        await fetch('/api/analytics/track', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            eventType: 'product_view',
            eventData: { productId: id },
            url: window.location.href
          })
        });
      } catch (err) {
        setError(err.message);
      } finally {
        setIsLoading(false);
      }
    };

    fetchData();
  }, [id]);

  if (isLoading) return <div className="text-center py-10">Loading...</div>;
  if (error) return <div className="text-center py-10 text-red-600">{error}</div>;
  if (!product) return <div className="text-center py-10">Product not found</div>;

  return (
    <>
      <Head>
        <title>{product.name} | Eco Vehicle</title>
        <meta name="description" content={product.description} />
      </Head>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
          {/* Product Image */}
          <div className="relative h-96 rounded-lg overflow-hidden">
            <Image
              src={product.imageUrl || '/placeholder-vehicle.jpg'}
              alt={product.name}
              layout="fill"
              objectFit="cover"
            />
          </div>

          {/* Product Info */}
          <div>
            <h1 className="text-3xl font-bold text-gray-900">{product.name}</h1>
            <div className="mt-3 flex items-center">
              <div className="flex text-yellow-400">
                {[...Array(5)].map((_, i) => (
                  <svg
                    key={i}
                    className={`h-5 w-5 ${
                      i < Math.floor(product.rating) ? 'fill-current' : 'fill-gray-300'
                    }`}
                    viewBox="0 0 20 20"
                  >
                    <path d="M10 15l-5.878 3.09 1.123-6.545L.489 6.91l6.572-.955L10 0l2.939 5.955 6.572.955-4.756 4.635 1.123 6.545z" />
                  </svg>
                ))}
              </div>
              <span className="ml-2 text-gray-600">
                ({product.reviewCount || 0} reviews)
              </span>
            </div>

            <div className="mt-4">
              <h2 className="sr-only">Product information</h2>
              <p className="text-3xl text-gray-900">${product.price.toLocaleString()}</p>
            </div>

            <div className="mt-6">
              <h3 className="text-lg font-medium text-gray-900">Description</h3>
              <div className="mt-2 prose prose-sm text-gray-500">
                {product.description}
              </div>
            </div>

            {/* Specifications */}
            <div className="mt-8">
              <h3 className="text-lg font-medium text-gray-900">Specifications</h3>
              <div className="mt-4 border-t border-gray-200">
                <dl className="divide-y divide-gray-200">
                  {Object.entries(product.specifications || {}).map(([key, value]) => (
                    <div key={key} className="py-3 flex justify-between">
                      <dt className="text-sm font-medium text-gray-500">{key}</dt>
                      <dd className="text-sm text-gray-900">{value}</dd>
                    </div>
                  ))}
                </dl>
              </div>
            </div>

            {/* Add to Cart Button */}
            {session && (
              <div className="mt-8">
                <button
                  type="button"
                  className="w-full bg-blue-600 text-white px-6 py-3 rounded-md hover:bg-blue-700 transition-colors"
                >
                  Add to Cart
                </button>
              </div>
            )}
          </div>
        </div>

        {/* Recommendations */}
        {recommendations.length > 0 && (
          <div className="mt-16">
            <h2 className="text-2xl font-bold text-gray-900">Similar Vehicles</h2>
            <div className="mt-6 grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">
              {recommendations.map((rec) => (
                <ProductCard key={rec._id} product={rec} />
              ))}
            </div>
          </div>
        )}
      </div>
    </>
  );
}
