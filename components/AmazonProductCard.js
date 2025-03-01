import Image from 'next/image';
import { generateAmazonAffiliateLink } from '../utils/amazon';

const AmazonProductCard = ({ product }) => {
  const {
    title,
    asin,
    imageUrl,
    price,
    rating,
    description,
    prime = false,
  } = product;

  return (
    <div className="bg-white rounded-lg shadow-md overflow-hidden hover:shadow-lg transition-shadow duration-300">
      <a
        href={generateAmazonAffiliateLink(asin)}
        target="_blank"
        rel="noopener noreferrer sponsored"
        className="block"
      >
        <div className="relative h-48 w-full">
          <Image
            src={imageUrl}
            alt={title}
            width={300}
            height={300}
            style={{
              objectFit: 'contain',
              width: '100%',
              height: '100%',
            }}
            className="p-4"
          />
        </div>
        <div className="p-4">
          <h3 className="text-lg font-semibold text-gray-800 line-clamp-2">
            {title}
          </h3>
          
          <div className="flex items-center mt-2">
            <div className="flex items-center">
              {[...Array(5)].map((_, i) => (
                <svg
                  key={i}
                  className={`w-4 h-4 ${
                    i < rating ? 'text-yellow-400' : 'text-gray-300'
                  }`}
                  fill="currentColor"
                  viewBox="0 0 20 20"
                >
                  <path d="M9.049 2.927c.3-.921 1.603-.921 1.902 0l1.07 3.292a1 1 0 00.95.69h3.462c.969 0 1.371 1.24.588 1.81l-2.8 2.034a1 1 0 00-.364 1.118l1.07 3.292c.3.921-.755 1.688-1.54 1.118l-2.8-2.034a1 1 0 00-1.175 0l-2.8 2.034c-.784.57-1.838-.197-1.539-1.118l1.07-3.292a1 1 0 00-.364-1.118L2.98 8.72c-.783-.57-.38-1.81.588-1.81h3.461a1 1 0 00.951-.69l1.07-3.292z" />
                </svg>
              ))}
            </div>
          </div>

          <p className="mt-2 text-sm text-gray-600 line-clamp-2">
            {description}
          </p>

          <div className="mt-4 flex items-center justify-between">
            <span className="text-xl font-bold text-gray-900">
              ${price}
            </span>
            {prime && (
              <span className="text-sm text-blue-600 font-semibold">
                Prime
              </span>
            )}
          </div>
        </div>
      </a>
    </div>
  );
};

export default AmazonProductCard;
