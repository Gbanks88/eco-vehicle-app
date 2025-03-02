const ASSOCIATE_ID = 'tech4fun0d-20';

export const generateAmazonAffiliateLink = (asin, customUrl = '') => {
  if (customUrl) {
    return `https://www.amazon.com/${customUrl}/ref=as_li_tl?tag=${ASSOCIATE_ID}`;
  }
  return `https://www.amazon.com/dp/${asin}?tag=${ASSOCIATE_ID}`;
};

export const generateSearchLink = (searchTerm) => {
  const encodedSearch = encodeURIComponent(searchTerm);
  return `https://www.amazon.com/s?k=${encodedSearch}&tag=${ASSOCIATE_ID}`;
};

export const generateWidgetLink = (widgetType, category) => {
  return `https://ws-na.amazon-adsystem.com/widgets/${widgetType}?ServiceVersion=20070822&OneJS=1&Operation=GetAdHtml&MarketPlace=US&source=ss&ref=as_ss_li_til&ad_type=product_link&tracking_id=${ASSOCIATE_ID}&marketplace=amazon&region=US&placement=${category}&asins=${category}&linkId=${Date.now()}&show_border=true&link_opens_in_new_window=true`;
};
