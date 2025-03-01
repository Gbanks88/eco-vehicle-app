/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  async rewrites() {
    return [
      {
        source: '/johnallens/:path*',
        destination: 'https://johnallens.com/:path*',
      },
      {
        source: '/api/johnallens/:path*',
        destination: 'https://johnallens.com/api/:path*',
      },
    ]
  },
  images: {
    domains: ['johnallens.com', 'm.media-amazon.com', 'images.unsplash.com'],
  },
  async headers() {
    return [
      {
        source: '/:path*',
        headers: [
          {
            key: 'X-Frame-Options',
            value: 'SAMEORIGIN',
          },
          {
            key: 'Content-Security-Policy',
            value: "default-src 'self' https://johnallens.com https://www.amazon.com https://images.unsplash.com; script-src 'self' 'unsafe-eval' 'unsafe-inline' https://johnallens.com https://www.amazon.com; style-src 'self' 'unsafe-inline' https://johnallens.com; img-src 'self' data: https: https://johnallens.com https://m.media-amazon.com https://images.unsplash.com; connect-src 'self' https://johnallens.com https://www.amazon.com https://images.unsplash.com; frame-src https://johnallens.com https://www.amazon.com",
          },
        ],
      },
    ]
  },
}

export default nextConfig
