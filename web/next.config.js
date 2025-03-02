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
      {
        source: '/cg4f/:path*',
        destination: 'https://cg4f.online/:path*',
      },
      {
        source: '/api/cg4f/:path*',
        destination: 'https://cg4f.online/api/:path*',
      },
    ]
  },
  images: {
    domains: ['johnallens.com', 'cg4f.online', 'm.media-amazon.com', 'images.unsplash.com'],
  },
  async headers() {
    return [
      {
        source: '/:path*',
        headers: [
          {
            key: 'Strict-Transport-Security',
            value: 'max-age=31536000; includeSubDomains; preload',
          },
          {
            key: 'X-Frame-Options',
            value: 'DENY',
          },
          {
            key: 'X-Content-Type-Options',
            value: 'nosniff',
          },
          {
            key: 'X-XSS-Protection',
            value: '1; mode=block',
          },
          {
            key: 'Referrer-Policy',
            value: 'strict-origin-when-cross-origin',
          },
          {
            key: 'Permissions-Policy',
            value: 'accelerometer=(), ambient-light-sensor=(), autoplay=(), battery=(), camera=(), cross-origin-isolated=(), display-capture=(), document-domain=(), encrypted-media=(), execution-while-not-rendered=(), execution-while-out-of-viewport=(), fullscreen=(self), geolocation=(), gyroscope=(), keyboard-map=(), magnetometer=(), microphone=(), midi=(), navigation-override=(), payment=(), picture-in-picture=(), publickey-credentials-get=(), screen-wake-lock=(), sync-xhr=(), usb=(), web-share=(), xr-spatial-tracking=()',
          },
          {
            key: 'Content-Security-Policy',
            value: "default-src 'self' https://*.johnallens.com https://*.cg4f.online https://*.netlify.app https://www.amazon.com https://images.unsplash.com; script-src 'self' 'unsafe-eval' 'unsafe-inline' https://*.johnallens.com https://*.cg4f.online https://*.netlify.app https://www.amazon.com https://sketchfab.com https://youtube.com; style-src 'self' 'unsafe-inline' https://fonts.googleapis.com https://*.johnallens.com https://*.cg4f.online; font-src 'self' https://fonts.gstatic.com; img-src 'self' data: https: https://*.johnallens.com https://*.cg4f.online https://m.media-amazon.com https://images.unsplash.com; media-src 'self' https:; connect-src 'self' https://*.johnallens.com https://*.cg4f.online https://*.netlify.app https://www.amazon.com https://images.unsplash.com; frame-src 'self' https://*.johnallens.com https://*.cg4f.online https://www.amazon.com https://sketchfab.com https://youtube.com; worker-src 'self' blob:; manifest-src 'self'; base-uri 'self'; form-action 'self' https://*.johnallens.com https://*.cg4f.online; upgrade-insecure-requests;",
          },
          {
            key: 'Cross-Origin-Embedder-Policy',
            value: 'require-corp',
          },
          {
            key: 'Cross-Origin-Opener-Policy',
            value: 'same-origin',
          },
          {
            key: 'Cross-Origin-Resource-Policy',
            value: 'same-origin',
          },
        ],
      },
    ]
  },
}

module.exports = nextConfig
