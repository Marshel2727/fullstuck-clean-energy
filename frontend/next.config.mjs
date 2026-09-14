/** @type {import('next').NextConfig} */
const nextConfig = {
  output: 'standalone',
  reactStrictMode: true,
  async rewrites() {
    return [{
      source: '/api/v1/:path*',
      destination: (process.env.BACKEND_INTERNAL_URL || 'http://127.0.0.1:8000') + '/api/v1/:path*',
    }];
  },
  images: {
    unoptimized: true,
  },
};

export default nextConfig;
