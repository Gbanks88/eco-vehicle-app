import { Html, Head, Main, NextScript } from 'next/document';

export default function Document() {
  return (
      <Html lang="en">
        <Head>
          {/* Netlify Analytics - No cookie tracking */}
          <script async src="https://cdn.jsdelivr.net/npm/netlify-cms@^2.0.0/dist/netlify-cms.js"></script>

          {/* Favicon */}
          <link rel="apple-touch-icon" sizes="180x180" href="/apple-touch-icon.png" />
          <link rel="icon" type="image/png" sizes="32x32" href="/favicon-32x32.png" />
          <link rel="icon" type="image/png" sizes="16x16" href="/favicon-16x16.png" />
          <link rel="manifest" href="/site.webmanifest" />
          <link rel="mask-icon" href="/safari-pinned-tab.svg" color="#10B981" />
          <meta name="msapplication-TileColor" content="#10B981" />
          <meta name="theme-color" content="#ffffff" />

          {/* Open Graph */}
          <meta property="og:type" content="website" />
          <meta property="og:site_name" content="Eco Vehicle Project" />
          <meta property="og:image" content="/og-image.jpg" />
          <meta property="twitter:card" content="summary_large_image" />
        </Head>
        <body>
          <Main />
          <NextScript />
        </body>
      </Html>
    );
}
