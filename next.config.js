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
    domains: ['johnallens.com'],
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
            value: "default-src 'self' https://johnallens.com; script-src 'self' 'unsafe-eval' 'unsafe-inline' https://johnallens.com; style-src 'self' 'unsafe-inline' https://johnallens.com; img-src 'self' data: https: https://johnallens.com; connect-src 'self' https://johnallens.com; frame-src https://johnallens.com",
          },
        ],
      },
    ]
  },
}

module.exports = nextConfig
