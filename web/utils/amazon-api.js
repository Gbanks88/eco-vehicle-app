import crypto from 'crypto';

const AMAZON_ACCESS_KEY = process.env.AMAZON_ACCESS_KEY;
const AMAZON_SECRET_KEY = process.env.AMAZON_SECRET_KEY;
const AMAZON_PARTNER_TAG = process.env.AMAZON_PARTNER_TAG;
const AMAZON_REGION = process.env.AMAZON_REGION || 'us-west-2';

const API_VERSION = '2013-08-01';
const BASE_URL = `https://webservices.amazon.${AMAZON_REGION}/onca/xml`;

function generateSignature(params) {
  const sortedParams = Object.keys(params)
    .sort()
    .reduce((acc, key) => {
      acc[key] = params[key];
      return acc;
    }, {});

  const canonicalQuery = Object.keys(sortedParams)
    .map(key => `${encodeURIComponent(key)}=${encodeURIComponent(sortedParams[key])}`)
    .join('&');

  const stringToSign = [
    'GET',
    `webservices.amazon.${AMAZON_REGION}`,
    '/onca/xml',
    canonicalQuery
  ].join('\n');

  return crypto
    .createHmac('sha256', AMAZON_SECRET_KEY)
    .update(stringToSign)
    .digest('base64');
}

export async function searchProducts(query, options = {}) {
  const {
    category = 'All',
    minPrice,
    maxPrice,
    sortBy = 'Relevance',
    page = 1
  } = options;

  const timestamp = new Date().toISOString();
  const params = {
    AWSAccessKeyId: AMAZON_ACCESS_KEY,
    AssociateTag: AMAZON_PARTNER_TAG,
    Keywords: query,
    Operation: 'ItemSearch',
    ResponseGroup: 'Images,ItemAttributes,Offers',
    SearchIndex: category,
    Service: 'AWSECommerceService',
    Sort: sortBy,
    Timestamp: timestamp,
    Version: API_VERSION,
    ItemPage: page
  };

  if (minPrice) params.MinimumPrice = minPrice;
  if (maxPrice) params.MaximumPrice = maxPrice;

  const signature = generateSignature(params);
  params.Signature = signature;

  const queryString = Object.keys(params)
    .map(key => `${encodeURIComponent(key)}=${encodeURIComponent(params[key])}`)
    .join('&');

  const url = `${BASE_URL}?${queryString}`;

  try {
    const response = await fetch(url);
    const data = await response.text();
    
    // Convert XML to JSON
    const parser = new DOMParser();
    const xmlDoc = parser.parseFromString(data, 'text/xml');
    
    // Extract items
    const items = Array.from(xmlDoc.getElementsByTagName('Item')).map(item => ({
      asin: item.getElementsByTagName('ASIN')[0]?.textContent,
      title: item.getElementsByTagName('Title')[0]?.textContent,
      price: item.getElementsByTagName('FormattedPrice')[0]?.textContent,
      imageUrl: item.getElementsByTagName('LargeImage')[0]?.getElementsByTagName('URL')[0]?.textContent,
      detailPageUrl: item.getElementsByTagName('DetailPageURL')[0]?.textContent,
      rating: item.getElementsByTagName('AverageRating')[0]?.textContent,
      reviewCount: item.getElementsByTagName('TotalReviews')[0]?.textContent,
      features: Array.from(item.getElementsByTagName('Feature')).map(feature => feature.textContent)
    }));

    return {
      items,
      totalPages: parseInt(xmlDoc.getElementsByTagName('TotalPages')[0]?.textContent || '1'),
      currentPage: page
    };
  } catch (error) {
    console.error('Amazon API error:', error);
    throw new Error('Failed to fetch products from Amazon');
  }
}

export function generateAmazonUrl(asin) {
  return `https://www.amazon.com/dp/${asin}?tag=${AMAZON_PARTNER_TAG}`;
}
